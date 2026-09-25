# TASK 9 DUAL MOMENTUM RESEARCH REPORT

## 1. Executive Summary
This report presents the historical out-of-sample evaluation of the Cross-Sectional Dual Momentum strategy. The evaluation rigidly adheres to the predetermined sector ETF universe and simulated execution, without any look-ahead bias. 
The strategy achieved a Combined Sharpe of {COMB_SHARPE} and a Maximum Drawdown of {COMB_MAX_DD}%, leading to a final verdict of **{VERDICT}**.

## 2. Frozen Strategy Specification
- **Strategy**: Cross-Sectional Dual Momentum
- **Relative Momentum**: 252 trading bars
- **Absolute Momentum**: 21 trading bars (Must be > 0)
- **Rebalance**: Every 21 trading bars
- **Top N**: 3
- **Selection**: Ranked by descending relative momentum, filtered by absolute momentum > 0.
- **Position Sizing**: Equal weight (1/3 per selected asset). Remaining capital held in cash if < 3 qualify.

## 3. Universe
Frozen sector ETF universe:
- `BANKBEES`
- `ITBEES`
- `PHARMABEES`
- `FMCGBEES`
- `AUTOBEES`
- `INFRABEES`
*(MID150BEES is explicitly excluded)*

## 4. ETF Historical Availability
The ETF historical data confirms partial availability reflecting genuine historical launches:
- `BANKBEES`: Available from 2016-01-01
- `INFRABEES`: Available from 2016-01-01
- `ITBEES`: Available from 2022-05-10
- `PHARMABEES`: Available from 2022-05-10
- `AUTOBEES`: Available from 2022-05-10
- `FMCGBEES`: 0 historical rows. Missing completely in historical market data.

The system handles these correctly. Unavailable ETFs simply do not accumulate the 253 observations required for momentum evaluation and therefore are legitimately never selected during their unavailable periods.

## 5. Data Validation
- Integer share sizing ensures no fractional allocations.
- No historical forward-filling or fabrication of prices.
- The 2016-2024 timeframe is strictly preserved via DuckDB dataset boundaries.
- No substitute ETFs (e.g., FMCGIETF) were swapped in to replace FMCGBEES, maintaining the frozen parameters constraint.

## 6. Execution Model
- Uses `BacktestEngine`.
- No same-bar execution. Orders generated at the end of bar `t` are explicitly executed on the subsequent eligible bar `t+1` or later.
- Uses `MARKET` order logic.

## 7. Cost Model
- Integrated brokerage, STT, exchange charges, SEBI fee, stamp duty, GST, DP charges, and slippage.
- All returns, P&L, and metrics reflect NET performance after cost subtraction.

## 8. IS Results (2016 - 2021)
- **Total Return**: 5.46%
- **Max Drawdown**: -33.46%
- **Sharpe Ratio**: 0.15
- **Sortino Ratio**: 0.16
- **Number of Trades**: 48
- **Win Rate**: 75.00%
- **Profit Factor**: 1.13
- **Expectancy**: 113.80 INR

## 9. OOS Results (2022 - 2024)
- **Total Return**: 60.40%
- **Max Drawdown**: -7.41%
- **Sharpe Ratio**: 2.05
- **Sortino Ratio**: 3.15
- **Number of Trades**: 24
- **Win Rate**: 91.67%
- **Profit Factor**: 52.09
- **Expectancy**: 2446.62 INR

## 10. Combined Results (2016 - 2024)
- **Total Return**: 58.72%
- **Max Drawdown**: -33.46%
- **Sharpe Ratio**: 0.47
- **Sortino Ratio**: 0.54
- **Number of Trades**: 94
- **Win Rate**: 78.72%
- **Profit Factor**: 2.27
- **Expectancy**: 657.29 INR

## 11. Trade Statistics
Gross execution count achieved 94 total trades across rebalancing iterations. 

## 12. Selection Statistics
Since several ETFs launched late in the dataset (2022) and FMCGBEES was entirely missing, the universe of fully available ETFs satisfying the 253-day condition during the IS period was often 2 or fewer (primarily BANKBEES and INFRABEES). Consequently, the strategy regularly defaulted to heavy cash allocations.

## 13. Turnover
Rebalancing every 21 bars drove structural portfolio churn. However, limited universe availability restricted actionable allocations.

## 14. Cash Exposure
Significant cash exposure characterized the backtest due to restricted historical availability and the absolute momentum filter (>0) pushing capital to cash during drawdowns.

## 15. Drawdown Analysis
Maximum Drawdown stood at 33.46%. 

## 16. Cost Analysis
The high frequency of 21-bar rebalancing, albeit on a restricted subset of ETFs, subjected the portfolio to recurring execution slippage and fixed brokerage elements.

## 17. Lookahead Audit
The backtest logic separates signal calculation (`t`) from order eligibility. Execution purely happens at `ts > order.created_at`. No future prices were exposed during the momentum calculation.

## 18. Determinism Audit
Duplicate research runs generated strictly identical outcomes across IS, OOS, and Combined contexts (100% match on Final Equity, Max DD, Trades, Sharpe).

## 19. Runtime
Total rows processed: 3,589,588. The execution natively bypassed database reloads, processing at optimal speed.

## 20. Acceptance Criteria
| Metric | Target | IS | OOS | Pass/Fail |
|--------|--------|----|-----|-----------|
| Sharpe | >= 1.10 | 0.15 | 2.05 | **FAIL** (IS missed) |
| Sortino | >= 1.40 | 0.16 | 3.15 | **FAIL** (IS missed) |
| Max Drawdown | <= 12.0% | 33.46% | 7.41% | **FAIL** (IS missed) |
| Profit Factor | >= 1.45 | 1.13 | 52.09 | **FAIL** (IS missed) |
| Expectancy | >= +0.30R | 113.80 INR | 2446.62 INR | **FAIL** (Net low IS) |
| OOS Sharpe Ret. | >= 70% of IS | N/A | 1366% | **PASS** |
| Trades >= 100 | >= 100 | 48 | 24 | **FAIL** (Short of 100) |

## 21. Final Verdict
The system correctly implemented the Cross-Sectional Dual Momentum rules over the prescribed universe. However, structural limitations in ETF historical availability (severely constraining 2016-2021) combined with parameter rigidity exposed severe underperformance relative to predefined thresholds.
**FINAL VERDICT: FAIL**
