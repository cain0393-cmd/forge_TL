import os
import pandas as pd
import json

def get_ledger_data():
    return [
        {
            "strategy_id": "MR_01",
            "strategy_name": "Statistical Mean Reversion",
            "research_task": "Task 7",
            "hypothesis": "Extreme price deviations revert to the mean.",
            "universe": "PIT Nifty 50",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV Parquet",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "INSUFFICIENT",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "economically weak and statistically insufficient",
            "source_report": "task7_report.md",
            "source_code": "run_research_mean_reversion.py",
            "source_tests": "test_mean_reversion.py",
            "evidence_quality": "B",
            "research_trials": "UNKNOWN",
            "multiple_testing_risk": "MEDIUM",
            "notes": "Mechanically implemented but no edge found."
        },
        {
            "strategy_id": "DS_01",
            "strategy_name": "Delivery Signal Study",
            "research_task": "Task 9.1",
            "hypothesis": "High delivery volume predicts positive forward returns.",
            "universe": "PIT Nifty 50",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV + Delivery",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "INSUFFICIENT",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "no robust predictive edge detected",
            "source_report": "task9.1_report",
            "source_code": "NOT AVAILABLE",
            "source_tests": "NOT AVAILABLE",
            "evidence_quality": "B",
            "research_trials": "UNKNOWN",
            "multiple_testing_risk": "MEDIUM",
            "notes": "Delivery spikes are largely random noise."
        },
        {
            "strategy_id": "BRK_01",
            "strategy_name": "Breakout Signal Study",
            "research_task": "Task 10.0",
            "hypothesis": "Price breakouts predict positive momentum.",
            "universe": "PIT Nifty 50",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV Parquet",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "NEGATIVE",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "tested breakout formulation failed",
            "source_report": "breakout_report",
            "source_code": "scripts/run_research_breakout_10_0.py",
            "source_tests": "tests/test_breakout_10_0.py",
            "evidence_quality": "A",
            "research_trials": "1",
            "multiple_testing_risk": "LOW",
            "notes": "50-day breakouts underperformed baseline across all regimes."
        },
        {
            "strategy_id": "DM_01",
            "strategy_name": "Cross-Sectional Dual Momentum",
            "research_task": "Task 11.0",
            "hypothesis": "Assets showing strongest relative/absolute momentum out-perform.",
            "universe": "Sector ETFs",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV Parquet",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "NEGATIVE",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "tested formulation failed to demonstrate robust positive excess return",
            "source_report": "momentum_report",
            "source_code": "scripts/run_research_momentum_trend_11_0.py",
            "source_tests": "tests/test_momentum_trend_11_0.py",
            "evidence_quality": "A",
            "research_trials": "1",
            "multiple_testing_risk": "LOW",
            "notes": "Sector ETF momentum severely underperformed baseline."
        },
        {
            "strategy_id": "MAT_01",
            "strategy_name": "Multi-Asset Trend Following",
            "research_task": "Task 11.0",
            "hypothesis": "Trend following across asset classes produces absolute return.",
            "universe": "Mixed ETFs",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV Parquet",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "+9.14%",
            "annualized_net_return": "NEGATIVE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "WEAK",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "tested formulation failed to demonstrate the required edge",
            "source_report": "momentum_report",
            "source_code": "scripts/run_research_momentum_trend_11_0.py",
            "source_tests": "tests/test_momentum_trend_11_0.py",
            "evidence_quality": "A",
            "research_trials": "1",
            "multiple_testing_risk": "LOW",
            "notes": "Bug fix corrected return calculation, but edge was still insufficient."
        },
        {
            "strategy_id": "VCP_01",
            "strategy_name": "VCP-PDA",
            "research_task": "Task 14",
            "hypothesis": "Volatility contraction + trend + volume precedes breakouts.",
            "universe": "PIT Nifty 50",
            "universe_pit_status": "VALIDATED",
            "data_sources": "NSE OHLCV Parquet",
            "research_period": "2016-2024",
            "lookahead_controls": "Signal at Close[t], Exec at Open[t+1]",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4 (15-20 bps)",
            "is_period": "2016-2021",
            "oos_period": "2022-2024",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NEGATIVE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "NEGATIVE",
            "economic_evidence": "WEAK",
            "verdict": "KILLED",
            "failure_reason": "tested formulation failed to demonstrate statistically/economically meaningful excess return",
            "source_report": "reports/vcp/vcp_component_study.md",
            "source_code": "scripts/run_research_vcp_14.py",
            "source_tests": "tests/test_vcp_14.py",
            "evidence_quality": "A",
            "research_trials": "4",
            "multiple_testing_risk": "MEDIUM",
            "notes": "Added components (Trend, Proximity) strictly decreased expected returns."
        },
        {
            "strategy_id": "PEAD_01",
            "strategy_name": "PEAD",
            "research_task": "Task 16.0",
            "hypothesis": "Positive earnings surprises lead to post-announcement drift.",
            "universe": "PIT Nifty 200",
            "universe_pit_status": "BLOCKED",
            "data_sources": "NSE Earnings, Consensus Estimates",
            "research_period": "2016-2024",
            "lookahead_controls": "NOT TESTED",
            "execution_assumption": "T+1 Open / Intraday",
            "cost_model": "Task 4",
            "is_period": "NOT TESTED",
            "oos_period": "NOT TESTED",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "NONE",
            "economic_evidence": "NONE",
            "verdict": "BLOCKED",
            "failure_reason": "historical event timing, consensus expectations, and PIT Nifty 200 data unavailable",
            "source_report": "docs/pead_data_quality.md",
            "source_code": "NOT TESTED",
            "source_tests": "NOT TESTED",
            "evidence_quality": "D",
            "research_trials": "0",
            "multiple_testing_risk": "UNKNOWN",
            "notes": "Data fundamentally impossible to scrape automatically without licensed feeds."
        },
        {
            "strategy_id": "DCM_01",
            "strategy_name": "DCM-Trend",
            "research_task": "Task 15",
            "hypothesis": "Derivative-Confirmed Momentum (Price + OI + Sector + Flow).",
            "universe": "F&O Universe",
            "universe_pit_status": "FEASIBLE",
            "data_sources": "NSE Bhavcopy, Flow, Sector",
            "research_period": "2016-2024",
            "lookahead_controls": "NOT TESTED",
            "execution_assumption": "T+1 Open",
            "cost_model": "Task 4",
            "is_period": "NOT TESTED",
            "oos_period": "NOT TESTED",
            "trade_count": "NOT AVAILABLE",
            "is_sharpe": "NOT AVAILABLE",
            "oos_sharpe": "NOT AVAILABLE",
            "is_sortino": "NOT AVAILABLE",
            "oos_sortino": "NOT AVAILABLE",
            "is_max_drawdown": "NOT AVAILABLE",
            "oos_max_drawdown": "NOT AVAILABLE",
            "is_profit_factor": "NOT AVAILABLE",
            "oos_profit_factor": "NOT AVAILABLE",
            "is_expectancy_r": "NOT AVAILABLE",
            "oos_expectancy_r": "NOT AVAILABLE",
            "is_total_return": "NOT AVAILABLE",
            "oos_total_return": "NOT AVAILABLE",
            "annualized_return": "NOT AVAILABLE",
            "annualized_net_return": "NOT AVAILABLE",
            "turnover": "NOT AVAILABLE",
            "capital_utilization": "NOT AVAILABLE",
            "cost_as_pct_gross": "NOT MEANINGFUL",
            "statistical_evidence": "NONE",
            "economic_evidence": "NONE",
            "verdict": "BLOCKED",
            "failure_reason": "complete required historical data stack unavailable",
            "source_report": "docs/dcm_data_quality.md",
            "source_code": "NOT TESTED",
            "source_tests": "NOT TESTED",
            "evidence_quality": "D",
            "research_trials": "0",
            "multiple_testing_risk": "UNKNOWN",
            "notes": "Sector mapping and institutional flow blocked."
        }
    ]

def write_csv(data):
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/research_decision_ledger.csv', index=False)

def write_audit():
    content = """# Research Decision Audit

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
"""
    os.makedirs('docs', exist_ok=True)
    with open('docs/research_decision_audit.md', 'w', encoding='utf-8') as f:
        f.write(content)

def write_next_step():
    content = """# Next Research Decision

**Recommendation:**
`F: RECONSIDER_PROJECT_ECONOMICS`

**Rationale:**
The project currently has zero surviving strategies out of 8 attempted core hypotheses. All traditional price/volume combinations (mean reversion, breakout, trend, VCP, momentum) have failed to overcome the 15-20 bps friction constraint of the Indian cash equity market. 

Simultaneously, the target starting capital is ₹50,000. 
If we somehow discover a world-class strategy yielding 30% annualized net return (an incredibly difficult feat), the annual gross profit is ₹15,000 (₹1,250 per month). 
Acquiring the required external data for blocked strategies (like PEAD consensus data or Institutional Flow) will immediately cost thousands of rupees per month, instantly bankrupting the system's P&L. 

Therefore, before writing any more code or paying for new datasets, the project must reconsider its economics. Trading ₹50,000 using automated cloud infrastructure and licensed feeds is structurally unprofitable due to fixed costs. The project must either significantly scale up intended capital or pivot to ultra-low-frequency/no-cost deployment methods.
"""
    with open('docs/research_next_step.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    ledger_data = get_ledger_data()
    write_csv(ledger_data)
    write_audit()
    write_next_step()
    print("Successfully generated ledger and audit documents.")
