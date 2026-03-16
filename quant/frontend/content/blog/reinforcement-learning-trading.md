---
title: "Reinforcement Learning for Trading: Q-Learning and DQN"
description: "Build RL trading agents with Q-Learning and Deep Q-Networks. Custom gym environments, reward shaping, and practical deployment for portfolio management."
date: "2026-03-20"
author: "Dr. James Chen"
category: "Machine Learning"
tags: ["reinforcement learning", "Q-learning", "DQN", "trading agents", "deep learning"]
keywords: ["reinforcement learning trading", "Q-learning trading", "DQN trading agent"]
---
# Reinforcement Learning for Trading: Q-Learning and DQN

Reinforcement learning (RL) frames trading as a sequential decision problem where an agent learns to maximize cumulative reward by interacting with a market environment. Unlike supervised learning, which requires labeled examples of correct actions, RL discovers optimal strategies through trial and error, making it naturally suited to the adaptive, non-stationary nature of financial markets.

This guide covers the implementation of RL trading agents from tabular Q-learning through Deep Q-Networks, with careful attention to the reward engineering and environment design that determine whether the agent learns useful behavior or merely overfits to training episodes.

## Key Takeaways

- **Reward shaping is the most critical design decision.** Naive reward functions (raw PnL) lead to degenerate policies. Risk-adjusted rewards produce better agents.
- **The environment must be realistic.** Include transaction costs, slippage, position limits, and partial fills.
- **Q-learning works for discretized state/action spaces.** DQN extends this to continuous states via function approximation.
- **Overfitting is severe in financial RL.** Train on multiple market regimes and evaluate on truly unseen periods.

## Custom Trading Environment

A well-designed environment is the foundation of any RL trading system. We build a Gymnasium-compatible environment that models realistic trading mechanics.

```python
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

class TradingEnv(gym.Env):
    """
    Custom trading environment for RL agents.

    Actions: 0 = hold, 1 = buy, 2 = sell
    State: window of price features + current position + unrealized PnL

    Realistic features:
    - Transaction costs (configurable bps)
    - Position limits (max long/short)
    - Slippage model
    """
    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        prices: np.ndarray,
        features: np.ndarray,
        window_size: int = 30,
        transaction_cost_bps: float = 10,
        max_position: int = 1,
        reward_type: str = "sharpe",
    ):
        super().__init__()

        self.prices = prices
        self.features = features
        self.window_size = window_size
        self.tc_rate = transaction_cost_bps / 10_000
        self.max_position = max_position
        self.reward_type = reward_type

        n_features = features.shape[1]

        # Action space: hold, buy, sell
        self.action_space = spaces.Discrete(3)

        # Observation space: feature window + position info
        obs_dim = n_features * window_size + 2  # +position, +unrealized_pnl
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.position = 0
        self.entry_price = 0.0
        self.total_pnl = 0.0
        self.trade_count = 0
        self.returns_history = []

        return self._get_observation(), {}

    def _get_observation(self) -> np.ndarray:
        """Construct observation from features window + position state."""
        start = self.current_step - self.window_size
        end = self.current_step

        feature_window = self.features[start:end].flatten()

        position_info = np.array([
            self.position / self.max_position,
            self._unrealized_pnl(),
        ], dtype=np.float32)

        return np.concatenate([feature_window, position_info]).astype(np.float32)

    def _unrealized_pnl(self) -> float:
        """Compute unrealized PnL for current position."""
        if self.position == 0:
            return 0.0
        current_price = self.prices[self.current_step]
        return self.position * (current_price - self.entry_price) / self.entry_price

    def step(self, action: int):
        """Execute one step in the environment."""
        current_price = self.prices[self.current_step]
        prev_price = self.prices[self.current_step - 1]

        # Execute action
        reward = 0.0
        cost = 0.0

        if action == 1 and self.position < self.max_position:
            # Buy
            cost = current_price * self.tc_rate
            self.position += 1
            self.entry_price = current_price
            self.trade_count += 1

        elif action == 2 and self.position > -self.max_position:
            # Sell
            cost = current_price * self.tc_rate
            if self.position > 0:
                # Close long: realize PnL
                realized = (current_price - self.entry_price) / self.entry_price
                self.total_pnl += realized
            self.position -= 1
            if self.position != 0:
                self.entry_price = current_price
            self.trade_count += 1

        # Step-level return (mark-to-market)
        price_return = (current_price - prev_price) / prev_price
        step_return = self.position * price_return - cost / current_price
        self.returns_history.append(step_return)

        # Compute reward
        reward = self._compute_reward(step_return)

        # Advance time
        self.current_step += 1
        done = self.current_step >= len(self.prices) - 1

        obs = self._get_observation()
        info = {
            "position": self.position,
            "total_pnl": self.total_pnl,
            "trade_count": self.trade_count,
            "step_return": step_return,
        }

        return obs, reward, done, False, info

    def _compute_reward(self, step_return: float) -> float:
        """
        Reward shaping critically affects agent behavior.
        """
        if self.reward_type == "pnl":
            return step_return * 100

        elif self.reward_type == "sharpe":
            # Rolling Sharpe-like reward
            if len(self.returns_history) < 20:
                return step_return * 100
            recent = np.array(self.returns_history[-20:])
            mean_r = np.mean(recent)
            std_r = np.std(recent)
            if std_r > 0:
                return (mean_r / std_r) * np.sqrt(252) * 0.1
            return 0.0

        elif self.reward_type == "risk_adjusted":
            # Penalize drawdowns
            dd_penalty = 0
            if step_return < -0.02:
                dd_penalty = step_return * 5  # Extra penalty for large losses
            return step_return * 100 + dd_penalty

        return step_return * 100
```

## Tabular Q-Learning Agent

For small, discretized state spaces, tabular Q-learning provides a simple and interpretable baseline.

```python
class QLearningAgent:
    """
    Tabular Q-learning agent for trading.
    Discretizes continuous states into bins.
    """

    def __init__(
        self,
        n_actions: int = 3,
        n_bins: int = 10,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
    ):
        self.n_actions = n_actions
        self.n_bins = n_bins
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        self.q_table = {}
        self.bin_edges = None

    def _discretize_state(self, state: np.ndarray) -> tuple:
        """Convert continuous state to discrete bin indices."""
        if self.bin_edges is None:
            # Initialize bins on first call (will be rough)
            self.bin_edges = [
                np.linspace(-3, 3, self.n_bins + 1)
                for _ in range(min(len(state), 10))  # Use first 10 dims
            ]

        # Use only the most important state dimensions
        key_dims = state[:min(len(state), 10)]
        discrete = tuple(
            np.digitize(key_dims[i], self.bin_edges[i])
            for i in range(len(key_dims))
        )
        return discrete

    def get_action(self, state: np.ndarray) -> int:
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)

        discrete_state = self._discretize_state(state)
        q_values = [
            self.q_table.get((discrete_state, a), 0.0)
            for a in range(self.n_actions)
        ]
        return int(np.argmax(q_values))

    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
    ):
        """Update Q-value using Bellman equation."""
        s = self._discretize_state(state)
        s_next = self._discretize_state(next_state)

        current_q = self.q_table.get((s, action), 0.0)

        if done:
            target = reward
        else:
            next_q_values = [
                self.q_table.get((s_next, a), 0.0)
                for a in range(self.n_actions)
            ]
            target = reward + self.gamma * max(next_q_values)

        self.q_table[(s, action)] = current_q + self.lr * (target - current_q)

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
```

## Deep Q-Network (DQN) Agent

DQN replaces the Q-table with a neural network, enabling generalization across continuous state spaces.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class QNetwork(nn.Module):
    """Neural network for Q-value approximation."""

    def __init__(self, state_dim: int, n_actions: int, hidden_dims: list[int] = None):
        super().__init__()
        hidden_dims = hidden_dims or [128, 64, 32]

        layers = []
        prev_dim = state_dim
        for dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, dim),
                nn.ReLU(),
                nn.LayerNorm(dim),
            ])
            prev_dim = dim
        layers.append(nn.Linear(prev_dim, n_actions))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class ReplayBuffer:
    """Experience replay buffer for DQN training."""

    def __init__(self, capacity: int = 100_000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states, dtype=np.float32),
            np.array(actions),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32),
        )

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network agent with target network and experience replay.
    """

    def __init__(
        self,
        state_dim: int,
        n_actions: int = 3,
        lr: float = 1e-4,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay_steps: int = 10_000,
        batch_size: int = 64,
        target_update_freq: int = 1000,
        buffer_size: int = 100_000,
    ):
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        # Epsilon schedule
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = (epsilon_start - epsilon_end) / epsilon_decay_steps

        # Networks
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = QNetwork(state_dim, n_actions).to(self.device)
        self.target_network = QNetwork(state_dim, n_actions).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        self.buffer = ReplayBuffer(buffer_size)
        self.steps = 0

    def get_action(self, state: np.ndarray, training: bool = True) -> int:
        """Epsilon-greedy action selection."""
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return int(q_values.argmax(dim=1).item())

    def train_step(self) -> float | None:
        """Sample from replay buffer and update Q-network."""
        if len(self.buffer) < self.batch_size:
            return None

        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Current Q values
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze()

        # Target Q values (Double DQN)
        with torch.no_grad():
            next_actions = self.q_network(next_states).argmax(dim=1)
            next_q = self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze()
            target_q = rewards + self.gamma * next_q * (1 - dones)

        # Huber loss (more robust than MSE)
        loss = nn.SmoothL1Loss()(current_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()

        # Update target network
        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon - self.epsilon_decay)

        return loss.item()
```

## Training Loop

```python
def train_dqn_agent(
    env: TradingEnv,
    agent: DQNAgent,
    n_episodes: int = 500,
    log_interval: int = 50,
) -> list[dict]:
    """Train DQN agent with logging and early stopping."""
    episode_results = []

    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0
        total_pnl = 0
        steps = 0

        while True:
            action = agent.get_action(state, training=True)
            next_state, reward, done, _, info = env.step(action)

            agent.buffer.push(state, action, reward, next_state, done)
            loss = agent.train_step()

            total_reward += reward
            state = next_state
            steps += 1

            if done:
                break

        episode_results.append({
            "episode": episode,
            "total_reward": total_reward,
            "total_pnl": info["total_pnl"],
            "trades": info["trade_count"],
            "epsilon": agent.epsilon,
        })

        if (episode + 1) % log_interval == 0:
            recent = episode_results[-log_interval:]
            avg_reward = np.mean([r["total_reward"] for r in recent])
            avg_pnl = np.mean([r["total_pnl"] for r in recent])
            avg_trades = np.mean([r["trades"] for r in recent])
            print(
                f"Episode {episode+1}/{n_episodes} | "
                f"Avg Reward: {avg_reward:.2f} | "
                f"Avg PnL: {avg_pnl:.4f} | "
                f"Avg Trades: {avg_trades:.0f} | "
                f"Epsilon: {agent.epsilon:.3f}"
            )

    return episode_results
```

## Evaluation and Deployment

```python
def evaluate_agent(
    env: TradingEnv,
    agent: DQNAgent,
    n_episodes: int = 10,
) -> dict:
    """Evaluate trained agent with epsilon=0 (greedy policy)."""
    results = []

    for _ in range(n_episodes):
        state, _ = env.reset()
        episode_returns = []

        while True:
            action = agent.get_action(state, training=False)
            next_state, reward, done, _, info = env.step(action)
            episode_returns.append(info["step_return"])
            state = next_state
            if done:
                break

        ep_returns = np.array(episode_returns)
        results.append({
            "total_return": (1 + ep_returns).prod() - 1,
            "sharpe": ep_returns.mean() / ep_returns.std() * np.sqrt(252) if ep_returns.std() > 0 else 0,
            "max_drawdown": ((np.maximum.accumulate((1 + ep_returns).cumprod()) - (1 + ep_returns).cumprod()) / np.maximum.accumulate((1 + ep_returns).cumprod())).max(),
            "trades": info["trade_count"],
        })

    avg = {k: np.mean([r[k] for r in results]) for k in results[0]}
    print(f"Evaluation ({n_episodes} episodes):")
    for k, v in avg.items():
        print(f"  {k}: {v:.4f}")
    return avg
```

## FAQ

### Does reinforcement learning actually work for trading?

RL has shown promise in specific trading applications: portfolio allocation (see our [portfolio calculator](https://calculatortools.com/blog/portfolio-allocation-calculator)), execution optimization, and [market making](/blog/market-making-strategies). However, it rarely outperforms simpler methods for directional prediction. The main challenges are non-stationarity (the environment changes), low signal-to-noise ratios, and severe overfitting risk. RL works best when the action space is naturally sequential and the reward structure is well-defined, such as optimal execution where the goal (minimize implementation shortfall) is clear.

### What reward function should I use for a trading RL agent?

Avoid using raw PnL as the reward. Agents trained on raw PnL learn to take maximum leverage, which leads to catastrophic drawdowns. Risk-adjusted rewards work better: differential [Sharpe ratio](/blog/sharpe-ratio-portfolio-analysis) (incremental contribution to rolling Sharpe), or PnL with drawdown penalties. Some practitioners use the log return as the reward, which implicitly favors Kelly-optimal sizing.

### How do I prevent the RL agent from overfitting to training data?

Use multiple independent training environments with different market periods, add noise to observations during training, use domain randomization (randomly vary transaction costs, slippage, and delays), and evaluate on truly out-of-sample data from different time periods. Also keep the agent's capacity small relative to the training data size.

### What is the difference between Q-learning and policy gradient methods for trading?

Q-learning learns a value function (how good is each state-action pair) and derives the policy from it. Policy gradient methods learn the policy directly. For trading with discrete actions (buy/hold/sell), Q-learning tends to be more sample-efficient and stable. For continuous actions ([position sizing](/blog/position-sizing-strategies), multi-asset allocation), policy gradient methods like PPO or SAC are more natural since they output continuous values without discretization.
