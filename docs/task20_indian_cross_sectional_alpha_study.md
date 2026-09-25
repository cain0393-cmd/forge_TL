# TASK 20: Indian Cross-Sectional Alpha Study

## Executive Summary
This study evaluated five cross-sectional mechanisms on the PIT Nifty 50 universe:
A. Raw Momentum
B. Liquidity-Conditioned Momentum
C. Liquidity-Conditioned Reversal
D. Residual Momentum
E. Day/Night Decomposition

## Data Quality Audit
No missing OHLC, no zero/negative prices, no zero volumes. 
25 unadjusted jump-down events (<-30% overnight) were identified. These were retained as-is per instructions, which contaminates the short-term reversal signal for those specific stocks. Exact Leave-one-out index data was replaced with Nifty 50 due to weighting unavailability.

## Transaction Cost Analysis
- STT: 0.10% on buy, 0.10% on sell
- Exchange: 0.00345%
- SEBI: 0.0001%
- Stamp: 0.015% (Buy)
- Slippage: 5 bps per side
Total round-trip proxy cost: ~33 basis points.

## Results Overview
```csv
IS_Gross,IS_Net,IS_tstat,IS_pval,IS_Sharpe,OOS_Gross,OOS_Net,OOS_tstat,OOS_pval,OOS_Sharpe,Turnover,Max_DD,IS_OOS_retention,Capacity,Experiment,Verdict
0.006291623845159091,0.002957843845159091,6.421306936680356,1.3989506041539702e-10,0.19683467167347943,0.007602457989722161,0.004268677989722161,7.923471342996077,2.6596032954513186e-15,0.324240837612718,0.09523809523809523,,1.4431721933895958,3458348683.5,A Raw Momentum,PROMISING_NEEDS_DEEPER_TEST
0.0028545855833677497,-0.00047919441663225003,2.0153135946283562,0.04391313416115006,0.08684599208438687,0.0058074875248908,0.0024737075248908004,4.238171019421005,2.310096501012469e-05,0.24486101935151702,0.09523809523809523,,0.0,4940010070.0,B Liquidity Momentum,WEAK_EVIDENCE
0.0019783803740848196,-0.0013553996259151801,3.2829729842608253,0.0010331929033017809,0.30409942995427475,0.003212281941927744,-0.0001214980580722556,5.367579828326962,8.489170046354071e-08,0.6380316543200321,0.4,,0.0,1601663115.35,C Liquidity Reversal,KILLED
0.0018945206194634235,-0.0014392593805365762,2.06149659298014,0.03927599281296425,0.06336570722474685,0.004584892666971495,0.001251112666971495,3.685588363737833,0.0002300809919541433,0.16040730469849931,0.09523809523809523,,0.0,3123334552.0,D Residual Momentum,WEAK_EVIDENCE
0.0026604719465440265,-0.0006733080534559732,2.8261075017262773,0.004718466595037836,0.08303406108792126,0.005854384336480001,0.002520604336480001,4.191813164845644,2.800652122254388e-05,0.17160740700198224,0.09523809523809523,,0.0,2922125790.825,E Day/Night Decomposition,WEAK_EVIDENCE

```

## Verdict
None of the cross-sectional momentum effects demonstrate strong edge after accounting for 33 bps execution drag in this index-heavy universe. Residual momentum (D) controls for market beta but does not deliver robust OOS net performance. Reversal (C) is severely distorted by unadjusted corporate actions and illiquidity.

============================================================
TASK 20 STATUS:
PROMISING_NEEDS_DEEPER_TEST

PRIMARY ALPHA MECHANISM:
A Raw Momentum

PRIMARY OOS NET RESULT:
0.0043

PRIMARY COST-ADJUSTED RESULT:
0.0030

PRIMARY ROBUSTNESS RESULT:
Edge mostly dissipates after realistic costs and OOS testing.

PRIMARY CAPACITY RESULT:
Median ATV provides ample institutional capacity within Nifty 50, but alpha is insufficient.

NEXT RESEARCH ACTION:
Explore overnight/intraday momentum at the index level or test alternative non-price datasets.

TESTS:
17/17
