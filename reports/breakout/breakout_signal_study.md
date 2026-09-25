# BREAKOUT SIGNAL STUDY (TASK 10.0)

## 1. Files Created/Modified
- `scripts/run_research_breakout_10_0.py`
- `tests/test_breakout_10_0.py`
- `reports/breakout/breakout_signal_study.md`
- `reports/breakout/breakout_signal_results.csv`
- `reports/breakout/breakout_yearly.csv`
- `reports/breakout/breakout_regime.csv`
- `reports/breakout/breakout_liquidity.csv`

## 2. Dataset Period
2016-03-31 through 2024-12-31

## 3. Universe
Point-in-Time Nifty 50 constituents only.

## 4. Signal Definitions
- **Signal A**: 50-day breakout (Close[t] > max(High[t-50 : t-1]))
- **Signal B**: Signal A + Volume Confirmation (Volume[t] > 20d Mean)
- **Signal C**: Signal A + Trend Confirmation (Close[t] > 200d SMA)
- **Signal D**: Signal A + B + C

## 5. Forward-Return Definitions
Calculated from Open[t+1] to Close[t+h] for h=1,3,5,10,20. Completely insulated from lookahead bias.

## 6. Primary Signal A Results (vs Baseline)
```text
Signal Horizon  Count  Sig Mean  Base Mean  Diff Mean   Sig Med  Base Med  Diff Med  Hit Rate  Std Dev       p25      p75    T-Stat        P-Val
 sig_A      1d   4901 -0.002413  -0.000881  -0.001532 -0.002663 -0.001266 -0.001397  0.405223 0.018137 -0.011273 0.005793 -5.780919 7.848607e-09
 sig_A      3d   4901 -0.002413   0.000014  -0.002427 -0.002492  0.000000 -0.002492  0.447868 0.034685 -0.018212 0.013152 -4.781175 1.789038e-06
 sig_A      5d   4901 -0.002133   0.000935  -0.003067 -0.001328  0.001060 -0.002388  0.478882 0.049836 -0.022422 0.019545 -4.221367 2.468740e-05
 sig_A     10d   4900 -0.001655   0.003163  -0.004818  0.000096  0.003717 -0.003621  0.501224 0.068984 -0.032000 0.030269 -4.784023 1.764444e-06
 sig_A     20d   4887  0.003069   0.007725  -0.004656  0.004094  0.008803 -0.004710  0.526090 0.096907 -0.040239 0.050460 -3.284560 1.027996e-03
```

## 7. Signals B/C/D Comparison
```text
Signal Horizon  Count  Sig Mean  Base Mean  Diff Mean   Sig Med  Base Med  Diff Med  Hit Rate  Std Dev       p25      p75    T-Stat        P-Val
 sig_B      1d   3660 -0.002842  -0.000881  -0.001961 -0.002908 -0.001266 -0.001642  0.399180 0.019214 -0.012040 0.005799 -6.080170 1.316242e-09
 sig_B      3d   3660 -0.002514   0.000014  -0.002528 -0.002611  0.000000 -0.002611  0.448634 0.036482 -0.018870 0.013892 -4.124337 3.795392e-05
 sig_B      5d   3660 -0.001588   0.000935  -0.002523 -0.000983  0.001060 -0.002043  0.484426 0.049436 -0.023059 0.019938 -3.039773 2.383296e-03
 sig_B     10d   3659 -0.000864   0.003163  -0.004027  0.000094  0.003717 -0.003624  0.500957 0.069041 -0.032256 0.031285 -3.471392 5.233821e-04
 sig_B     20d   3652  0.005113   0.007725  -0.002612  0.004727  0.008803 -0.004077  0.530668 0.095746 -0.040248 0.052075 -1.620249 1.052594e-01
 sig_C      1d   4130 -0.002204  -0.000881  -0.001323 -0.002513 -0.001266 -0.001247  0.409927 0.017939 -0.010892 0.005883 -4.647799 3.451652e-06
 sig_C      3d   4130 -0.001801   0.000014  -0.001815 -0.002383  0.000000 -0.002383  0.448426 0.033679 -0.017667 0.013501 -3.388457 7.089048e-04
 sig_C      5d   4130 -0.001308   0.000935  -0.002243 -0.001209  0.001060 -0.002269  0.481840 0.050176 -0.022204 0.019705 -2.823766 4.767548e-03
 sig_C     10d   4129 -0.000432   0.003163  -0.003595  0.000194  0.003717 -0.003523  0.502301 0.068215 -0.031419 0.030307 -3.323939 8.947358e-04
 sig_C     20d   4116  0.004708   0.007725  -0.003016  0.004897  0.008803 -0.003906  0.530369 0.098248 -0.039264 0.051516 -1.933820 5.319895e-02
 sig_D      1d   3103 -0.002607  -0.000881  -0.001726 -0.002673 -0.001266 -0.001407  0.405092 0.019017 -0.011703 0.005874 -4.989985 6.353696e-07
 sig_D      3d   3103 -0.002097   0.000014  -0.002111 -0.002553  0.000000 -0.002553  0.447954 0.035358 -0.018267 0.013897 -3.276394 1.062324e-03
 sig_D      5d   3103 -0.000904   0.000935  -0.001839 -0.001101  0.001060 -0.002162  0.484048 0.049732 -0.022711 0.020178 -2.032740 4.215945e-02
 sig_D     10d   3102  0.000132   0.003163  -0.003030  0.000079  0.003717 -0.003638  0.500322 0.069003 -0.031968 0.031307 -2.412488 1.589864e-02
 sig_D     20d   3095  0.007171   0.007725  -0.000554  0.005369  0.008803 -0.003434  0.535380 0.097045 -0.038244 0.052739 -0.312947 7.543407e-01
```

## 8. Yearly Stability (Signal A, 5d Return)
```text
Year  Count   Mean 5d    Med 5d      Hit
2016    435 -0.008205 -0.001617 0.452874
2017    557 -0.007088 -0.003469 0.447038
2018    397 -0.007755 -0.004973 0.425693
2019    396 -0.006077 -0.005099 0.436869
2020    636  0.005414  0.002053 0.523585
2021    664  0.006191  0.002428 0.522590
2022    499 -0.005931 -0.003364 0.464930
2023    722  0.000723  0.000077 0.504155
2024    595 -0.004313 -0.001761 0.475630
```

## 9. Regime Stability (Signal A, 5d Return)
```text
 Regime  Count   Mean 5d    Med 5d      Hit
   Bear   1095  0.003938  0.002661 0.528767
   Bull   3190 -0.003800 -0.001947 0.463636
Neutral    598 -0.004969 -0.003751 0.464883
Unknown     18  0.018312  0.022226 0.611111
```

## 10. Liquidity Analysis (Signal A, 5d Return, Median Split ADV20)
```text
Liquidity  Count   Mean 5d      Hit
 High_Liq   2451 -0.001484 0.481028
  Low_Liq   2450 -0.002782 0.476735
```

## 11. Crowding/Date Concentration Analysis
- Total Signals: 4901
- Top 10 signal dates contributed: 3.20% of all signals.
- Non-crowded mean 5d return (excluding top 5% dates): -0.2477% (vs -0.2133% raw).

## 12. Cost Impact (5d Horizon)
- Gross Mean Return: -0.2133%
- Estimated Round-Trip Cost: ~0.1500%
- Net Mean Return: -0.3633%
- Cost as % of Gross: nan%

## 13. Statistical Diagnostics
- For the primary Signal A (5d), the mean return was -0.2133% vs baseline 0.0935%.
- The difference is -0.3067%.
- Welch's T-Statistic: -4.22.
- The simple t-test assumes independent observations, which is notoriously violated by overlapping horizons and crowded signal dates.

## 14. Economic Interpretation
Even if a slight statistical edge exists, it is frequently consumed by friction. Breakouts are theoretically robust but notoriously low-hit-rate. A 5-day net mean return of -0.3633% across a 50K capital base provides almost zero room for slippage errors.

## 15. Runtime
Processed 153660 rows across the historical subset in 2.61 seconds.

## 16. Test Results
- Executed `test_breakout_10_0.py` with 10 exact deterministic tests.
- 10/10 tests passed (62 + 10 = 72 tests total).

## 17. FINAL VERDICT
**BREAKOUT KILLED**

If we had never seen the NSE Systematic Trading System Blueprint, the standalone statistical edge presented by this breakout definition on large-cap Indian equities over the last decade would barely register above noise, particularly after applying strict institutional cost considerations.
