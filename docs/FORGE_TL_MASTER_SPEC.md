# FORGE_TL — Master System Specification

## 0. PROJECT IDENTITY

Project name:

FORGE_TL

FORGE_TL is a systematic trading research and execution engine for Indian markets.

Primary objective:

Build a small, auditable, testable trading system capable of:

1. Historical data ingestion
2. Data validation
3. Historical backtesting
4. Strategy research
5. Portfolio/risk management
6. Paper trading
7. Eventually live execution

The system must prioritize:

* correctness
* reproducibility
* realistic trading assumptions
* minimal complexity
* auditability
* risk control

The system is NOT intended to become a general-purpose trading framework.

Do not build unnecessary abstractions.

---

# 1. MARKET

Initial market:

NSE India cash equities.

Initial trading style:

Long-only delivery/CNC.

Initial capital:

₹50,000.

Initial maximum simultaneous positions:

2.

Initial risk budget:

1% of capital per trade.

Initial risk amount at ₹50,000:

₹500.

The system must not assume that leverage, futures, options, short selling, intraday margin, or derivatives are available.

Derivatives may be added only in a later phase.

---

# 2. INITIAL STRATEGIES

The initial strategy research set is:

1. Cross-Sectional Dual Momentum
2. Multi-Asset Trend Following
3. Statistical Mean Reversion
4. Post-Earnings Announcement Drift (PEAD)

Strategy implementation order:

1. Cross-Sectional Dual Momentum
2. Multi-Asset Trend Following
3. Statistical Mean Reversion
4. PEAD

Do not implement all four simultaneously.

Each strategy must independently pass research/backtest validation before entering the portfolio allocator.

---

# 3. INITIAL PORTFOLIO ARCHITECTURE

Capital is initially divided conceptually into two slots.

Slot 1:

Macro Anchor

Initial allocation:

₹25,000.

Slot 2:

Tactical Alpha

Initial allocation:

₹25,000.

Slot 1 priority:

1. Cross-Sectional Dual Momentum
2. Multi-Asset Trend Following
3. Defensive asset/cash

Slot 2 priority:

1. PEAD
2. Statistical Mean Reversion
3. Cash

Initial maximum exposure:

Two positions.

The allocator must never exceed configured capital/risk limits.

---

# 4. INITIAL UNIVERSES

Dual Momentum:

Use liquid sector/market ETFs.

Trend Following:

Initial candidate universe:

* NIFTYBEES
* JUNIORBEES
* GOLDBEES
* SILVERBEES
* SETF10GILT

The exact final universe must be configurable.

Mean Reversion:

Initial universe:

Point-in-time NIFTY 50 constituents.

PEAD:

Initial universe:

NIFTY 200 with liquidity/turnover filtering.

IMPORTANT:

Universe membership must eventually be point-in-time aware.

Do NOT use today's constituents to backtest historical periods.

---

# 5. MARKET DATA

Historical daily data:

Primary source:

NSE Bhavcopy / UDiFF daily market data.

Storage:

DuckDB + Parquet.

Raw data:

data/raw/

Processed data:

data/processed/

Parquet:

data/parquet/

Database:

data/forge_tl.duckdb

The data pipeline must be deterministic and idempotent.

Running the same ingestion twice must not create duplicate records.

---

# 6. CANONICAL BAR SCHEMA

Canonical market bars must contain at minimum:

timestamp
symbol
open
high
low
close
volume

Additional metadata may be retained when genuinely useful, but do not expand the canonical schema unnecessarily.

Data normalization must tolerate reasonable source-column naming differences.

Data validation must reject:

* missing required fields
* invalid timestamps
* non-numeric OHLCV
* negative prices
* negative volume
* impossible OHLC relationships

Do not silently repair bad financial data unless the repair rule is explicit and tested.

---

# 7. NSE INGESTION

The NSE ingestion layer must:

1. Download the appropriate daily market file.
2. Store the raw archive.
3. Read the UDiFF format.
4. Identify relevant cash-market instruments.
5. Normalize into canonical bars.
6. Validate the data.
7. Write to DuckDB.
8. Optionally export canonical Parquet.
9. Remain idempotent.

NSE source-specific logic must remain isolated from generic data normalization.

Do not make the entire data layer NSE-specific.

---

# 8. HISTORICAL DATA DESIGN

Historical data must support:

* daily bars
* symbol-level queries
* date-range queries
* universe filtering
* strategy backtesting

Eventually support:

* point-in-time universes
* corporate actions
* delistings
* symbol changes

Do not implement advanced corporate-action infrastructure before it is actually required by the next accepted strategy.

---

# 9. BACKTEST ENGINE

The backtest engine must be event/order based rather than a simplistic vectorized return calculator.

At minimum it must model:

Signal
→ order
→ fill
→ position
→ portfolio
→ costs
→ equity curve

The engine must prevent look-ahead bias.

A signal generated using information available at time T must not use information from T+1 or later.

Execution timing must be explicit.

Initial target execution model:

Signal:

15:15

Risk calculation:

15:18

Order:

15:20

Order timeout:

15:25

Unfilled order:

cancel.

Partial fills:

must update position and risk.

These times are initial configuration, not hardcoded assumptions.

---

# 10. COST MODEL

Costs must be modeled component-by-component.

Do not use one unexplained "transaction cost %" number.

Model separately where applicable:

* brokerage
* STT
* exchange transaction charges
* SEBI charges
* stamp duty
* GST
* DP charges
* slippage

The cost model must be configurable.

Backtests must report:

gross P&L
total costs
net P&L

A strategy that only works before realistic costs should not pass.

---

# 11. SLIPPAGE

Initial assumptions:

ETF:

0.05%

NIFTY equity:

0.10%

These are initial research assumptions only.

Slippage must be configurable.

The system should eventually support sensitivity testing.

---

# 12. STRATEGY INTERFACE

Each strategy should expose a small, common interface.

Conceptually:

input market data
→ calculate indicators/features
→ generate signal
→ return desired action/target

The strategy should NOT directly:

* place broker orders
* modify account state
* manage database connections
* send Telegram messages

Strategy logic must remain separate from execution.

---

# 13. POSITION SIZING

Initial risk budget:

1% of portfolio capital per trade.

At ₹50,000:

₹500.

Position sizing must account for:

* entry price
* stop distance
* risk budget
* available capital
* minimum practical order size
* configured position limits

Never allow position sizing to exceed available capital.

---

# 14. RISK ENGINE

The risk layer must be able to enforce:

* maximum position count
* maximum capital exposure
* maximum per-trade risk
* maximum portfolio drawdown
* strategy eligibility
* regime restrictions
* circuit breaker

Risk checks must happen BEFORE live order submission.

---

# 15. REGIME FILTER

Initial regime model:

Bull:

Nifty > 200 EMA
AND
VIX <= 16.5

Neutral:

Nifty > 200 EMA
AND
VIX between 16.5 and 19

OR

Nifty < 200 EMA
AND
VIX <= 16.5

Bear:

Nifty < 200 EMA

OR

VIX > 19

Initial policy:

Bull:
all eligible strategies allowed.

Neutral:
restricted strategy participation.

Bear:
100% defensive.

All thresholds must be configuration values.

Do not hardcode them inside strategy code.

---

# 16. PAPER TRADING

Before live deployment:

Minimum paper trading period:

60 trading sessions.

Acceptance goals:

* zero crashes
* correct order lifecycle
* correct position accounting
* correct P&L
* drawdown below 4%
* observed slippage reasonably consistent with model

Paper trading must use the same strategy/risk/portfolio code intended for live trading wherever practical.

Only the execution adapter should differ.

---

# 17. LIVE EXECUTION

Initial broker:

Dhan.

Broker integration must be isolated behind a broker interface.

The strategy layer must not know whether execution is Dhan, paper, or another broker.

Initial execution sequence:

signal
→ risk validation
→ order creation
→ broker submission
→ order status
→ fill
→ portfolio update

Order states must be explicitly handled.

At minimum:

PENDING
TRANSIT
TRADED
PARTIAL
REJECTED
CANCELLED
EXPIRED

Do not assume that an order submitted successfully means it was filled.

---

# 18. DATABASE

Use DuckDB.

Avoid introducing PostgreSQL, Redis, Kafka, or other infrastructure during the initial project.

Database responsibilities:

* market data
* trades
* orders
* positions
* portfolio snapshots
* backtest results where useful

The database must support deterministic queries.

---

# 19. FILE STORAGE

Keep the repository small.

Preferred initial structure:

forge_TL/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docs/
│   └── FORGE_TL_MASTER_SPEC.md
├── src/
│   └── forge_tl/
│       ├── **init**.py
│       ├── **main**.py
│       ├── core.py
│       ├── data.py
│       └── backtest.py
├── tests/
└── data/
├── raw/
├── processed/
└── parquet/

This is a starting structure, not a requirement to create empty files.

Create a new module only when separation materially improves correctness or maintainability.

---

# 20. CONFIGURATION

Configuration must be externalized.

Use environment/configuration files for:

* broker credentials
* database path
* capital
* risk limits
* strategy parameters
* slippage
* execution settings

Never hardcode API credentials.

Never commit secrets.

---

# 21. LOGGING

The system must produce useful logs for:

* ingestion
* validation failures
* signals
* orders
* fills
* risk rejection
* exceptions

Logs must be concise and useful for debugging.

Do not build an elaborate observability platform.

---

# 22. TESTING PHILOSOPHY

Every layer must have tests.

Tests should focus on:

* deterministic behavior
* edge cases
* financial correctness
* idempotency
* failure handling

Important examples:

Same input twice:

same result.

Invalid market data:

rejected.

Insufficient capital:

order rejected.

Risk limit exceeded:

order rejected.

Unfilled order:

position remains unchanged.

Partial fill:

position reflects actual filled quantity.

---

# 23. BACKTEST VALIDATION

Initial research split:

In-sample:

2016–2021

Out-of-sample:

2022–2024

Paper trading:

60 sessions.

Walk-forward:

24-month rolling training window
stepped every 6 months.

Parameter robustness:

±15% parameter plateau where applicable.

Minimum target:

100 closed trades where the strategy's trading frequency makes this statistically practical.

Do not force 100 trades onto inherently low-frequency strategies if doing so would distort the strategy.

---

# 24. STRATEGY ACCEPTANCE SCORECARD

Initial target thresholds:

Sharpe >= 1.10

Sortino >= 1.40

Maximum drawdown <= 12%

Profit Factor >= 1.45

OOS Sharpe retention >= 70% of IS Sharpe

Expectancy >= +0.30R

These are research acceptance thresholds, not promises of profitability.

A strategy failing multiple rejection criteria must not enter the live strategy pool.

---

# 25. WALK-FORWARD / ROBUSTNESS

Do not optimize for one historical period.

A strategy should demonstrate:

* stable behavior across periods
* reasonable parameter robustness
* acceptable OOS degradation
* realistic transaction costs
* no obvious look-ahead bias
* no obvious survivorship bias

Do not select a strategy because it has the highest backtest return.

---

# 26. CIRCUIT BREAKER

Hard portfolio drawdown circuit breaker:

10%.

If breached:

1. stop new entries
2. move system to safe state
3. liquidate according to predefined policy where appropriate
4. stop live strategy execution
5. revert to paper/research mode
6. require manual review

Do not automatically resume live trading after a hard circuit breaker.

---

# 27. DEVELOPMENT STAGES

Stage 0:

Foundation

Stage 1:

Market data

Stage 2:

Historical storage / Parquet

Stage 3:

Backtest engine

Stage 4:

Dual Momentum

Stage 5:

Trend Following

Stage 6:

Mean Reversion

Stage 7:

PEAD

Stage 8:

Portfolio allocator

Stage 9:

Paper trading

Stage 10:

Broker integration

Stage 11:

Live deployment

Do not skip directly to live trading.

---

# 28. DEVELOPMENT RULES

RULE 1:

Correctness over speed.

RULE 2:

Minimal files.

RULE 3:

No unnecessary abstractions.

RULE 4:

No feature should be implemented merely because it is common in other trading frameworks.

RULE 5:

Do not copy Freqtrade or other frameworks.

RULE 6:

Do not introduce dependencies unless justified.

RULE 7:

Do not silently change accepted architecture.

RULE 8:

Do not modify an accepted layer unless a genuine regression or dependency requires it.

RULE 9:

Every completed task must have executable tests.

RULE 10:

Every task must produce an implementation report.

---

# 29. ANTIGRAVITY WORKFLOW

Antigravity is the implementation agent.

For each task:

1. Read this specification.
2. Inspect the current repository.
3. Identify existing accepted functionality.
4. Implement only the requested task.
5. Run tests.
6. Fix implementation errors locally.
7. Re-run tests.
8. Produce an implementation report.

Do not ask the user to manually fix obvious implementation errors before attempting to diagnose them.

Do not repeatedly loop on an ambiguous problem.

If requirements conflict or the implementation cannot proceed safely:

STOP.

State:

"BLOCKED — clarification required"

and explain exactly what information is missing.

---

# 30. IMPLEMENTATION REPORT

Every task must finish with:

IMPLEMENTATION REPORT

Task: <task name>

Status:
PASS / PARTIAL / BLOCKED

Files added:
...

Files changed:
...

Tests executed:
...

Test results:
...

Acceptance criteria:

[PASS] ...
[PASS] ...
[FAIL] ...

Known limitations:
...

Architecture changes:
...

Potential risks:
...

Do not claim PASS when an acceptance criterion is failing.

---

# 31. FIRST PRINCIPLE

FORGE_TL is a trading research and execution system.

The most dangerous bugs are not syntax errors.

The most dangerous bugs are:

* look-ahead bias
* survivorship bias
* unrealistic fills
* incorrect costs
* incorrect position accounting
* incorrect risk calculation
* data leakage
* overfitting
* accidental leverage
* duplicate orders
* incorrect broker state handling

The project must prioritize detecting these failures.

END OF MASTER SPEC
