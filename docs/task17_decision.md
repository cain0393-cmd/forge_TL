# Task 17 Decision: Alpha Research Prioritization

## Overview
- **Research Objective**: Identify and prioritize genuinely distinct alpha sources outside of classical momentum/trend/reversion that failed in prior tasks.
- **Candidates Evaluated**: 15
- **Candidates Data-Blocked**: 5 (Sector Reversion, Index Rebalancing, PEAD, DCM-Trend, Flow Shocks)
- **Candidates Research-Ready**: 10
- **Scoring Methodology**: Weighted scoring (15% Eco Rationale, 15% Data, 15% PIT, 10% Execution, 10% Cost, 10% Capacity, 10% Robustness, 5% Simplicity, 5% Competition, 5% Novelty) out of 100.

## Top 3 Research Priorities

### #1
**Candidate**: VIX Term Structure / Basis (C10)
**Why**: Fear pricing (implied volatility) routinely overshoots realized volatility in India due to systemic retail option buying. Mean-reversion of this premium is a structural cross-asset arbitrage mechanism completely independent of pure price momentum.
**Data status**: AVAILABLE (India VIX & Nifty 50 Cash).
**PIT status**: YES.
**Expected holding period**: 1-4 weeks.
**Main risk**: Realized volatility spikes matching implied volatility during a true black swan event.
**Why it is better than alternatives**: It exploits a well-known derivatives premium (variance risk premium) without requiring us to trade derivatives—we simply use the mispricing to time cash equity exposure. It is entirely uncorrelated with previously killed strategies.

### #2
**Candidate**: India VIX Panic Spikes (C09)
**Why**: Simple, robust measure of capitulation. Panic is universally human and structurally identical across decades.
**Data status**: AVAILABLE.
**PIT status**: YES.
**Expected holding period**: 1-4 weeks.
**Main risk**: Buying too early in a cascading structural bear market.
**Why it is better than alternatives**: Provides a market-timing overlay that can drastically improve the capacity and hit-rate of any underlying cash strategy by ensuring capital is only deployed when risk premiums are highest.

### #3
**Candidate**: Residual Momentum (C04)
**Why**: Isolates idiosyncratic stock accumulation by stripping out market beta. 
**Data status**: AVAILABLE.
**PIT status**: YES.
**Expected holding period**: 1-4 weeks.
**Main risk**: Computationally intensive, and long-only residual momentum can lag the broader market during purely beta-driven liquidity rallies.
**Why it is better than alternatives**: Fixes the flaw of Dual Momentum (Task 11) which simply bought high-beta stocks that subsequently collapsed.

## Recommended Next Task
**Task**: Research VIX Term Structure / Basis (Variance Risk Premium Cash Timing)
**Reason**: It offers a completely different economic mechanism (risk premium extraction via cross-asset sentiment) compared to all previously killed technical price strategies. The data is locally available, pristine, and perfectly PIT-safe.
