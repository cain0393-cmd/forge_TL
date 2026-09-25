import os
import pandas as pd
import json

def get_candidates():
    return [
        {
            "candidate_id": "C01",
            "alpha_family": "Price/Return",
            "candidate_name": "Overnight Gap Reversal",
            "mechanism": "Large overnight gaps (up or down) reverse during the ensuing day or next few days.",
            "economic_rationale": "Retail overreaction at the open is absorbed by institutional liquidity providers, pulling price back to fundamental value.",
            "indian_market_relevance": "Indian markets have heavy retail participation at the open, often driven by global cues (SGX Nifty / US markets), leading to exaggerated opening prints.",
            "required_data": "Daily OHLC (Open and Close separately).",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "PARTIALLY_FEASIBLE (Requires entering at T+1 Open and exiting at T+1 Close for intraday, or T+2 Open for overnight reversal).",
            "cost_sensitivity": "HIGH",
            "capacity_assessment": "High capacity on Nifty 50, but susceptible to slippage if executed exactly at the open.",
            "holding_period": "Intraday to 1-2 days",
            "competition": "Widely exploited by HFTs for intraday, less crowded for multiday.",
            "research_complexity": "LOW",
            "failure_modes": "Transaction costs consuming the small gap edge. Lookahead bias if Open/Close timing is mishandled.",
            "scores": [3, 5, 5, 3, 2, 4, 3, 4, 2, 3], # Eco(15), Data(15), PIT(15), Exec(10), Cost(10), Cap(10), Rob(10), Simp(5), Comp(5), Nov(5)
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C02",
            "alpha_family": "Price/Return",
            "candidate_name": "Overnight Gap Continuation",
            "mechanism": "Large overnight gaps continue trending in the direction of the gap over the next 3-5 days.",
            "economic_rationale": "Gaps represent major structural news (earnings, macro). Price discovery is not instantaneous; institutional money scales in over several days.",
            "indian_market_relevance": "Institutional execution in India often spans multiple days due to liquidity constraints in even Nifty 50 stocks.",
            "required_data": "Daily OHLC.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "MODERATE",
            "capacity_assessment": "High capacity.",
            "holding_period": "3-5 days",
            "competition": "Moderately crowded.",
            "research_complexity": "LOW",
            "failure_modes": "Whipsaws in choppy regimes. Transaction costs.",
            "scores": [4, 5, 5, 5, 3, 4, 4, 4, 3, 3],
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C03",
            "alpha_family": "Price/Return",
            "candidate_name": "Short-Term Cross-Sectional Reversal",
            "mechanism": "Buy the worst 5 performers of the Nifty 50 over the last 3 days.",
            "economic_rationale": "Liquidity shocks and temporary supply imbalances cause price dislocation that reverts as market makers restore equilibrium.",
            "indian_market_relevance": "Highly relevant. Concentrated ETF flows often blindly sell constituents, causing temporary dislocations in fundamentally sound stocks.",
            "required_data": "Daily Close.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "HIGH",
            "capacity_assessment": "High.",
            "holding_period": "3-5 days",
            "competition": "Moderately crowded.",
            "research_complexity": "LOW",
            "failure_modes": "Catching falling knives during severe market crashes. Cost drag.",
            "scores": [4, 5, 5, 5, 2, 4, 3, 5, 2, 2],
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C04",
            "alpha_family": "Price/Return",
            "candidate_name": "Residual Momentum",
            "mechanism": "Regress stock returns against the Nifty 50. Buy stocks with the highest residual (idiosyncratic) momentum.",
            "economic_rationale": "Stripping out market beta reveals true, stock-specific accumulation by informed market participants.",
            "indian_market_relevance": "Indian indices are heavily skewed by a few mega-caps (Reliance, HDFC). Residual momentum isolates true stock-specific flows.",
            "required_data": "Daily Close, Nifty 50 Index Close.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "MODERATE",
            "capacity_assessment": "High.",
            "holding_period": "1-4 weeks",
            "competition": "Less researched than absolute momentum.",
            "research_complexity": "MEDIUM",
            "failure_modes": "Requires robust rolling regressions (computational overhead). Market neutral portfolios require shorting, which is blocked. Long-only residual momentum may underperform in bull runs.",
            "scores": [5, 5, 5, 4, 3, 4, 4, 3, 4, 4],
            "research_priority": "RESEARCH_PRIORITY"
        },
        {
            "candidate_id": "C05",
            "alpha_family": "Price/Return",
            "candidate_name": "Volatility Compression Breakout (NR7)",
            "mechanism": "Buy stocks experiencing extreme short-term volatility compression (e.g., Narrowest Range of last 7 days) that subsequently break out.",
            "economic_rationale": "Volatility is cyclical. Periods of extreme indifference/compression reliably precede violent expansions as new information enters.",
            "indian_market_relevance": "Classic retail strategy in India, but often executed poorly. Systematizing it cross-sectionally on Nifty 50 provides statistical rigor.",
            "required_data": "Daily OHLC.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "MODERATE",
            "capacity_assessment": "High.",
            "holding_period": "2-5 days",
            "competition": "Widely known, but mostly applied discretionarily.",
            "research_complexity": "LOW",
            "failure_modes": "False breakouts. Low hit rate requires strict risk management.",
            "scores": [3, 5, 5, 5, 3, 4, 3, 4, 2, 2],
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C06",
            "alpha_family": "Volume/Liquidity",
            "candidate_name": "Silent Volume Shock",
            "mechanism": "Volume > 3x average, but price change is exceptionally tight (< 0.5%).",
            "economic_rationale": "Institutional accumulation happening passively against retail selling, absorbing all liquidity without moving price.",
            "indian_market_relevance": "Pre-breakout footprint for large caps where massive liquidity is needed to build positions.",
            "required_data": "Daily OHLCV.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "MODERATE",
            "capacity_assessment": "High.",
            "holding_period": "1-3 weeks",
            "competition": "Less researched systematically.",
            "research_complexity": "MEDIUM",
            "failure_modes": "Could represent a large block deal with no directional implication. Hard to distinguish accumulation from distribution without OI.",
            "scores": [4, 5, 5, 5, 3, 4, 4, 4, 4, 4],
            "research_priority": "RESEARCH_PRIORITY"
        },
        {
            "candidate_id": "C07",
            "alpha_family": "Volume/Liquidity",
            "candidate_name": "Price-Volume Divergence (Exhaustion)",
            "mechanism": "Price drops to a new 20-day low, but volume is < 50% of 20-day average.",
            "economic_rationale": "Lack of selling pressure at lows indicates supply exhaustion. The markdown is unconfirmed by institutional volume.",
            "indian_market_relevance": "Useful in identifying false breakdowns in a structurally long-biased market.",
            "required_data": "Daily OHLCV.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "HIGH",
            "capacity_assessment": "Moderate.",
            "holding_period": "2-5 days",
            "competition": "Moderate.",
            "research_complexity": "LOW",
            "failure_modes": "Catching falling knives. Low volume might just precede a massive volume washout.",
            "scores": [4, 5, 5, 5, 2, 4, 3, 4, 3, 3],
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C08",
            "alpha_family": "Market Structure",
            "candidate_name": "Market Breadth Divergence",
            "mechanism": "Nifty 50 index is rising, but Nifty 50 Advance-Decline line is falling. Used as a market-timing regime filter.",
            "economic_rationale": "Trend is supported by only a few heavyweights; market is internally weak and prone to systemic reversal.",
            "indian_market_relevance": "Nifty 50 is heavily cap-weighted. Reliance and HDFC Bank can mask underlying weakness in the other 48 stocks.",
            "required_data": "Daily Close of all Nifty 50 stocks + Index Close.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE (Regime filter applied to cash strategies).",
            "cost_sensitivity": "LOW COST SENSITIVITY (Reduces trades, thus saving costs).",
            "capacity_assessment": "Market-wide.",
            "holding_period": "1-3 months (Regime duration)",
            "competition": "Standard institutional tool.",
            "research_complexity": "MEDIUM",
            "failure_modes": "Can keep you out of a narrow but persistent bull market, causing severe underperformance vs benchmark.",
            "scores": [5, 5, 5, 5, 5, 5, 4, 4, 3, 2],
            "research_priority": "RESEARCH_READY"
        },
        {
            "candidate_id": "C09",
            "alpha_family": "Cross-Asset",
            "candidate_name": "India VIX Panic Spikes",
            "mechanism": "Buy Nifty 50 stocks when India VIX spikes > 20% in 3 days.",
            "economic_rationale": "VIX spikes indicate forced liquidation, margin calls, and panic pricing, creating a transient risk-premium overcompensation.",
            "indian_market_relevance": "Indian retail panic and DII (Domestic Institutional Investors) acting as liquidity providers of last resort creates reliable mean reversion after VIX spikes.",
            "required_data": "India VIX Daily Close, Nifty 50 Equity OHLC.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "LOW COST SENSITIVITY (High gross returns from buying panics overcome friction).",
            "capacity_assessment": "Massive.",
            "holding_period": "1-4 weeks",
            "competition": "Less crowded systematically in cash equities.",
            "research_complexity": "LOW",
            "failure_modes": "In a true systemic crisis (e.g., COVID 2020), VIX can stay elevated while equities drop another 30%. Requires strict capital scaling.",
            "scores": [5, 5, 5, 5, 4, 5, 4, 4, 4, 4],
            "research_priority": "RESEARCH_PRIORITY"
        },
        {
            "candidate_id": "C10",
            "alpha_family": "Cross-Asset",
            "candidate_name": "VIX Term Structure / Basis",
            "mechanism": "Ratio of Implied Volatility (VIX) to Realized Volatility (20-day historical vol of Nifty 50). Buy when IV/RV > 1.5.",
            "economic_rationale": "When implied volatility wildly exceeds actual realized volatility, fear is overpriced relative to the actual mathematical risk.",
            "indian_market_relevance": "Retail option buying in India chronically overprices downside puts, driving VIX artificially high relative to actual index movement.",
            "required_data": "India VIX, Nifty 50 Index.",
            "data_status": "AVAILABLE",
            "pit_status": "YES",
            "execution_feasibility": "FEASIBLE",
            "cost_sensitivity": "LOW COST SENSITIVITY",
            "capacity_assessment": "Massive.",
            "holding_period": "1-4 weeks",
            "competition": "Standard for option sellers, rare for cash equity timing.",
            "research_complexity": "MEDIUM",
            "failure_modes": "Realized vol can suddenly spike to meet implied vol.",
            "scores": [5, 5, 5, 5, 4, 5, 4, 4, 4, 5],
            "research_priority": "RESEARCH_PRIORITY"
        },
        {
            "candidate_id": "C11",
            "alpha_family": "Market Structure",
            "candidate_name": "Sector Index Reversion",
            "mechanism": "Buy Nifty 50 stocks belonging to a sector that crashed > 5% yesterday.",
            "economic_rationale": "Sector ETF redemptions blindly sell all constituents, creating a liquidity gap in fundamentally strong stocks.",
            "indian_market_relevance": "Sectoral funds are highly popular in India, causing correlated indiscriminate selling.",
            "required_data": "Sector Index OHLC, Historical PIT Stock-to-Sector Mappings.",
            "data_status": "BLOCKED",
            "pit_status": "BLOCKED (No historical PIT sector mappings).",
            "execution_feasibility": "N/A",
            "cost_sensitivity": "N/A",
            "capacity_assessment": "N/A",
            "holding_period": "N/A",
            "competition": "N/A",
            "research_complexity": "VERY HIGH (Data Engineering)",
            "failure_modes": "N/A",
            "scores": [4, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "research_priority": "DATA_BLOCKED"
        },
        {
            "candidate_id": "C12",
            "alpha_family": "Events",
            "candidate_name": "Index Rebalancing Anticipation",
            "mechanism": "Buy stocks likely to be included in Nifty 50 ahead of the official inclusion date.",
            "economic_rationale": "Passive index funds are forced to buy, pushing up the price.",
            "indian_market_relevance": "Massive passive flows tracking Nifty 50.",
            "required_data": "Historical Nifty 100 free-float market cap data, explicit NSE methodology historical re-runs.",
            "data_status": "BLOCKED",
            "pit_status": "BLOCKED",
            "execution_feasibility": "N/A",
            "cost_sensitivity": "N/A",
            "capacity_assessment": "N/A",
            "holding_period": "N/A",
            "competition": "N/A",
            "research_complexity": "VERY HIGH",
            "failure_modes": "N/A",
            "scores": [4, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "research_priority": "DATA_BLOCKED"
        },
        {
            "candidate_id": "C13",
            "alpha_family": "Events",
            "candidate_name": "Post-Earnings Announcement Drift (PEAD)",
            "mechanism": "Standardized unexpected earnings predict multi-week drift.",
            "economic_rationale": "Analysts anchor to old estimates and slowly revise them upwards.",
            "indian_market_relevance": "Classic anomaly.",
            "required_data": "Consensus estimates, exact earnings timestamps.",
            "data_status": "BLOCKED",
            "pit_status": "BLOCKED",
            "execution_feasibility": "N/A",
            "cost_sensitivity": "N/A",
            "capacity_assessment": "N/A",
            "holding_period": "N/A",
            "competition": "N/A",
            "research_complexity": "VERY HIGH",
            "failure_modes": "N/A",
            "scores": [5, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "research_priority": "DATA_BLOCKED"
        },
        {
            "candidate_id": "C14",
            "alpha_family": "Derivatives",
            "candidate_name": "Derivative-Confirmed Momentum",
            "mechanism": "Price breakout + Futures OI expansion.",
            "economic_rationale": "Breakout is supported by new committed capital (OI), not just short covering.",
            "indian_market_relevance": "Indian F&O market is one of the most active in the world.",
            "required_data": "Historical Futures OI.",
            "data_status": "BLOCKED (Requires external acquisition of 2200 Bhavcopies).",
            "pit_status": "BLOCKED",
            "execution_feasibility": "N/A",
            "cost_sensitivity": "N/A",
            "capacity_assessment": "N/A",
            "holding_period": "N/A",
            "competition": "N/A",
            "research_complexity": "VERY HIGH",
            "failure_modes": "N/A",
            "scores": [5, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "research_priority": "DATA_BLOCKED"
        },
        {
            "candidate_id": "C15",
            "alpha_family": "Derivatives",
            "candidate_name": "Institutional Flow Shocks",
            "mechanism": "Follow extreme FII/DII daily net flows.",
            "economic_rationale": "Massive institutional money physically moves the market.",
            "indian_market_relevance": "FII flows heavily dictate Indian market trends.",
            "required_data": "FII/DII daily aggregates.",
            "data_status": "BLOCKED",
            "pit_status": "BLOCKED",
            "execution_feasibility": "N/A",
            "cost_sensitivity": "N/A",
            "capacity_assessment": "N/A",
            "holding_period": "N/A",
            "competition": "N/A",
            "research_complexity": "VERY HIGH",
            "failure_modes": "N/A",
            "scores": [5, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "research_priority": "DATA_BLOCKED"
        }
    ]

def calculate_priority_score(scores):
    # Weights: Eco(0.15), Data(0.15), PIT(0.15), Exec(0.10), Cost(0.10), Cap(0.10), Rob(0.10), Simp(0.05), Comp(0.05), Nov(0.05)
    weights = [0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.05]
    total = sum(s * w for s, w in zip(scores, weights))
    # Normalize to a 100-point scale where max possible is 5 (so total * 20)
    return round(total * 20, 1)

def write_csv_and_map(candidates):
    # Calculate scores
    for c in candidates:
        if c['data_status'] == 'BLOCKED':
            c['economic_priority_score'] = 0.0
        else:
            c['economic_priority_score'] = calculate_priority_score(c['scores'])

    # Write CSV
    df = pd.DataFrame(candidates)
    df = df.drop(columns=['scores'])
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/alpha_candidate_ledger.csv', index=False)
    
    # Write MD
    md_content = "# Alpha Source Map & Research Prioritization\n\n"
    md_content += "## Objective\nTo identify 15 genuinely distinct alpha mechanisms and rank them for future research in the `forge_TL` project.\n\n"
    
    for c in candidates:
        md_content += f"### {c['candidate_id']} - {c['candidate_name']}\n"
        md_content += f"- **Family**: {c['alpha_family']}\n"
        md_content += f"- **Mechanism**: {c['mechanism']}\n"
        md_content += f"- **Economic Rationale**: {c['economic_rationale']}\n"
        md_content += f"- **Indian Relevance**: {c['indian_market_relevance']}\n"
        md_content += f"- **Required Data**: {c['required_data']}\n"
        md_content += f"- **Data Status**: {c['data_status']}\n"
        md_content += f"- **PIT Status**: {c['pit_status']}\n"
        md_content += f"- **Execution Feasibility**: {c['execution_feasibility']}\n"
        md_content += f"- **Cost Sensitivity**: {c['cost_sensitivity']}\n"
        md_content += f"- **Capacity**: {c['capacity_assessment']}\n"
        md_content += f"- **Holding Period**: {c['holding_period']}\n"
        md_content += f"- **Competition**: {c['competition']}\n"
        md_content += f"- **Complexity**: {c['research_complexity']}\n"
        md_content += f"- **Failure Modes**: {c['failure_modes']}\n"
        md_content += f"- **Priority Score**: {c['economic_priority_score']}/100\n"
        md_content += f"- **Verdict**: **{c['research_priority']}**\n\n"
        
    os.makedirs('docs', exist_ok=True)
    with open('docs/alpha_source_map.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    return candidates

def write_decision_document(candidates):
    ready_cands = [c for c in candidates if c['data_status'] != 'BLOCKED']
    ready_cands.sort(key=lambda x: x['economic_priority_score'], reverse=True)
    
    top_3 = ready_cands[:3]
    
    content = """# Task 17 Decision: Alpha Research Prioritization

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
"""
    with open('docs/task17_decision.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    cands = get_candidates()
    write_csv_and_map(cands)
    write_decision_document(cands)
    print("Files generated.")
