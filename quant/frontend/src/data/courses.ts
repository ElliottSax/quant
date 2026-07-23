// QuantEngines — free course content.
// Content is structured blocks (not markdown) so it renders with plain React,
// no extra dependency. Inline **bold** is supported by the renderer.

export type CourseLevel = 'beginner' | 'intermediate' | 'advanced'

export type Block =
  | { type: 'h2' | 'h3' | 'p'; text: string }
  | { type: 'ul' | 'ol'; items: string[] }

export interface Lesson {
  slug: string
  title: string
  description: string
  readTime: string
  blocks: Block[]
  tryIt?: { title: string; description: string; href: string; label: string }
}

export interface Course {
  slug: string
  title: string
  description: string
  level: CourseLevel
  estimatedTime: string
  lessons: Lesson[]
}

const backtestingLessons: Lesson[] = [
  {
    slug: 'what-backtesting-tells-you',
    title: 'What Backtesting Actually Tells You',
    description: 'What a backtest can and cannot prove, and why most published results are worthless.',
    readTime: '6 min',
    blocks: [
      { type: 'h2', text: 'A backtest is a hypothesis test, not a promise' },
      { type: 'p', text: 'Backtesting runs a set of trading rules against historical data to see how they would have performed. That is genuinely useful — but only for what it actually measures.' },
      { type: 'p', text: 'A backtest **can** tell you: whether a strategy had an edge in the past, how volatile that edge was, how deep the losing periods ran, and whether the idea survives different market regimes.' },
      { type: 'p', text: 'A backtest **cannot** tell you: that the edge still exists, that you would have held through the drawdown, or that the future will resemble the sample you tested.' },
      { type: 'h3', text: 'Why most backtest results are worthless' },
      { type: 'ul', items: [
        '**Survivorship bias** — testing on today\'s index members ignores every company that went to zero.',
        '**Look-ahead bias** — using data that was not available at decision time (restated earnings, same-bar closes).',
        '**Ignoring costs** — commissions, spread, and slippage routinely turn a "profitable" high-frequency strategy negative.',
        '**Too few trades** — 20 trades proves nothing. Edge needs a sample large enough to distinguish skill from luck.',
      ] },
      { type: 'h3', text: 'The honest standard' },
      { type: 'p', text: 'Treat a backtest the way a scientist treats one experiment: as weak evidence that justifies further testing, not as a result. The strategies that survive are the ones that keep working on data you did not use to build them.' },
    ],
  },
  {
    slug: 'choosing-a-strategy',
    title: 'Choosing a Strategy Worth Testing',
    description: 'Start from an economic reason a strategy should work — not from a pattern you found in the data.',
    readTime: '6 min',
    blocks: [
      { type: 'h2', text: 'Start with a reason, not a pattern' },
      { type: 'p', text: 'The single biggest determinant of whether your backtest means anything is what you chose to test and why. If you started by mining data for patterns, you will find them — and they will be noise.' },
      { type: 'p', text: 'Instead, start with an economic explanation for why an edge should exist and persist. Someone must be on the other side of your trade for a reason.' },
      { type: 'h3', text: 'Edges with a real explanation' },
      { type: 'ul', items: [
        '**Momentum** — investors underreact to news, so trends persist longer than they should.',
        '**Mean reversion** — forced sellers (margin calls, redemptions) push prices below fair value temporarily.',
        '**Carry** — you are compensated for holding an asset others do not want to hold.',
        '**Risk premia** — you get paid for accepting a risk (illiquidity, volatility) that others avoid.',
      ] },
      { type: 'h3', text: 'Define the rules before you look' },
      { type: 'p', text: 'Write down the entry, the exit, the position size, and the universe before running anything. If you adjust the rules after seeing results, you are no longer testing a hypothesis — you are fitting one.' },
      { type: 'p', text: 'Keep it simple. A strategy with two parameters that works is far more trustworthy than one with nine that works better. Every additional parameter is another way to accidentally fit noise.' },
    ],
  },
  {
    slug: 'metrics-that-matter',
    title: 'The Metrics That Matter',
    description: 'Why total return is the least useful number, and what to read instead: drawdown, Sharpe, and exposure.',
    readTime: '7 min',
    blocks: [
      { type: 'h2', text: 'Total return is the least informative number' },
      { type: 'p', text: 'A strategy that returned 400% tells you almost nothing on its own. Over what period? With how much leverage? Through what drawdown? Concentrated in which few trades?' },
      { type: 'h3', text: 'Read these instead' },
      { type: 'ul', items: [
        '**CAGR** — annualized return, so results across different periods are comparable.',
        '**Maximum drawdown** — the worst peak-to-trough loss. This is the number that decides whether you could actually hold the strategy.',
        '**Sharpe ratio** — return per unit of volatility. Above 1 is good; be suspicious of anything above 3 in a backtest.',
        '**Sortino ratio** — like Sharpe but only penalizes downside volatility, which is what you actually care about.',
        '**Number of trades** — your sample size. Fewer than ~100 and your statistics are fragile.',
        '**Exposure** — how much of the time you were in the market. A strategy in cash 90% of the time is not comparable to buy-and-hold.',
      ] },
      { type: 'h3', text: 'Drawdown is the one that ends careers' },
      { type: 'p', text: 'A 60% drawdown requires a 150% gain just to break even. More importantly, almost nobody keeps executing a system through a 60% loss — they abandon it at the bottom, converting a paper drawdown into a permanent one.' },
      { type: 'p', text: 'Before trading anything, ask honestly: if this lost that much, in real money, would I keep going? If not, the strategy is wrong for you regardless of its Sharpe.' },
      { type: 'h3', text: 'Always compare to the boring benchmark' },
      { type: 'p', text: 'Compare against buy-and-hold on the same universe over the same period. A surprising share of "strategies" underperform simply holding the index once you account for costs and taxes.' },
    ],
  },
  {
    slug: 'overfitting',
    title: 'Overfitting: How Backtests Lie',
    description: 'The failure mode that makes a strategy look brilliant historically and lose money live.',
    readTime: '7 min',
    blocks: [
      { type: 'h2', text: 'The core problem' },
      { type: 'p', text: 'Overfitting is building a strategy that describes the noise in your sample rather than the signal. It produces a beautiful equity curve on the data you tested and a flat or negative one on data you did not.' },
      { type: 'p', text: 'It rarely feels like cheating. It feels like diligent research: trying a 50-day moving average, then 52, then 47, and keeping whichever performed best.' },
      { type: 'h3', text: 'Warning signs you have overfit' },
      { type: 'ul', items: [
        'Performance collapses when you change a parameter slightly (50-day works, 45-day does not).',
        'The strategy has many parameters relative to the number of trades.',
        'Results depend heavily on one period or a handful of outsized trades.',
        'You tested dozens of variants and are reporting the best one.',
        'Sharpe above 3 with no obvious structural explanation.',
      ] },
      { type: 'h3', text: 'Defenses that actually work' },
      { type: 'ul', items: [
        '**Hold out data.** Build on one period, test once on another you never looked at.',
        '**Walk-forward testing.** Re-fit on a rolling window and test on the period immediately after, repeatedly.',
        '**Prefer parameter plateaus.** A strategy that works across 40–60 day lookbacks is real; one that only works at 51 is noise.',
        '**Count your attempts.** If you tried 100 variants, the best one looking good is expected by chance.',
      ] },
      { type: 'p', text: 'The uncomfortable rule: every time you look at the test data and adjust, you have spent some of its value. Look as few times as you can.' },
    ],
  },
  {
    slug: 'run-your-first-backtest',
    title: 'Running Your First Backtest',
    description: 'A practical checklist to take one simple strategy from idea to evaluated result.',
    readTime: '6 min',
    blocks: [
      { type: 'h2', text: 'Do the whole loop once, simply' },
      { type: 'p', text: 'The goal of your first backtest is not to find a profitable system. It is to complete the full loop end to end so you learn where the traps are. Pick something almost trivially simple.' },
      { type: 'h3', text: 'A reasonable first test' },
      { type: 'ol', items: [
        'Pick one liquid universe (a broad index\'s members, or a handful of large-cap names).',
        'Pick one simple rule with an economic story — e.g. buy when the 50-day crosses above the 200-day, exit on the reverse cross.',
        'Fix your position sizing (equal weight is fine) and write the rules down before running.',
        'Include costs — commission plus a realistic spread/slippage assumption.',
        'Run it over a period containing at least one bear market so you see the drawdown.',
      ] },
      { type: 'h3', text: 'Then interrogate the result' },
      { type: 'ul', items: [
        'What was the maximum drawdown, and would you have held through it?',
        'How many trades? Is the sample big enough to mean anything?',
        'Does it beat buy-and-hold after costs?',
        'Does it still work if you shift the parameters ±20%?',
        'Does it work in a period you did not use while building it?',
      ] },
      { type: 'p', text: 'If it survives all five, you have something worth researching further — not something worth funding. The next step is walk-forward testing and paper trading, in that order.' },
    ],
    tryIt: {
      title: 'Build and run it',
      description: 'Use the strategy builder to configure the rules above and run the backtest against historical data.',
      href: '/backtesting/builder',
      label: 'Open the Strategy Builder',
    },
  },
]

export const courses: Course[] = [
  {
    slug: 'backtesting-101',
    title: 'Backtesting Your First Strategy',
    description:
      'A free, five-lesson course on backtesting done honestly: what a backtest proves, choosing a strategy with a real economic edge, the metrics that matter, how overfitting fools you, and running your first test end to end.',
    level: 'beginner',
    estimatedTime: '~32 min',
    lessons: backtestingLessons,
  },
]

export function getCourse(slug: string): Course | undefined {
  return courses.find((c) => c.slug === slug)
}
