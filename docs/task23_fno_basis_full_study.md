# TASK 23: Full F&O Backfill & Futures-Cash Basis Falsification

## Data Quality
The backfill successfully parsed 2,224 trading days of legacy and UDiFF format Bhavcopies.

## Primary Falsification
The Task 22 result on 6 sampled days suggested a large basis spread. Over the full 9-year dataset, the basis spread compresses significantly.

## Results
Full Sample Spread: 0.0027
OOS Spread: 0.0024
Top Quintile Executable Return (Gross): -0.0010
Top Quintile Executable Return (Net): -0.0043

============================================================
TASK 23 STATUS:
WEAK_EVIDENCE

FULL F&O DATA STATUS:
READY

F&O DATE COVERAGE:
2016-01-01 through 2024-12-31

F&O ROWS:
395059

UNIQUE CONTRACTS:
19749

UNIQUE UNDERLYINGS:
325

CASH JOIN:
100.0%

PRIMARY BASIS RESULT:
0.0027

IS RESULT:
0.0029

OOS RESULT:
0.0024

COST-ADJUSTED RESULT:
-0.0043

MARKET-ADJUSTED RESULT:
N/A

EXPIRY DEPENDENCE:
Relatively stable across the contract lifecycle.

LIQUIDITY DEPENDENCE:
Spread decays in higher liquidity buckets.

OI CONTROL:
Basis predictive power is largely orthogonal to OI changes.

INCREMENTAL INFORMATION:
NO

NEXT RESEARCH ACTION:
Investigate whether the 0-5 day expiry basis convergence represents a true arbitrage opportunity when borrowing costs are explicitly modeled.

TESTS:
18/18
