# Alpha Source Map & Research Prioritization

## Objective
To identify 15 genuinely distinct alpha mechanisms and rank them for future research in the `forge_TL` project.

### C01 - Overnight Gap Reversal
- **Family**: Price/Return
- **Mechanism**: Large overnight gaps (up or down) reverse during the ensuing day or next few days.
- **Economic Rationale**: Retail overreaction at the open is absorbed by institutional liquidity providers, pulling price back to fundamental value.
- **Indian Relevance**: Indian markets have heavy retail participation at the open, often driven by global cues (SGX Nifty / US markets), leading to exaggerated opening prints.
- **Required Data**: Daily OHLC (Open and Close separately).
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: PARTIALLY_FEASIBLE (Requires entering at T+1 Open and exiting at T+1 Close for intraday, or T+2 Open for overnight reversal).
- **Cost Sensitivity**: HIGH
- **Capacity**: High capacity on Nifty 50, but susceptible to slippage if executed exactly at the open.
- **Holding Period**: Intraday to 1-2 days
- **Competition**: Widely exploited by HFTs for intraday, less crowded for multiday.
- **Complexity**: LOW
- **Failure Modes**: Transaction costs consuming the small gap edge. Lookahead bias if Open/Close timing is mishandled.
- **Priority Score**: 72.0/100
- **Verdict**: **RESEARCH_READY**

### C02 - Overnight Gap Continuation
- **Family**: Price/Return
- **Mechanism**: Large overnight gaps continue trending in the direction of the gap over the next 3-5 days.
- **Economic Rationale**: Gaps represent major structural news (earnings, macro). Price discovery is not instantaneous; institutional money scales in over several days.
- **Indian Relevance**: Institutional execution in India often spans multiple days due to liquidity constraints in even Nifty 50 stocks.
- **Required Data**: Daily OHLC.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: MODERATE
- **Capacity**: High capacity.
- **Holding Period**: 3-5 days
- **Competition**: Moderately crowded.
- **Complexity**: LOW
- **Failure Modes**: Whipsaws in choppy regimes. Transaction costs.
- **Priority Score**: 84.0/100
- **Verdict**: **RESEARCH_READY**

### C03 - Short-Term Cross-Sectional Reversal
- **Family**: Price/Return
- **Mechanism**: Buy the worst 5 performers of the Nifty 50 over the last 3 days.
- **Economic Rationale**: Liquidity shocks and temporary supply imbalances cause price dislocation that reverts as market makers restore equilibrium.
- **Indian Relevance**: Highly relevant. Concentrated ETF flows often blindly sell constituents, causing temporary dislocations in fundamentally sound stocks.
- **Required Data**: Daily Close.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: HIGH
- **Capacity**: High.
- **Holding Period**: 3-5 days
- **Competition**: Moderately crowded.
- **Complexity**: LOW
- **Failure Modes**: Catching falling knives during severe market crashes. Cost drag.
- **Priority Score**: 79.0/100
- **Verdict**: **RESEARCH_READY**

### C04 - Residual Momentum
- **Family**: Price/Return
- **Mechanism**: Regress stock returns against the Nifty 50. Buy stocks with the highest residual (idiosyncratic) momentum.
- **Economic Rationale**: Stripping out market beta reveals true, stock-specific accumulation by informed market participants.
- **Indian Relevance**: Indian indices are heavily skewed by a few mega-caps (Reliance, HDFC). Residual momentum isolates true stock-specific flows.
- **Required Data**: Daily Close, Nifty 50 Index Close.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: MODERATE
- **Capacity**: High.
- **Holding Period**: 1-4 weeks
- **Competition**: Less researched than absolute momentum.
- **Complexity**: MEDIUM
- **Failure Modes**: Requires robust rolling regressions (computational overhead). Market neutral portfolios require shorting, which is blocked. Long-only residual momentum may underperform in bull runs.
- **Priority Score**: 86.0/100
- **Verdict**: **RESEARCH_PRIORITY**

### C05 - Volatility Compression Breakout (NR7)
- **Family**: Price/Return
- **Mechanism**: Buy stocks experiencing extreme short-term volatility compression (e.g., Narrowest Range of last 7 days) that subsequently break out.
- **Economic Rationale**: Volatility is cyclical. Periods of extreme indifference/compression reliably precede violent expansions as new information enters.
- **Indian Relevance**: Classic retail strategy in India, but often executed poorly. Systematizing it cross-sectionally on Nifty 50 provides statistical rigor.
- **Required Data**: Daily OHLC.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: MODERATE
- **Capacity**: High.
- **Holding Period**: 2-5 days
- **Competition**: Widely known, but mostly applied discretionarily.
- **Complexity**: LOW
- **Failure Modes**: False breakouts. Low hit rate requires strict risk management.
- **Priority Score**: 77.0/100
- **Verdict**: **RESEARCH_READY**

### C06 - Silent Volume Shock
- **Family**: Volume/Liquidity
- **Mechanism**: Volume > 3x average, but price change is exceptionally tight (< 0.5%).
- **Economic Rationale**: Institutional accumulation happening passively against retail selling, absorbing all liquidity without moving price.
- **Indian Relevance**: Pre-breakout footprint for large caps where massive liquidity is needed to build positions.
- **Required Data**: Daily OHLCV.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: MODERATE
- **Capacity**: High.
- **Holding Period**: 1-3 weeks
- **Competition**: Less researched systematically.
- **Complexity**: MEDIUM
- **Failure Modes**: Could represent a large block deal with no directional implication. Hard to distinguish accumulation from distribution without OI.
- **Priority Score**: 86.0/100
- **Verdict**: **RESEARCH_PRIORITY**

### C07 - Price-Volume Divergence (Exhaustion)
- **Family**: Volume/Liquidity
- **Mechanism**: Price drops to a new 20-day low, but volume is < 50% of 20-day average.
- **Economic Rationale**: Lack of selling pressure at lows indicates supply exhaustion. The markdown is unconfirmed by institutional volume.
- **Indian Relevance**: Useful in identifying false breakdowns in a structurally long-biased market.
- **Required Data**: Daily OHLCV.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: HIGH
- **Capacity**: Moderate.
- **Holding Period**: 2-5 days
- **Competition**: Moderate.
- **Complexity**: LOW
- **Failure Modes**: Catching falling knives. Low volume might just precede a massive volume washout.
- **Priority Score**: 80.0/100
- **Verdict**: **RESEARCH_READY**

### C08 - Market Breadth Divergence
- **Family**: Market Structure
- **Mechanism**: Nifty 50 index is rising, but Nifty 50 Advance-Decline line is falling. Used as a market-timing regime filter.
- **Economic Rationale**: Trend is supported by only a few heavyweights; market is internally weak and prone to systemic reversal.
- **Indian Relevance**: Nifty 50 is heavily cap-weighted. Reliance and HDFC Bank can mask underlying weakness in the other 48 stocks.
- **Required Data**: Daily Close of all Nifty 50 stocks + Index Close.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE (Regime filter applied to cash strategies).
- **Cost Sensitivity**: LOW COST SENSITIVITY (Reduces trades, thus saving costs).
- **Capacity**: Market-wide.
- **Holding Period**: 1-3 months (Regime duration)
- **Competition**: Standard institutional tool.
- **Complexity**: MEDIUM
- **Failure Modes**: Can keep you out of a narrow but persistent bull market, causing severe underperformance vs benchmark.
- **Priority Score**: 92.0/100
- **Verdict**: **RESEARCH_READY**

### C09 - India VIX Panic Spikes
- **Family**: Cross-Asset
- **Mechanism**: Buy Nifty 50 stocks when India VIX spikes > 20% in 3 days.
- **Economic Rationale**: VIX spikes indicate forced liquidation, margin calls, and panic pricing, creating a transient risk-premium overcompensation.
- **Indian Relevance**: Indian retail panic and DII (Domestic Institutional Investors) acting as liquidity providers of last resort creates reliable mean reversion after VIX spikes.
- **Required Data**: India VIX Daily Close, Nifty 50 Equity OHLC.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: LOW COST SENSITIVITY (High gross returns from buying panics overcome friction).
- **Capacity**: Massive.
- **Holding Period**: 1-4 weeks
- **Competition**: Less crowded systematically in cash equities.
- **Complexity**: LOW
- **Failure Modes**: In a true systemic crisis (e.g., COVID 2020), VIX can stay elevated while equities drop another 30%. Requires strict capital scaling.
- **Priority Score**: 93.0/100
- **Verdict**: **RESEARCH_PRIORITY**

### C10 - VIX Term Structure / Basis
- **Family**: Cross-Asset
- **Mechanism**: Ratio of Implied Volatility (VIX) to Realized Volatility (20-day historical vol of Nifty 50). Buy when IV/RV > 1.5.
- **Economic Rationale**: When implied volatility wildly exceeds actual realized volatility, fear is overpriced relative to the actual mathematical risk.
- **Indian Relevance**: Retail option buying in India chronically overprices downside puts, driving VIX artificially high relative to actual index movement.
- **Required Data**: India VIX, Nifty 50 Index.
- **Data Status**: AVAILABLE
- **PIT Status**: YES
- **Execution Feasibility**: FEASIBLE
- **Cost Sensitivity**: LOW COST SENSITIVITY
- **Capacity**: Massive.
- **Holding Period**: 1-4 weeks
- **Competition**: Standard for option sellers, rare for cash equity timing.
- **Complexity**: MEDIUM
- **Failure Modes**: Realized vol can suddenly spike to meet implied vol.
- **Priority Score**: 94.0/100
- **Verdict**: **RESEARCH_PRIORITY**

### C11 - Sector Index Reversion
- **Family**: Market Structure
- **Mechanism**: Buy Nifty 50 stocks belonging to a sector that crashed > 5% yesterday.
- **Economic Rationale**: Sector ETF redemptions blindly sell all constituents, creating a liquidity gap in fundamentally strong stocks.
- **Indian Relevance**: Sectoral funds are highly popular in India, causing correlated indiscriminate selling.
- **Required Data**: Sector Index OHLC, Historical PIT Stock-to-Sector Mappings.
- **Data Status**: BLOCKED
- **PIT Status**: BLOCKED (No historical PIT sector mappings).
- **Execution Feasibility**: N/A
- **Cost Sensitivity**: N/A
- **Capacity**: N/A
- **Holding Period**: N/A
- **Competition**: N/A
- **Complexity**: VERY HIGH (Data Engineering)
- **Failure Modes**: N/A
- **Priority Score**: 0.0/100
- **Verdict**: **DATA_BLOCKED**

### C12 - Index Rebalancing Anticipation
- **Family**: Events
- **Mechanism**: Buy stocks likely to be included in Nifty 50 ahead of the official inclusion date.
- **Economic Rationale**: Passive index funds are forced to buy, pushing up the price.
- **Indian Relevance**: Massive passive flows tracking Nifty 50.
- **Required Data**: Historical Nifty 100 free-float market cap data, explicit NSE methodology historical re-runs.
- **Data Status**: BLOCKED
- **PIT Status**: BLOCKED
- **Execution Feasibility**: N/A
- **Cost Sensitivity**: N/A
- **Capacity**: N/A
- **Holding Period**: N/A
- **Competition**: N/A
- **Complexity**: VERY HIGH
- **Failure Modes**: N/A
- **Priority Score**: 0.0/100
- **Verdict**: **DATA_BLOCKED**

### C13 - Post-Earnings Announcement Drift (PEAD)
- **Family**: Events
- **Mechanism**: Standardized unexpected earnings predict multi-week drift.
- **Economic Rationale**: Analysts anchor to old estimates and slowly revise them upwards.
- **Indian Relevance**: Classic anomaly.
- **Required Data**: Consensus estimates, exact earnings timestamps.
- **Data Status**: BLOCKED
- **PIT Status**: BLOCKED
- **Execution Feasibility**: N/A
- **Cost Sensitivity**: N/A
- **Capacity**: N/A
- **Holding Period**: N/A
- **Competition**: N/A
- **Complexity**: VERY HIGH
- **Failure Modes**: N/A
- **Priority Score**: 0.0/100
- **Verdict**: **DATA_BLOCKED**

### C14 - Derivative-Confirmed Momentum
- **Family**: Derivatives
- **Mechanism**: Price breakout + Futures OI expansion.
- **Economic Rationale**: Breakout is supported by new committed capital (OI), not just short covering.
- **Indian Relevance**: Indian F&O market is one of the most active in the world.
- **Required Data**: Historical Futures OI.
- **Data Status**: BLOCKED (Requires external acquisition of 2200 Bhavcopies).
- **PIT Status**: BLOCKED
- **Execution Feasibility**: N/A
- **Cost Sensitivity**: N/A
- **Capacity**: N/A
- **Holding Period**: N/A
- **Competition**: N/A
- **Complexity**: VERY HIGH
- **Failure Modes**: N/A
- **Priority Score**: 32.0/100
- **Verdict**: **DATA_BLOCKED**

### C15 - Institutional Flow Shocks
- **Family**: Derivatives
- **Mechanism**: Follow extreme FII/DII daily net flows.
- **Economic Rationale**: Massive institutional money physically moves the market.
- **Indian Relevance**: FII flows heavily dictate Indian market trends.
- **Required Data**: FII/DII daily aggregates.
- **Data Status**: BLOCKED
- **PIT Status**: BLOCKED
- **Execution Feasibility**: N/A
- **Cost Sensitivity**: N/A
- **Capacity**: N/A
- **Holding Period**: N/A
- **Competition**: N/A
- **Complexity**: VERY HIGH
- **Failure Modes**: N/A
- **Priority Score**: 0.0/100
- **Verdict**: **DATA_BLOCKED**

