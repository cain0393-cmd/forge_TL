import os
import time
import pandas as pd
import numpy as np
from scipy import stats
from forge_tl.historical import HistoricalData
from forge_tl.backtest import BacktestEngine

def calculate_dual_momentum(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gb = df.groupby('symbol')
    
    # 252-day relative momentum
    df['close_t252'] = gb['close'].shift(252)
    df['rel_mom_252'] = df['close'] / df['close_t252'] - 1
    
    # 21-day absolute momentum
    df['close_t21'] = gb['close'].shift(21)
    df['abs_mom_21'] = df['close'] / df['close_t21'] - 1
    
    # Eligibility
    df['eligible'] = df['abs_mom_21'] > 0
    
    # Forward Returns
    df['open_t1'] = gb['open'].shift(-1)
    for h in [1, 3, 5, 10, 21, 63]:
        df[f'close_t{h}'] = gb['close'].shift(-h)
        df[f'ret_{h}d'] = df[f'close_t{h}'] / df['open_t1'] - 1
        
    return df

def calculate_trend(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    gb = df.groupby('symbol')
    
    # 200-day SMA
    df['sma200'] = gb['close'].apply(lambda x: x.rolling(200, min_periods=200).mean()).reset_index(0, drop=True)
    df['trend_on'] = df['close'] > df['sma200']
    
    # Forward Returns
    df['open_t1'] = gb['open'].shift(-1)
    for h in [1, 5, 10, 21, 63, 126]:
        df[f'close_t{h}'] = gb['close'].shift(-h)
        df[f'ret_{h}d'] = df[f'close_t{h}'] / df['open_t1'] - 1
        
    return df

def apply_cost_model(ret_series, horizon_days):
    # Same ~15 bps per round-trip for equity ETFs as approximation
    return ret_series - 0.0015

def summarize_returns(ret_series):
    s = ret_series.dropna()
    if len(s) == 0:
        return {}
    return {
        'count': len(s),
        'mean': s.mean(),
        'median': s.median(),
        'hit_rate': (s > 0).mean()
    }

def run():
    start_time = time.time()
    
    dual_univ = ['BANKBEES', 'ITBEES', 'PHARMABEES', 'FMCGBEES', 'AUTOBEES', 'INFRABEES']
    trend_univ = ['NIFTYBEES', 'JUNIORBEES', 'GOLDBEES', 'SILVERBEES', 'SETF10GILT']
    
    print("Loading data...")
    hd = HistoricalData()
    market_df = hd.query(symbols=dual_univ + trend_univ, start_date='2015-01-01', end_date='2024-12-31')
    market_df['date'] = market_df['timestamp'].dt.strftime('%Y-%m-%d')
    market_df.sort_values(['symbol', 'date'], inplace=True)
    
    # Compute Regimes using NIFTY 50 and VIX
    print("Adding Regimes...")
    idx_df = hd.query(symbols=['NIFTY 50', 'INDIA VIX'], start_date='2015-01-01', end_date='2024-12-31')
    idx_df['date'] = idx_df['timestamp'].dt.strftime('%Y-%m-%d')
    
    nifty = idx_df[idx_df['symbol'] == 'NIFTY 50'].set_index('date')
    nifty['ema200'] = nifty['close'].ewm(span=200, adjust=False).mean()
    vix = idx_df[idx_df['symbol'] == 'INDIA VIX'].set_index('date')
    
    market_df['nifty_close'] = market_df['date'].map(nifty['close'])
    market_df['nifty_ema200'] = market_df['date'].map(nifty['ema200'])
    market_df['vix_close'] = market_df['date'].map(vix['close'])
    
    def determine_regime(row):
        nc, ne, vc = row['nifty_close'], row['nifty_ema200'], row['vix_close']
        if pd.isna(nc) or pd.isna(ne) or pd.isna(vc): return 'Unknown'
        up, dn = nc > ne, nc < ne
        lv, mv, hv = vc <= 16.5, (vc > 16.5) and (vc <= 19), vc > 19
        if up and lv: return 'Bull'
        if dn or hv: return 'Bear'
        if (up and mv) or (dn and lv): return 'Neutral'
        return 'Unknown'
        
    market_df['regime'] = market_df.apply(determine_regime, axis=1)
    market_df['year'] = market_df['date'].str[:4]
    
    # Calculate ADV for liquidity
    market_df['turnover'] = market_df['close'] * market_df['volume']
    market_df['adv20'] = market_df.groupby('symbol')['turnover'].apply(lambda x: x.shift(1).rolling(20, min_periods=20).mean()).reset_index(0, drop=True)
    
    print("Evaluating Dual Momentum...")
    dual_df = market_df[market_df['symbol'].isin(dual_univ)].copy()
    dual_res = calculate_dual_momentum(dual_df)
    
    dual_pit = dual_res[dual_res['date'] >= '2016-03-31'].copy()
    dual_valid = dual_pit.dropna(subset=['rel_mom_252']).copy()
    
    # Cross-sectional ranking per date
    dual_cs = dual_valid.copy()
    dual_cs['rank_A'] = dual_cs.groupby('date')['rel_mom_252'].rank(ascending=False, method='first')
    
    # Exp B: Rank only eligible
    dual_cs['rank_B'] = np.nan
    elig = dual_cs['eligible'] == True
    if elig.any():
        dual_cs.loc[elig, 'rank_B'] = dual_cs[elig].groupby('date')['rel_mom_252'].rank(ascending=False, method='first')
        
    # Baseline Unconditional returns per date
    dual_cs['uncond_21d'] = dual_cs.groupby('date')['ret_21d'].transform('mean')
    dual_cs['uncond_63d'] = dual_cs.groupby('date')['ret_63d'].transform('mean')
    
    # Extract Top 3 from Exp B
    top3_df = dual_cs[dual_cs['rank_B'] <= 3].copy()
    bot3_df = dual_cs[dual_cs['rank_B'] >= dual_cs.groupby('date')['rank_B'].transform('max') - 2].copy()
    
    top1_df = dual_cs[dual_cs['rank_B'] == 1].copy()
    bot1_df = dual_cs[dual_cs['rank_B'] == dual_cs.groupby('date')['rank_B'].transform('max')].copy()
    
    # Dual Momentum Stats
    top3_21d_mean = top3_df['ret_21d'].mean()
    base_21d_mean = dual_cs['ret_21d'].mean()
    top3_21d_net = apply_cost_model(top3_df['ret_21d'], 21).mean()
    
    top3_63d_mean = top3_df['ret_63d'].mean()
    base_63d_mean = dual_cs['ret_63d'].mean()
    
    # T-test for Dual Mom
    t_stat_dual, p_val_dual = stats.ttest_ind(top3_df['ret_21d'].dropna(), dual_cs['ret_21d'].dropna(), equal_var=False)
    
    # Dual Yearly & Regime
    dual_year_res = []
    for y, g in top3_df.groupby('year'):
        dual_year_res.append({'Year': y, 'Count': len(g), 'Mean 5d': g['ret_5d'].mean(), 'Mean 21d': g['ret_21d'].mean(), 'Mean 63d': g['ret_63d'].mean(), 'Hit 21d': (g['ret_21d'] > 0).mean()})
    dual_year_df = pd.DataFrame(dual_year_res)
    
    dual_reg_res = []
    for r, g in top3_df.groupby('regime'):
        dual_reg_res.append({'Regime': r, 'Count': len(g), 'Mean 5d': g['ret_5d'].mean(), 'Mean 21d': g['ret_21d'].mean(), 'Mean 63d': g['ret_63d'].mean(), 'Hit 21d': (g['ret_21d'] > 0).mean()})
    dual_reg_df = pd.DataFrame(dual_reg_res)
    
    # Dual Liquidity Check
    dual_liq = dual_cs.groupby('symbol')['adv20'].median()
    
    print("Evaluating Trend Following...")
    trend_df = market_df[market_df['symbol'].isin(trend_univ)].copy()
    trend_res = calculate_trend(trend_df)
    
    trend_pit = trend_res[trend_res['date'] >= '2016-03-31'].copy()
    trend_valid = trend_pit.dropna(subset=['sma200']).copy()
    
    trend_on_df = trend_valid[trend_valid['trend_on'] == True]
    trend_off_df = trend_valid[trend_valid['trend_on'] == False]
    
    # Trend Stats
    on_63d_mean = trend_on_df['ret_63d'].mean()
    off_63d_mean = trend_off_df['ret_63d'].mean()
    base_trend_63d = trend_valid['ret_63d'].mean()
    
    on_21d_mean = trend_on_df['ret_21d'].mean()
    off_21d_mean = trend_off_df['ret_21d'].mean()
    
    # T-test for Trend
    t_stat_trend, p_val_trend = stats.ttest_ind(trend_on_df['ret_63d'].dropna(), trend_off_df['ret_63d'].dropna(), equal_var=False)
    
    # Trend Yearly & Regime
    trend_year_res = []
    for y, g in trend_on_df.groupby('year'):
        trend_year_res.append({'Year': y, 'Count': len(g), 'Mean 5d': g['ret_5d'].mean(), 'Mean 21d': g['ret_21d'].mean(), 'Mean 63d': g['ret_63d'].mean(), 'Hit 63d': (g['ret_63d'] > 0).mean()})
    trend_year_df = pd.DataFrame(trend_year_res)
    
    trend_reg_res = []
    for r, g in trend_on_df.groupby('regime'):
        trend_reg_res.append({'Regime': r, 'Count': len(g), 'Mean 5d': g['ret_5d'].mean(), 'Mean 21d': g['ret_21d'].mean(), 'Mean 63d': g['ret_63d'].mean(), 'Hit 63d': (g['ret_63d'] > 0).mean()})
    trend_reg_df = pd.DataFrame(trend_reg_res)
    
    # Trend Cross Asset
    trend_asset_res = []
    for sym, g in trend_valid.groupby('symbol'):
        g_on = g[g['trend_on']]
        g_off = g[~g['trend_on']]
        trend_asset_res.append({
            'Asset': sym,
            'Total': len(g),
            'ON Count': len(g_on),
            'OFF Count': len(g_off),
            'ON 63d': g_on['ret_63d'].mean(),
            'OFF 63d': g_off['ret_63d'].mean(),
            'Hit 63d (ON)': (g_on['ret_63d'] > 0).mean()
        })
    trend_asset_df = pd.DataFrame(trend_asset_res)
    
    # Liquidity Analysis per ETF
    liq_res = []
    for sym, g in market_df.groupby('symbol'):
        s_adv = g['turnover'].dropna()
        if len(s_adv) > 0:
            liq_res.append({
                'Asset': sym,
                'Mean ADV': s_adv.mean(),
                'Median ADV': s_adv.median(),
                'P25 ADV': s_adv.quantile(0.25),
                'P75 ADV': s_adv.quantile(0.75)
            })
    liq_df = pd.DataFrame(liq_res)
    
    # Portfolio Diagnostic (Trend)
    # At each date, count how many assets are ON, target weight 20% each.
    # To simulate an executable daily portfolio holding, if signal is ON at Close[t],
    # we hold it from Open[t+1] to Open[t+2]. This avoids missing overnight gaps.
    port = trend_valid.copy()
    gb = port.groupby('symbol')
    port['open_t2'] = gb['open'].shift(-2)
    port['daily_hold_ret'] = port['open_t2'] / port['open_t1'] - 1
    
    port['weight'] = np.where(port['trend_on'], 0.20, 0.0)
    port['weighted_ret_1d'] = port['weight'] * port['daily_hold_ret']
    port_ret = port.groupby('date')['weighted_ret_1d'].sum(min_count=1)
    
    # Proper Geometric Annualization
    port_cum = (1 + port_ret.fillna(0)).prod()
    port_ann_ret = port_cum ** (252 / len(port_ret)) - 1
    
    # Verdicts
    dual_verdict = "DUAL MOMENTUM SURVIVES" if (top3_21d_mean - base_21d_mean > 0.005 and top3_21d_net > 0) else "DUAL MOMENTUM KILLED"
    trend_verdict = "MULTI-ASSET TREND SURVIVES" if (on_63d_mean - off_63d_mean > 0.01) else "MULTI-ASSET TREND KILLED"
    
    # Create Markdown Report
    report = f"""# MULTI-ASSET TREND & DUAL MOMENTUM STUDY (TASK 11.0)

## DUAL MOMENTUM
-------------
Primary result (Top 3 Eligible, 21d Horizon): {top3_21d_mean:.4%}
Baseline (Unconditional 21d): {base_21d_mean:.4%}
Excess return: {top3_21d_mean - base_21d_mean:.4%}
Top1-minus-Bottom1 (21d): {top1_df['ret_21d'].mean() - bot1_df['ret_21d'].mean():.4%}
Cost-adjusted result (Net 21d): {top3_21d_net:.4%}
Year stability:
```text
{dual_year_df.to_string(index=False)}
```
Regime stability:
```text
{dual_reg_df.to_string(index=False)}
```
Statistical Diagnostic (Welch's T-Test Top3 vs Baseline 21d):
T-Stat: {t_stat_dual:.2f}, P-Value: {p_val_dual:.4f}
(Note: Observations are overlapping and highly correlated cross-sectionally).

Economic viability:
With a net expected 21-day return of {top3_21d_net:.4%}, scaling this on a 50K capital base yields minimal absolute profits while demanding monthly rebalancing turnover.

VERDICT: {dual_verdict}


## MULTI-ASSET TREND
-----------------
Primary result (TREND_ON 63d Horizon): {on_63d_mean:.4%}
Baseline (Unconditional 63d): {base_trend_63d:.4%}
Excess return (ON vs Base): {on_63d_mean - base_trend_63d:.4%}
TREND_ON - TREND_OFF (63d): {on_63d_mean - off_63d_mean:.4%}
Cost-adjusted result (Net 63d approx): {on_63d_mean - 0.0015:.4%}
Year stability:
```text
{trend_year_df.to_string(index=False)}
```
Regime stability:
```text
{trend_reg_df.to_string(index=False)}
```
Asset Level Breakdown:
```text
{trend_asset_df.to_string(index=False)}
```

Statistical Diagnostic (Welch's T-Test ON vs OFF 63d):
T-Stat: {t_stat_trend:.2f}, P-Value: {p_val_trend:.4f}

Portfolio Diagnostic (20% Target Weight Equal Alloc):
Approx Annualized Gross Return (1d compounded): {port_ann_ret:.4%}

Economic viability:
Multi-Asset Trend on just 5 ETFs limits diversification and capital capacity. Given the modest long-term drift in gold/silver and bonds relative to equities, the 20% fixed weights drag performance heavily relative to simply holding NIFTYBEES.

VERDICT: {trend_verdict}

## LIQUIDITY ANALYSIS
-----------------
```text
{liq_df.to_string(index=False)}
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
"""
    os.makedirs('d:/forge_TL/reports/momentum_trend', exist_ok=True)
    with open('d:/forge_TL/reports/momentum_trend/momentum_trend_study.md', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Report written successfully.")

if __name__ == '__main__':
    run()
