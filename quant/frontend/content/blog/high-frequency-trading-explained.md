---
title: "High-Frequency Trading Explained: How HFT Actually Works"
description: "Understand how high-frequency trading works, including market making, latency arbitrage, and statistical arbitrage at microsecond timescales."
date: "2026-03-27"
author: "Dr. James Chen"
category: "Algo Trading"
tags: ["high-frequency trading", "HFT", "market making", "latency arbitrage"]
keywords: ["high-frequency trading explained", "how HFT works", "high-frequency trading strategies"]
---

# High-Frequency Trading Explained: How HFT Actually Works

High-frequency trading (HFT) is the most technologically intensive segment of financial markets, where firms compete to execute strategies at microsecond timescales. HFT accounts for approximately 50-60% of US equity volume and has fundamentally changed market structure since its rise in the mid-2000s. Despite widespread media attention and regulatory scrutiny, particularly after Michael Lewis's "Flash Boys" (2014), HFT remains poorly understood by most market participants. This guide explains how HFT actually works, the strategies employed, the technology required, and the impact on market quality.

The goal is not to teach readers how to build an HFT system (which requires millions in infrastructure), but to provide a quantitative understanding of HFT mechanics that informs better trading decisions for all market participants.

## What Qualifies as High-Frequency Trading?

### Defining Characteristics

The SEC and CFTC define HFT by several characteristics:

1. **Extraordinary speed**: Order submission and cancellation in microseconds (millionths of a second)
2. **Co-location**: Servers physically located in exchange data centers
3. **High message rates**: Millions of orders per day
4. **Very short holding periods**: Seconds to minutes (rarely overnight)
5. **Low per-trade profit**: Fractions of a cent per share
6. **High volume**: Profitability depends on massive trade counts
7. **Minimal overnight inventory**: Positions are largely flat by market close

### HFT by the Numbers

| Metric | Typical HFT Firm |
|--------|-----------------|
| Latency (order submission) | 1-10 microseconds |
| Daily orders | 1-10 million |
| Daily trades | 100,000-1,000,000 |
| Average hold time | 5 seconds - 5 minutes |
| Profit per trade | $0.001 - $0.01 per share |
| Daily revenue | $100,000 - $5,000,000 |
| Annual revenue | $25M - $1B+ |
| Infrastructure cost | $5M - $50M/year |

## Core HFT Strategies

### Strategy 1: Electronic Market Making

The most common HFT strategy: continuously posting bid and ask quotes, earning the spread on each round trip.

**How it works**:
1. Post a bid at $100.00 and an ask at $100.01
2. If both sides fill: profit = $0.01 per share (1 cent spread)
3. Adjust quotes based on inventory, volatility, and order flow
4. Maintain near-zero inventory at all times

**Key challenges**:
- **Adverse selection**: Informed traders hit your quotes when the price is about to move against you
- **Inventory risk**: Accumulating unwanted inventory during directional moves
- **Quote competition**: Other market makers competing for the same spread

**Profit model**: A successful market maker earns 30-50% of the gross spread after adverse selection losses. On a stock with a $0.01 spread, that is $0.003-0.005 per share, multiplied by millions of shares daily.

### Strategy 2: Latency Arbitrage

Exploit the speed difference between exchanges to profit from stale quotes.

**How it works**:
1. Stock trades at $100.00 on Exchange A
2. Large buy order on Exchange A pushes price to $100.01
3. Exchange B still shows $100.00 (a few microseconds behind)
4. HFT buys at $100.00 on Exchange B before the quote updates
5. Sells at $100.01 when Exchange B's price catches up

**Controversy**: Latency arbitrage is the most criticized HFT strategy because it taxes other market participants (particularly institutional investors who post limit orders on slower exchanges). Budish, Cramton, and Shim (2015) estimated that latency arbitrage extracts approximately $5 billion annually from US equity markets.

**Infrastructure requirement**: Proprietary fiber optic cables, microwave towers, or even shortwave radio between exchange data centers. The latency difference between fiber optic and microwave between Chicago (CME) and New Jersey (NYSE) is approximately 4.5 milliseconds vs. 4.1 milliseconds.

### Strategy 3: Statistical Arbitrage at High Frequency

Apply traditional stat arb models (pairs trading, mean reversion) at millisecond timescales.

**How it works**:
1. Monitor relationships between correlated instruments (SPY vs. ES futures, ETFs vs. component stocks)
2. When a temporary price divergence occurs (due to order flow or latency)
3. Trade the convergence
4. Hold for milliseconds to seconds

**Example**: ETF arbitrage. When SPY's theoretical price (calculated from component stocks) diverges from its traded price by more than transaction costs, trade the convergence.

### Strategy 4: Event-Driven HFT

Trade on public information releases faster than other participants.

**How it works**:
1. Parse economic data releases (FOMC, NFP, CPI) in microseconds
2. Analyze the deviation from consensus expectations
3. Submit orders before other participants can process the information

**Technology**: Natural language processing pipelines that parse press releases, news wires, and SEC filings in under 1 millisecond. Some firms use pre-parsed feeds from providers like Refinitiv or Bloomberg that deliver structured data.

## The Technology Stack

### Hardware

| Component | Specification | Cost |
|-----------|--------------|------|
| Co-located server | Custom-built, air-cooled | $50K-200K |
| Network interface card | Solarflare/Mellanox (kernel bypass) | $5K-15K |
| FPGA boards | Xilinx/Intel (sub-microsecond logic) | $10K-50K |
| Microwave towers | Custom link (Chicago-NJ) | $10M+ (one-time) |
| Data feeds | Direct exchange feeds (not consolidated) | $100K-500K/year |
| Co-location rack | Exchange data center | $5K-20K/month |

### Software

**Operating system**: Linux with custom kernel modifications for low-latency networking (kernel bypass, huge pages, CPU pinning, interrupt affinity).

**Programming languages**: C++ (core strategy logic, order management), FPGA/Verilog (hardware-accelerated processing), Python (research, backtesting, monitoring only).

**Key optimizations**:
- Lock-free data structures (avoid mutex contention)
- Memory-mapped I/O (eliminate kernel overhead)
- Zero-copy networking (move data without copying between buffers)
- Cache optimization (keep hot data in L1/L2 cache)
- Pre-computed decision tables (avoid real-time computation)

### Latency Budget

| Component | Latency |
|-----------|---------|
| Market data receive | 1-5 microseconds |
| Signal processing | 0.5-2 microseconds |
| Risk check | 0.1-0.5 microseconds |
| Order submission | 1-3 microseconds |
| **Total (tick-to-trade)** | **3-10 microseconds** |

For comparison, a human blink takes approximately 300,000 microseconds.

## HFT's Impact on Market Quality

### Positive Effects

**Tighter spreads**: HFT competition has reduced bid-ask spreads by 50-70% since the mid-2000s. The average spread on S&P 500 stocks fell from approximately $0.05 in 2005 to $0.01 in 2025.

**Improved price discovery**: HFT market makers update quotes faster, incorporating new information more quickly into prices.

**Increased liquidity**: Total volume and displayed depth have increased significantly.

### Negative Effects

**Phantom liquidity**: HFT quotes are often cancelled before they can be filled (85-95% cancellation rate). This displayed liquidity may not be accessible to other traders.

**Flash crashes**: HFT can amplify market dislocations, as seen in the May 2010 Flash Crash (-9.2% in minutes) and numerous "mini flash crashes" in individual stocks.

**Adverse selection**: HFT market makers selectively avoid trading with informed counterparties, leaving institutional investors with worse execution on their most valuable orders.

**Arms race externalities**: The billions spent on latency infrastructure produce no social value beyond transferring profits between market participants. Budish et al. proposed frequent batch auctions as an alternative.

### Net Assessment

Academic consensus (Menkveld, 2013; Brogaard, Hendershott, and Riordan, 2014) is that HFT market making improves market quality on average (tighter spreads, better price discovery) but that latency arbitrage creates costs for other participants. The net effect is debated but likely modestly positive for most investors.

## What Non-HFT Traders Should Know

### Practical Implications

1. **Avoid market orders in fast markets**: During high volatility, HFT market makers widen spreads and reduce displayed depth. Your market order may execute at prices far from the NBBO.

2. **Use limit orders**: HFT cannot adversely select against limit orders that are passively resting. Use limit orders placed inside the spread for better execution.

3. **Avoid the open and close**: HFT activity and spread variability are highest during the first and last 15 minutes. Mid-session execution is typically better for non-urgent orders.

4. **Be aware of phantom liquidity**: Displayed depth at the top of the order book may not be accessible. Look at depth across multiple price levels.

5. **Use algorithmic execution for large orders**: VWAP, TWAP, and implementation shortfall algorithms minimize the information leakage that HFT can exploit.

### The "Speed Tax" on Retail Traders

For typical retail orders (100-1,000 shares), HFT's impact is minimal. Retail order flow is mostly handled by wholesalers (Citadel Securities, Virtu Financial) who provide price improvement relative to the NBBO. The average retail order receives $0.001-0.003 per share in price improvement.

For institutional orders (10,000+ shares), HFT can significantly increase execution costs through information leakage and adverse selection. This is where dark pools and sophisticated execution algorithms provide value.

## Regulatory Landscape

### Key Regulations

| Regulation | Jurisdiction | Impact |
|-----------|-------------|--------|
| Reg NMS (2007) | US | Created the order routing system HFT exploits |
| MiFID II (2018) | EU | HFT registration, tick size regime, market maker obligations |
| Consolidated Audit Trail | US | Full order lifecycle tracking for surveillance |
| SEC Market Structure Reform | US (proposed) | Minimum tick sizes, order-by-order competition |

### Proposed Reforms

**Frequent batch auctions** (Budish et al.): Replace continuous trading with discrete auctions every 100 milliseconds. This would eliminate latency arbitrage while maintaining price discovery.

**Speed bumps** (IEX): Introduce a deliberate 350-microsecond delay for incoming orders. IEX's speed bump has been approved by the SEC and reduces latency arbitrage on its exchange.

**Transaction taxes**: Several jurisdictions have proposed per-transaction taxes that would make HFT's high-volume, low-margin model uneconomic. Critics argue this would reduce liquidity and widen spreads.

## Key Takeaways

- HFT accounts for 50-60% of US equity volume, operating at microsecond timescales
- The four core HFT strategies are market making, latency arbitrage, statistical arbitrage, and event-driven trading
- HFT market making has reduced spreads by 50-70% since the mid-2000s, benefiting all investors
- Latency arbitrage extracts approximately $5 billion annually from other market participants
- HFT infrastructure costs $5-50 million annually, creating a barrier to entry
- Non-HFT traders should use limit orders, avoid the open/close, and use algorithmic execution for large orders
- Regulatory proposals (batch auctions, speed bumps) aim to reduce latency arbitrage while preserving market making benefits

## Frequently Asked Questions

### Can retail traders compete with HFT?

Not at the same timescale, nor should they try. HFT competes on microseconds; retail traders should compete on hours, days, or weeks. Retail traders have advantages that HFT does not: patience (no need to turn over positions daily), flexibility (can hold through volatility), and no infrastructure costs. Focus on strategies where holding periods are measured in days or longer, where HFT's speed advantage is irrelevant.

### Is high-frequency trading legal?

Yes, HFT is legal in all major jurisdictions. Market making, statistical arbitrage, and event-driven trading are all legitimate activities. However, specific practices like "spoofing" (placing orders with no intent to fill to manipulate prices) and "layering" (stacking orders to create false impressions of supply/demand) are illegal and have resulted in significant fines and criminal charges.

### How profitable is HFT?

HFT profitability has declined significantly since its peak in 2009-2012 as competition has increased and easy opportunities have been arbitraged away. Industry estimates suggest that aggregate HFT revenue in US equities has declined from approximately $7.2 billion in 2009 to $1.5-2.5 billion in 2024. Individual firms range from $25 million to over $1 billion in annual revenue. The most profitable firms are those with the best technology (lowest latency) and the broadest market coverage (multiple asset classes and geographies).

### Does HFT cause flash crashes?

HFT does not directly cause flash crashes, but it can amplify them. During the May 2010 Flash Crash, HFT firms withdrew liquidity (stopped market making) as prices fell rapidly, exacerbating the decline. When HFT market makers determine that conditions are too risky, they pull their quotes simultaneously, creating a liquidity vacuum. Exchanges have since implemented circuit breakers (Limit Up/Limit Down) to prevent similar events.

---

*This analysis is for educational purposes only. This article describes HFT for informational understanding and does not provide instructions for building HFT systems.*
