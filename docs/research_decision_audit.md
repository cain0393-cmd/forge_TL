# Research Decision Audit

## 1. Executive Summary
This audit formally compiles every hypothesis tested within the `forge_TL` project between 2016-01-01 and 2024-12-31. To date, 8 distinct signal concepts or strategies have been formally researched. Of these, 6 were explicitly **KILLED** due to a lack of statistically and economically meaningful edge in out-of-sample or cross-validated testing. The remaining 2 strategies (PEAD and DCM-Trend) are **BLOCKED** at the data-acquisition layer due to inaccessible consensus estimates, missing point-in-time sector classifications, and lack of historical Nifty 200/institutional flow data.

Currently, exactly **0 strategies survive**. The project does not possess a verified positive expectancy strategy ready for deployment.

## 2. Strategy Decision Ledger
The formal ledger has been exported to `data/research_decision_ledger.csv`. It covers:
1. Statistical Mean Reversion: **KILLED**
2. Delivery Signal Study: **KILLED**
3. Breakout Signal Study: **KILLED**
4. Cross-Sectional Dual Momentum: **KILLED**
5. Multi-Asset Trend Following: **KILLED**
6. VCP-PDA: **KILLED**
7. PEAD: **BLOCKED**
8. DCM-Trend: **BLOCKED**

## 3. Statistical Evidence
Across the 6 fully tested hypotheses, we found no systematic alpha. 
- Sharpe/Sortino ratios were near zero or negative.
- Expectancy models failed to clear the null hypothesis (e.g. VCP Component A 5D excess return +0.069%, p=0.27).
- Adding "confirming" indicators (trend, proximity) typically worsened the mathematical edge, indicating research fragility rather than robust logic.

## 4. Economic Evidence
- **Annualized net return**: All tested formulations yielded negative net returns.
- **₹ P&L**: ₹0 or negative.
- **Turnover & Costs**: The 15-20 bps friction (STT, brokerage, slippage) consumes any marginal gross edge (such as VCP's 29 bps gross return).
- **Capacity**: Not a concern since edge is non-existent.

## 5. Data Quality
The underlying OHLCV Parquet layer is pristine, strictly Point-in-Time (PIT) safe, and fully utilizes the `Nifty50UniverseProvider`. 
Blocked research (PEAD, DCM-Trend) stems directly from a refusal to compromise PIT safety (e.g., rejecting the use of today's Nifty 200 or current sector classifications as historical proxies).

## 6. Lookahead Controls
All non-blocked tests strictly separated information from execution:
- Signals evaluated at `Close[t]`.
- Execution enforced at `Open[t+1]` or later.
- No leakage from future highs/lows was permitted.

## 7. Multiple Testing
The research correctly tracked component testing (e.g., VCP tested A, B, C, D in a ladder). Because results remained statistically insignificant, the risk of p-hacking a false positive is currently **LOW/MEDIUM**. Overfitting was explicitly rejected.

## 8. Current Survivors
**NO SURVIVING STRATEGIES.**

## 9. Current Blocked Strategies
- **PEAD**: Needs institutional historical consensus feed and Nifty 200 PIT ledgers.
- **DCM-Trend**: Needs comprehensive historical derivative reconstruction, PIT sector ledgers, and institutional flow aggregates.

## 10. Economic Viability
The system architecture presumes a starting capital of ₹50,000 with a strict 1% risk rule (₹500). Even if a strategy with an exceptional 20% annualized net return existed, it would only yield ₹10,000/year (~₹833/month). If monthly infrastructure costs (VPS, data feeds) exceed ₹833, the system is mathematically guaranteed to lose money regardless of trading edge. 
Given that we currently have 0% net return, the economic viability of the project at ₹50,000 is **strictly unviable**.

## 11. Research Gaps
- We have completely exhausted simple price/volume/momentum setups on the Nifty 50 cash equities.
- We lack external data streams (macro, options flow, institutional sentiment, fundamentals).
- We lack alternative asset classes (currencies, commodities).

## 12. Next Step
The recommended action is formally recorded in `research_next_step.md`.
