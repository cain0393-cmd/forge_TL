# Task 5 Strategy Specification

This document provides a precise, implementation-ready baseline specification for the initial four quantitative strategies in forge_TL.

**Common Engine Rules:**
- All execution strictly obeys Task 4 next-bar causality: Signal observed at completed bar $t$ -> order placed at $t$ -> order eligible strictly $> t$ -> earliest possible execution is $t+1$ or later.
- No optimization has been performed. These are naive, defensible baselines meant for reproducible performance evaluation.
- No future information is utilized.
- Missing data explicitly defaults to skipping signals or dropping universe components without fabrication.

---

## Strategy 1: Cross-Sectional Dual Momentum

**Objective**: Maximize returns by owning the strongest momentum sectors, provided those sectors are also in a positive absolute trend.
**Hypothesis**: Relative momentum persists cross-sectionally among sector indices, and absolute momentum serves as a filter against entering severe equity drawdowns.

**Universe Validation & Correction**:

The originally proposed `FMCG`, `AUTO`, and `INFRA` are broad index names rather than the intended tradable ETF securities.

The frozen baseline universe therefore consists only of the following sector-oriented NSE ETF securities:

`BANKBEES`, `ITBEES`, `PHARMABEES`, `FMCGBEES`, `AUTOBEES`, `INFRABEES`.

`MID150BEES` is intentionally excluded because it represents broad mid-cap exposure rather than a sector exposure and would therefore change the cross-sectional sector-momentum hypothesis being tested.

**Historical Availability Constraint**:
Each security is eligible only when sufficient historical observations actually exist. A security is never assumed to exist before its available historical data. For the 252-session relative-momentum calculation, at least 253 close observations are required.

No historical prices are fabricated for unavailable securities.
- *Constraint*: We strictly respect historical inception dates. If a symbol lacks sufficient historical data to calculate the lookback window on bar $t$, it is excluded from the ranking for that bar. No survivorship bias injection via fabricated early data.

**Required Data**:
- Historical ETF prices.

**Signal Calculation**:
- **Relative Momentum**: Rate of Change (ROC) over 252 trading days. $M_{rel} = \frac{Close_t}{Close_{t-252}} - 1$.
- **Absolute Momentum**: 21-day Rate of Change > 0. $M_{abs} = \frac{Close_t}{Close_{t-21}} - 1 > 0$.

**Entry/Ranking Rules**:
- Calculate $M_{rel}$ and $M_{abs}$ for all symbols in the universe that have at least 252 days of history.
- Filter: Keep only symbols where $M_{abs}$ is True.
- Rank: Sort remaining eligible symbols descending by $M_{rel}$.
- Select: Top 3 symbols.

**Exit Rules**:
- Every rebalance day, exit any currently held symbol that is no longer in the Top 3 passing the absolute filter.

**Rebalance Frequency**:
- Monthly (every 21 trading bars).

**Position Limits / Sizing**:
- Equal weight across selected assets. If 3 assets qualify, each gets 33.3% of current portfolio equity. Cash is held if < 3 assets qualify.
- No leverage. No shorting.

**Tie Handling**:
- If $M_{rel}$ ties, sort alphabetically by symbol as a deterministic tie-breaker.

**Lookahead Risks**:
- Evaluated on $Close_t$, execution is requested strictly $> t$. The 252-day lookback is inclusive of $t$. No forward leakage.

**Parameter Defaults**:
- `momentum_window` = 252
- `rebalance_bars` = 21
- `top_n` = 3

---

## Strategy 2: Multi-Asset Trend Following

**Objective**: Participate in large macroeconomic trends while avoiding major drawdowns by using moving-average crossovers across diverse asset classes.
**Hypothesis**: Large capital flows create persistent, multi-month trends across uncorrelated asset classes (equities, gold, bonds).

**Universe**:
- `NIFTYBEES` (Large-cap Indian Equities)
- `JUNIORBEES` (Mid-cap Indian Equities)
- `GOLDBEES` (Gold)
- `SILVERBEES` (Silver)
- `SETF10GILT` (10-Year Indian Gov Bonds)

**Required Data**:
- Historical ETF prices.

**Signal Calculation**:
- **Trend Indicator**: 200-day Simple Moving Average ($SMA_{200}$).

**Entry/Exit Rules**:
- **Entry**: If $Close_t > SMA_{200}$, trend is positive. Asset is eligible for holding.
- **Exit**: If $Close_t < SMA_{200}$, trend is negative. Asset is sold.

**Ranking Rules**:
- No cross-sectional ranking. The strategy evaluates every asset entirely independently.

**Position Sizing**:
- Equal target allocation per asset (20% equity per asset).
- If an asset is below its SMA, its 20% allocation remains in cash.
- Rebalance occurs on any crossover signal. The strategy outputs target weights directly using the backtester's native capabilities, without introducing a separate portfolio allocator component.
- No shorting, no leverage.

**Missing Data**:
- If an asset lacks 200 days of history, it is deemed ineligible and its weight is 0%.

**Tie Handling**:
- Irrelevant due to independent signal generation.

**Lookahead Risks**:
- Same as above. The SMA strictly utilizes $[t-199, t]$. Orders submitted > $t$.

**Parameter Defaults**:
- `sma_window` = 200

---

## Strategy 3: Statistical Mean Reversion

**Objective**: Exploit short-term overreactions in index constituents by fading extreme statistical deviations.
**Hypothesis**: Large, rapid price drops in liquid index constituents tend to over-correct and revert to their near-term mean within a few days.

**Universe**:
- Point-in-time Nifty 50.

**Data Dependency Declaration**:
- Historical Nifty 50 PIT membership data is NOT available in the current DuckDB database.
- **Implementation Mechanism**: The strategy will depend on a `UniverseProvider` interface. For testing purposes, we use a mock provider returning fixed symbols. Synthetic PIT-universe data is ONLY for mechanics testing. No real performance claim until real data is sourced. Do NOT fall back to ETFs.

**Signal Calculation**:
- $r_t = \frac{Close_t}{Close_{t-1}} - 1$.
- $CR5_t = \prod_{i=0}^4 (1 + r_{t-i}) - 1$ (the product of the trailing 5 returns ending at $t$).
- $\mu_{20,t}$ = mean of trailing 20 daily returns ending at $t$.
- $\sigma_{20,t}$ = population standard deviation of those same 20 returns.
- $Z_t = \frac{CR5_t - 5 \times \mu_{20,t}}{\sqrt{5} \times \sigma_{20,t}}$.

*The specification must explicitly state that the CR5 window is the trailing five returns contained within the trailing 20-return reference distribution.*

**Entry/Exit Rules**:
- **Entry**: If $Z_t < -2.0$, Buy.
- **Exit**: If $Z_t > 0.0$ (reverted to mean) OR holding period reaches 5 bars.

**Position Sizing / Limits**:
- Equal weight based on maximum simultaneous holdings limit of 5 (20% per position).
- If more than 5 qualify, select the 5 most negative Z-scores.

**Tie Handling**:
- If Z-scores tie, sort alphabetically.

**Missing Data / Extremes**:
- If $\sigma_{20} == 0$, Z-score is 0 (ignore).
- If < 25 days history, skip symbol.

**Parameter Defaults**:
- `mean_window` = 20
- `return_window` = 5
- `entry_z` = -2.0
- `exit_z` = 0.0
- `max_holdings` = 5

---

## Strategy 4: Post-Earnings Announcement Drift (PEAD)

**Objective**: Capture the delayed, systematic price drift that follows extreme fundamental earnings surprises.
**Hypothesis**: The market underreacts to significant earnings surprises, causing the price to drift in the direction of the surprise over the subsequent weeks.

**Universe**:
- Broad Equities (All available symbols).

**Data Dependency Declaration**:
- Historical Earnings Data is NOT available in the current DuckDB database.
- **Implementation Mechanism**: The strategy strictly enforces a deterministic PEAD data contract. It depends on an `EarningsEventProvider` which yields events containing `event_timestamp`, `available_timestamp`, `surprise_pct`, and `period_end`. 

**Strict Separation of Time**:
- `period_end`: The end of the reporting period (e.g., quarter end).
- `event_timestamp`: The actual time the earnings announcement occurred.
- `available_timestamp`: The exact timestamp the information became machine-readable/publicly available.
- **Signal Rule**: The strategy asks the provider for events where `available_timestamp <= current_bar_timestamp`. It records events it has processed to prevent re-processing. If an event's `available_timestamp` falls over a weekend, it becomes observable on Monday's close.
- **Order Rule**: Orders are generated strictly when observed at $t$. Thus `eligible_at` becomes `current_bar_timestamp + 1 microsecond`, guaranteeing NO pre-announcement trading.

**Signal Calculation**:
- **Surprise**: Uses the provided `surprise_pct` from the data contract.

**Entry/Exit Rules**:
- **Entry**: If `surprise_pct` > 10.0%, Buy.
- **Exit**: Time-based exit exactly 20 trading bars after entry.

**Position Limits**:
- Allocates fixed percentage of current equity (e.g. 5% per event) up to 100% capacity.

**Missing Data**:
- If an event has no `available_timestamp`, it is entirely dropped.

**Parameter Defaults**:
- `surprise_threshold` = 10.0
- `holding_bars` = 20
- `allocation_pct` = 0.05
