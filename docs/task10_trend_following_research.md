# TASK 10 TREND FOLLOWING RESEARCH REPORT

## 1. Executive Summary
This report presents the historical evaluation of the Multi-Asset Trend Following strategy. The strategy applies a simple 200-day Simple Moving Average (SMA) across a diverse 5-asset universe (Equity, Gold, Silver, Bonds) with equal allocation to eligible assets.
Despite successfully capturing the post-2021 bull run, the strategy's In-Sample (IS) performance suffered massive drawdowns due to structural whipsaws and the delayed availability of diversification assets like `SETF10GILT` and `SILVERBEES`. 
With an IS Sharpe Ratio of 0.34 and a Max Drawdown of 55.90%, the strategy fails the project's strict acceptance criteria. The final verdict is **FAIL**.

## 2. Frozen Strategy Specification
- **Strategy**: Multi-Asset Trend Following
- **Signal**: `Close > SMA200`
- **Sizing**: Equal-weight across eligible assets (`1 / N`). 100% cash if no assets are eligible.
- **Constraints**: No leverage, no shorting, no volatility scaling.

## 3. Universe
- `NIFTYBEES`
- `JUNIORBEES`
- `GOLDBEES`
- `SILVERBEES`
- `SETF10GILT`

## 4. ETF Historical Availability
The system correctly enforces the 200-day warmup requirement. ETFs only become tradable *after* 200 valid observations exist. No prices were fabricated or forward-filled.

- **NIFTYBEES**: First Price: 2016-01-01 | 200th Obs: 2016-10-25
- **JUNIORBEES**: First Price: 2016-01-01 | 200th Obs: 2016-10-25
- **GOLDBEES**: First Price: 2016-01-01 | 200th Obs: 2016-10-25
- **SILVERBEES**: First Price: 2022-05-10 | 200th Obs: 2023-02-22
- **SETF10GILT**: First Price: 2016-06-23 | 200th Obs: 2018-07-13

## 5. SMA Method
A strict 200-day Simple Moving Average is used. Partial SMAs were disallowed, ensuring no signals were generated before an asset matured past 200 trading days.

## 6. Warmup Handling
During the first ~10 months of 2016, the strategy correctly remained 100% in cash as `NIFTYBEES`, `JUNIORBEES`, and `GOLDBEES` warmed up. `SETF10GILT` joined in mid-2018, and `SILVERBEES` only contributed to the OOS period starting in early 2023.

## 7. Execution Model
Orders are submitted at the end of the bar (`t`) and execute on the next eligible trading bar (`t+1`), strictly preventing same-bar lookahead bias.

## 8. Cost Model
Full `BacktestEngine` costs (brokerage, STT, exchange charges, SEBI fee, stamp duty, GST, DP charges, and slippage) were subtracted. All metrics reflect net performance.

## 9. IS Results (2016 - 2021)
- **Total Return**: 29.39%
- **Max Drawdown**: -55.90%
- **Sharpe Ratio**: 0.34
- **Sortino Ratio**: 0.39
- **Number of Trades**: 456
- **Win Rate**: 74.34%
- **Profit Factor**: 1.25
- **Expectancy**: 68.82 INR

## 10. OOS Results (2022 - 2024)
- **Total Return**: 42.12%
- **Max Drawdown**: -6.55%
- **Sharpe Ratio**: 1.70
- **Sortino Ratio**: 2.56
- **Number of Trades**: 393
- **Win Rate**: 95.67%
- **Profit Factor**: 12.47
- **Expectancy**: 104.96 INR

## 11. Combined Results (2016 - 2024)
- **Total Return**: 79.72%
- **Max Drawdown**: -55.90%
- **Sharpe Ratio**: 0.45
- **Sortino Ratio**: 0.51
- **Number of Trades**: 1010
- **Win Rate**: 83.47%
- **Profit Factor**: 1.53
- **Expectancy**: 78.13 INR

## 12. Portfolio Exposure Analysis
The strategy dynamically shifted from 0 to 5 holdings based on trends. Heavy churning (456 IS trades, 393 OOS trades) occurred around the SMA line, exposing the portfolio to severe whipsaws during range-bound regimes (e.g., COVID-19 crash and recovery).

## 13. Asset-Level Exposure
`NIFTYBEES`, `JUNIORBEES`, and `GOLDBEES` dominated the IS period, while `SILVERBEES` and `SETF10GILT` provided critical diversification in the OOS period, heavily influencing the OOS performance surge.

## 14. Cash Analysis
The strategy effectively fled to cash during sharp market corrections. However, lagging SMA whipsaws often caused it to sell near bottoms and buy near local tops during the volatile 2020 period.

## 15. Drawdown Analysis
The 55.90% Max Drawdown in the IS period severely breaches the 12% limit. This indicates the 200-day SMA on an equal-weight basket without volatility scaling or risk parity is structurally too slow to prevent massive capital destruction during rapid market shocks.

## 16. Cost Analysis
The sheer volume of trades (1010 total) due to daily rebalancing around the SMA line generated massive transaction costs and slippage, eroding gross returns.

## 17. Lookahead Audit
The backtest logic separates signal calculation (`t`) from order eligibility. Execution purely happens at `ts > order.created_at`. 

## 18. Determinism Audit
Duplicate research runs generated strictly identical outcomes across IS, OOS, and Combined contexts (100% match on Final Equity, Max DD, Trades, Sharpe).

## 19. Runtime
Total rows processed: 8,960. The execution optimized data loading by filtering to the 5 symbols, completing the dual-pass validation almost instantly.

## 20. Acceptance Criteria
| Metric | Target | IS | OOS | Pass/Fail |
|--------|--------|----|-----|-----------|
| Sharpe | >= 1.10 | 0.34 | 1.70 | **FAIL** (IS missed) |
| Sortino | >= 1.40 | 0.39 | 2.56 | **FAIL** (IS missed) |
| Max Drawdown | <= 12.0% | 55.90% | 6.55% | **FAIL** (IS missed) |
| Profit Factor | >= 1.45 | 1.25 | 12.47 | **FAIL** (IS missed) |
| Expectancy | >= +0.30R | 68.82 INR | 104.96 INR | **FAIL** (Net low IS) |
| OOS Sharpe Ret. | >= 70% of IS | N/A | 500% | **PASS** |
| Trades >= 100 | >= 100 | 456 | 393 | **PASS** |

## 21. Final Verdict
The system correctly implemented the Multi-Asset Trend Following rules over the prescribed universe. The strategy failed the In-Sample performance thresholds comprehensively due to structural whipsaws and unmanaged volatility, resulting in a 55.90% Max Drawdown.
**FINAL VERDICT: FAIL**
