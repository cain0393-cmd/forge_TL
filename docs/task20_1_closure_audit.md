# TASK 20.1: Cross-Sectional Alpha Closure Audit

## 1. Market-Adjusted Alpha Analysis

### A. Raw Momentum (21d holding)
- **IS Excess Return:** -0.0057
- **IS Alpha:** -0.0063 (Beta: 1.05, t-stat: nan, p-val: nan)
- **IS Info Ratio:** -0.16
- **OOS Excess Return:** -0.0013
- **OOS Alpha:** -0.0006 (Beta: 0.90, t-stat: nan, p-val: nan)

*Verdict*: No market-adjusted alpha. The strategy underperforms the Nifty 50 benchmark both IS and OOS.

### B. Residual Momentum (21d holding)
- **IS Excess Return:** -0.0106
- **IS Alpha:** -0.0105 (Beta: 0.99, t-stat: nan, p-val: nan)
- **IS Info Ratio:** -0.32
- **OOS Excess Return:** -0.0032
- **OOS Alpha:** -0.0029 (Beta: 0.96, t-stat: nan, p-val: nan)

*Verdict*: No market-adjusted alpha. Residualization does not rescue the momentum factor.

## 2. Corporate-Action Contamination Sensitivity (Liquidity Reversal)

- **Total Jump-Down Events (< -30% ON):** 25
- **Total Affected Observation Days:** 125
- **Raw Reversal Mean 5d Return:** 0.0025
- **CA-Masked Reversal Mean 5d Return:** 0.0025
- **Difference:** 0.0000

*Verdict*: The 25 unadjusted corporate action jumps affected 125 observation days. Masking these artifacts produced a negligible difference in the mean 5-day return (Difference: 0.0000). The negative result reported in Task 20 for short-term reversal was therefore NOT materially contaminated by these specific jump events. The original reversal result stands.

## 3. Final Closure Matrix

| Mechanism | Market-Adjusted Alpha | Cost-Adjusted Result | OOS Result | CA Sensitivity | Final Status |
|---|---|---|---|---|---|
| A. Raw Momentum | None | Negative / Small | Underperforms | N/A | KILLED |
| B. Residual Momentum | None | Negative / Small | Underperforms | N/A | KILLED |
| C. Liquidity Momentum | None | Negative | Underperforms | N/A | KILLED |
| D. Liquidity Reversal | N/A | N/A | N/A | Not Materially Contaminated | KILLED |
| E. Day/Night | None | Negative | Underperforms | N/A | KILLED |

============================================================
TASK 20.1 STATUS:
KILLED

MOMENTUM BRANCH:
KILLED

REVERSAL BRANCH:
KILLED

MARKET-ADJUSTED ALPHA:
Cross-sectional price momentum completely fails to deliver market-adjusted excess returns, even after controlling for beta via residualization.

CORPORATE-ACTION SENSITIVITY:
Short-term reversal calculations are NOT materially contaminated by the 25 unadjusted jump-down events (0.0000 difference). The negative result is structurally sound.

NEXT RESEARCH ACTION:
Transition away from pure price momentum/reversal factors in cash equities and explore index-level effects or alternative data.

TESTS:
3/3
