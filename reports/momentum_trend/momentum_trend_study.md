# MULTI-ASSET TREND & DUAL MOMENTUM STUDY (TASK 11.0)

## DUAL MOMENTUM
-------------
Primary result (Top 3 Eligible, 21d Horizon): 0.6738%
Baseline (Unconditional 21d): 0.8599%
Excess return: -0.1861%
Top1-minus-Bottom1 (21d): -0.2045%
Cost-adjusted result (Net 21d): 0.5238%
Year stability:
```text
Year  Count   Mean 5d  Mean 21d  Mean 63d  Hit 21d
2017    341  0.002325  0.015998  0.055247 0.630499
2018    287  0.000277 -0.010310 -0.015095 0.554007
2019    271 -0.012866 -0.066606 -0.191132 0.416974
2020    308  0.001025  0.032644  0.111632 0.727273
2021    334 -0.004493  0.011347  0.026213 0.592814
2022    290 -0.002781 -0.008636 -0.000342 0.427586
2023    489  0.002580  0.024747  0.098526 0.730061
2024    629 -0.000960  0.020207  0.062542 0.629571
```
Regime stability:
```text
 Regime  Count   Mean 5d  Mean 21d  Mean 63d  Hit 21d
   Bear    621  0.001978  0.027287  0.072772 0.681159
   Bull   2032 -0.001853  0.001871  0.024123 0.598425
Neutral    291 -0.004703 -0.003622 -0.017507 0.491409
Unknown      5 -0.006700  0.018360  0.055504 0.800000
```
Statistical Diagnostic (Welch's T-Test Top3 vs Baseline 21d):
T-Stat: -0.90, P-Value: 0.3671
(Note: Observations are overlapping and highly correlated cross-sectionally).

Economic viability:
With a net expected 21-day return of 0.5238%, scaling this on a 50K capital base yields minimal absolute profits while demanding monthly rebalancing turnover.

VERDICT: DUAL MOMENTUM KILLED


## MULTI-ASSET TREND
-----------------
Primary result (TREND_ON 63d Horizon): 0.4080%
Baseline (Unconditional 63d): 1.2743%
Excess return (ON vs Base): -0.8663%
TREND_ON - TREND_OFF (63d): -3.4321%
Cost-adjusted result (Net 63d approx): 0.2580%
Year stability:
```text
Year  Count   Mean 5d  Mean 21d  Mean 63d  Hit 63d
2016     84 -0.011719 -0.021371  0.060017 0.690476
2017    557  0.003186  0.019142  0.047623 0.852783
2018    568 -0.002146 -0.007303  0.003242 0.556338
2019    682 -0.011805 -0.049362 -0.151210 0.448680
2020    510 -0.011475 -0.004069  0.019771 0.594118
2021    747 -0.010694 -0.001132  0.020211 0.567604
2022    636 -0.006735 -0.010934 -0.013940 0.462264
2023   1062 -0.003228  0.005617  0.033457 0.723164
2024   1168 -0.001861  0.011479  0.047196 0.580479
```
Regime stability:
```text
 Regime  Count   Mean 5d  Mean 21d  Mean 63d  Hit 63d
   Bear   1418 -0.007524  0.002038  0.023122 0.610014
   Bull   3944 -0.003953 -0.004380  0.003497 0.617901
Neutral    636 -0.009198 -0.010225 -0.034995 0.490566
Unknown     16 -0.009101  0.001614  0.012734 0.500000
```
Asset Level Breakdown:
```text
     Asset  Total  ON Count  OFF Count    ON 63d  OFF 63d  Hit 63d (ON)
  GOLDBEES   2022      1319        703 -0.030267 0.031135      0.548143
JUNIORBEES   2022      1484        538  0.031083 0.045328      0.597709
 NIFTYBEES   2022      1605        417 -0.005780 0.040831      0.621184
SETF10GILT   1444      1214        230  0.016329 0.012365      0.691928
SILVERBEES    455       392         63  0.020910 0.144278      0.446429
```

Statistical Diagnostic (Welch's T-Test ON vs OFF 63d):
T-Stat: -10.82, P-Value: 0.0000

Portfolio Diagnostic (20% Target Weight Equal Alloc):
Approx Annualized Gross Return (1d compounded): 9.1444%

Economic viability:
Multi-Asset Trend on just 5 ETFs limits diversification and capital capacity. Given the modest long-term drift in gold/silver and bonds relative to equities, the 20% fixed weights drag performance heavily relative to simply holding NIFTYBEES.

VERDICT: MULTI-ASSET TREND KILLED

## LIQUIDITY ANALYSIS
-----------------
```text
     Asset     Mean ADV   Median ADV      P25 ADV      P75 ADV
  AUTOBEES 2.387577e+07  11441181.12 5.680035e+06 2.995882e+07
  BANKBEES 2.017668e+08 148509125.65 1.413355e+07 3.008917e+08
  GOLDBEES 1.624868e+08  98550254.88 3.830204e+07 2.004092e+08
 INFRABEES 3.609722e+06    495100.65 1.422825e+05 1.811511e+06
    ITBEES 1.963717e+08 147327494.03 9.319472e+07 2.276183e+08
JUNIORBEES 4.562587e+07  22677684.21 5.465042e+06 5.064631e+07
 NIFTYBEES 3.501608e+08 193079800.48 3.786702e+07 5.102524e+08
PHARMABEES 5.021005e+07  36752947.55 1.600417e+07 7.137755e+07
SETF10GILT 1.115016e+06     65130.96 1.030175e+04 7.617952e+05
SILVERBEES 2.778930e+08 150331315.94 7.296926e+07 3.876364e+08
```
As shown, these ETFs have highly variable traded value distributions. SILVERBEES and SETF10GILT are materially thinner than broad equity ETFs, meaning slippage on 50K allocations would likely erase any borderline edges.


## RESEARCH PRIORITY
-----------------
1. Both non-PEAD standalone indicator hypotheses have failed to demonstrate sufficient edge after robust institutional analysis.
2. Nifty 50 constituents and primary sector ETFs are highly efficient; simple historical price crossovers do not reliably overcome friction.
3. The PEAD / Institutional Flow branch should be prioritized next as it introduces exogenous fundamental data/event timestamps rather than price-derived indicators.

## FINAL CONCLUSION
----------------
Answer explicitly:
"If we had never seen the original strategy blueprint, would the historical evidence independently justify allocating another engineering cycle to either strategy?"

**NO.** Neither Cross-Sectional Dual Momentum nor Multi-Asset Trend following produced historically stable, economically actionable edges beyond basic market beta. Allocating further engineering effort to optimize thresholds or weights would be pure data snooping. Both are killed.
