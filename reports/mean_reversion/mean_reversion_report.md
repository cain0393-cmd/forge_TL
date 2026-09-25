# MEAN REVERSION RESEARCH REPORT (TASK 7.2)

## 1. Files Created/Modified
- `scripts/run_research_mean_reversion_7_2.py`
- `reports/mean_reversion/mean_reversion_report.md`
- `reports/mean_reversion/mean_reversion_metrics.csv`
- `reports/mean_reversion/mean_reversion_yearly.csv`
- `reports/mean_reversion/mean_reversion_regime.csv`

## 2. Exact Research Command
```bash
python scripts/run_research_mean_reversion_7_2.py
```

## 3. Dataset Period Actually Used
2016-01-01 through 2024-12-31

## 4. IS Period
2016-01-01 through 2021-12-31

## 5. OOS Period
2022-01-01 through 2024-12-31

## 6. Universe Provider Used
`Nifty50UniverseProvider` (Point-in-time)

## 7. Strategy Parameters
- Returns window: 5 days
- Mean window: 20 days
- Entry Z-score: < -2.0
- Exit Z-score: > 0.0 or 5-day hold
- Max holdings: 5
- Capital: 50,000 INR
- Target per trade: ~500 INR (1%)

## 8. Cost/Slippage Assumptions
Included via `BacktestEngine` componentized cost model: Brokerage, STT, Exchange transaction charges, SEBI fee, Stamp duty, GST, DP charges, and slippage.

## 9. Runtime
- Backtest time: ~32.46s
- Processed rows: 3,589,588

## 10. IS Metrics
- Total Return: 36.96%
- Sharpe Ratio: 0.47
- Max Drawdown: 21.19%
- Profit Factor: 1.17
- Win Rate: 50.8%
- Trades: 786

## 11. OOS Metrics
- Total Return: 20.54%
- Sharpe Ratio: 0.76
- Max Drawdown: 8.73%
- Profit Factor: 1.26
- Win Rate: 52.8%
- Trades: 356

## 12. OOS Retention
- OOS Sharpe / IS Sharpe = 160%

## 13. Yearly Results
| Year | Return | Sharpe | Max DD | Trades | Win Rate | Profit Factor | Expectancy |
|------|--------|--------|--------|--------|----------|---------------|------------|
| 2016 | -7.01% | -0.43  | -9.2%  | 91     | 57.1%    | 0.81          | -37.89 INR |
| 2017 | 1.38%  | 0.17   | -3.6%  | 62     | 49.0%    | 1.02          | 3.24 INR   |
| 2018 | 2.95%  | 0.33   | -3.8%  | 131    | 52.6%    | 1.10          | 10.56 INR  |
| 2019 | -7.91% | -0.98  | -8.4%  | 101    | 47.5%    | 0.72          | -40.68 INR |
| 2020 | 17.77% | 1.14   | -21.1% | 144    | 58.3%    | 1.63          | 66.05 INR  |
| 2021 | 29.25% | 1.79   | -4.8%  | 132    | 50.3%    | 1.54          | 86.20 INR  |
| 2022 | -7.90% | -0.75  | -9.5%  | 122    | 48.3%    | 0.78          | -40.37 INR |
| 2023 | 12.19% | 1.59   | -3.7%  | 137    | 55.4%    | 1.44          | 49.03 INR  |
| 2024 | 11.31% | 1.19   | -2.2%  | 116    | 52.5%    | 1.45          | 75.41 INR  |

## 14. Regime Results
| Regime | Trades | Net PnL | Win Rate | Profit Factor | Expectancy |
|--------|--------|---------|----------|---------------|------------|
| Bull   | 734    | 14,063  | 51.7%    | 1.14          | 19.16 INR  |
| Neutral| 151    | -3,752  | 44.3%    | 0.88          | -24.84 INR |
| Bear   | 277    | 18,293  | 58.1%    | 1.53          | 66.04 INR  |

## 15. Trade Statistics
- Total combined trades: 1,162
- The strategy demonstrates extreme dependency on high-volatility bear environments. Only 277 out of 1,162 trades (23%) occurred in Bear regimes, yet they accounted for more than half (18,293 INR) of the net profits.
- Neutral regimes structurally bled capital.

## 16. Data/Lookahead Validation
- All signals are calculated on completed bars and explicitly filled on subsequent bars. Lookahead protection logic actively prevents same-bar fills.
- Only PIT Nifty 50 constituents were traded.

## 17. Determinism Validation
- The script performed an identical two-pass backtest.
- The determinism checks returned TRUE (matching trade counts, total returns, and equity curves).

## 18. Full Test Result
- Total Tests: 55 passed.
- Baseline maintained.

## 19. Failures/Anomalies
- IS Sharpe (0.47) and Max Drawdown (21.19%) violently breach the required baseline parameters (Sharpe >= 1.1, Max DD <= 12%).
- Expectancy falls woefully short of the +0.30R target. At 1% risk (~500 INR), expectancy was merely ~25 INR across the backtest (< 0.05R).
- The strategy's edge is highly fragmented, leaning overwhelmingly on a few high-volatility pockets (2020, 2021) and failing otherwise.

## 20. Final Verdict: KILL
The strategy completely misses its baseline acceptance criteria in both in-sample risk metrics (Max DD > 21%) and return metrics (Sharpe < 0.5). Performance is highly fragile, depending almost entirely on the pandemic volatility crash and subsequent bounce. The underlying edge demonstrates no durability across normalized market conditions. Re-tuning parameters risks extreme curve fitting. The Mean Reversion strategy branch should be safely archived.
