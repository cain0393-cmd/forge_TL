# DELIVERY SIGNAL STUDY (TASK 9.1)

## 1. Files Created
- `scripts/run_research_delivery_9_1.py`
- `tests/test_delivery_signals.py`
- `reports/delivery/delivery_signal_report.md`
- `reports/delivery/delivery_quantile_results.csv`
- `reports/delivery/delivery_bucket_results.csv`
- `reports/delivery/delivery_yearly_results.csv`
- `reports/delivery/delivery_regime_results.csv`
- `reports/delivery/delivery_liquidity_results.csv`

## 2. Dataset Period
2016-03-31 through 2024-12-31

## 3. Universe
Strict Point-in-Time Nifty 50 Universe to avoid survivorship bias.
Total unique symbols evaluated over the entire period: 76

## 4. Signal Definitions
- **Signal A**: Absolute delivery percentage.
- **Signal B**: High delivery threshold groups (>60%, >70%, etc.).
- **Signal C**: Abnormal delivery percentage (Current - 20d/60d Rolling Mean).
- **Signal D**: Abnormal delivery volume (Current / 20d Rolling Mean).
- **Signal E**: Abnormal traded volume (Current / 20d Rolling Mean).
*Note: Rolling baselines strictly exclude the day `t` observation.*

## 5. Forward-Return Definitions
To enforce realistic trading constraints, signals observed after market close on day `t` are executed at the Open on day `t+1`. 
Returns are defined as: `Close[t+h] / Open[t+1] - 1` for horizons `h` = 1, 3, 5, 10, 20.

## 6. Overall Results
Delivery percentage demonstrates zero predictive power over the Nifty 50 universe. 

Across absolute buckets, abnormal spikes, and volume ratios, the Q5 minus Q1 spreads are economically insignificant (often < 0.05% over 5 days) and statistically indistinguishable from zero noise.

For instance, looking at 5-day returns across absolute delivery buckets (Signal A):
- 20-30%: 0.1498%
- 50-60%: 0.0362%
- 80-90%: 0.0536%
There is no monotonic relationship.

## 7. Horizon Results & 8. Quantile Results
Looking at Abnormal Delivery Percentage (Signal C, 20-day) Q5 (highest abnormal delivery) vs Q1:
- 1d Mean: Q1 = -0.1144%, Q5 = -0.0780%
- 5d Mean: Q1 = 0.0195%, Q5 = 0.0281%
Spread is negligible and not monotonically ordered.

## 9. Yearly Stability (Signal C 5d Spread)
```text
Year     Q1_5d     Q5_5d  Spread (Q5-Q1)
2016  0.001118  0.000905       -0.000213
2017  0.000790  0.000011       -0.000779
2018 -0.003972 -0.002708        0.001264
2019 -0.001291 -0.002005       -0.000714
2020  0.002048 -0.000203       -0.002250
2021  0.002152  0.002043       -0.000109
2022 -0.000939  0.001520        0.002459
2023  0.001967  0.003884        0.001917
2024  0.000432 -0.000579       -0.001011
```
The spread flips randomly between positive and negative years.

## 10. Regime Stability (Signal C 5d Spread)
```text
 Regime     Q1_5d     Q5_5d  Spread (Q5-Q1)
   Bear  0.002611  0.002139       -0.000473
   Bull -0.000440 -0.000302        0.000138
Neutral -0.003365 -0.002027        0.001338
Unknown  0.008281  0.005316       -0.002964
```
No clear edge in any regime.

## 11. Liquidity Analysis (Signal C 5d Spread)
```text
Liquidity     Q1_5d     Q5_5d  Spread (Q5-Q1)
      Low  0.000454  0.000418       -0.000036
      Med  0.000558  0.000931        0.000373
     High -0.000487 -0.000506       -0.000019
```
Even splitting the Nifty 50 universe by daily turnover does not reveal a hidden delivery edge.

## 12. Statistical Evidence
T-statistics across essentially all Q5 and Q1 bucket returns for 1d and 5d horizons fail to reach significance levels once adjusted for the overlapping cross-sectional variance. Even taken raw, t-stats hover between -0.5 and 1.2, implying purely random drift.

## 13. Multiple-Testing Considerations
Despite testing dozens of combinations (A/B/C/D/E, 1d/3d/5d/10d/20d, buckets, quantiles, regimes), not a single combination produced a robust t-stat > 2.5 with a monotonic quantile relationship. This strongly confirms the absence of an edge.

## 14. Important Confounders
- Correlation of Delivery % to Absolute Intraday Volatility: -0.114
- Correlation of Delivery % to Turnover: -0.105
Delivery percentage shows slight negative correlation with volatility, suggesting less volatile days have marginally higher delivery proportions, but this does not translate to directional predictive power.

## 15. Runtime
- Approximately 21.96 seconds using vectorized Pandas and DuckDB-accelerated Parquet reads.

## 16. Test Results
- Added `test_delivery_signals.py` to assert correct rolling baselines (excluding t), correct forward open/close logic, and deterministic calculations.
- Baseline of 62 + new tests passed.

## 17. Limitations
- Restricted purely to the Nifty 50 large-cap universe. It is possible (though highly debatable) that delivery signals work on highly illiquid micro-caps, but for institutional large-cap trading, the signal is dead.

## 18. Final Verdict: NO EVIDENCE
There is absolutely **NO EVIDENCE** that historical delivery percentages or abnormal delivery volumes hold predictive power over the Nifty 50 universe. The relationship is pure noise. Proceeding to strategy construction (Task 9.2) with this signal would lead to aggressive curve-fitting and inevitable failure.

**Verdict**: NO EVIDENCE.
