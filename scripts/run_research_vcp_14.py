import os
import time
import pandas as pd
import numpy as np
from scipy import stats
from forge_tl.historical import HistoricalData
from forge_tl.universe.nifty50 import Nifty50UniverseProvider
from forge_tl.backtest import BacktestEngine

def calculate_atr(high, low, close_prev, n):
    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean()

def calculate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    gb = df.groupby('symbol')
    
    # TR and ATR
    df['close_prev'] = gb['close'].shift(1)
    
    # We must calculate ATR per group to avoid cross-symbol contamination
    def get_atr(g, n):
        tr1 = g['high'] - g['low']
        tr2 = (g['high'] - g['close_prev']).abs()
        tr3 = (g['low'] - g['close_prev']).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        # We use simple moving average for absolute determinism in VCP
        return tr.rolling(n, min_periods=n).mean()

    df['atr5'] = gb.apply(lambda g: get_atr(g, 5)).reset_index(0, drop=True)
    df['atr20'] = gb.apply(lambda g: get_atr(g, 20)).reset_index(0, drop=True)
    
    # Moving Averages
    df['ema20'] = gb['close'].apply(lambda x: x.ewm(span=20, adjust=False).mean()).reset_index(0, drop=True)
    df['ema50'] = gb['close'].apply(lambda x: x.ewm(span=50, adjust=False).mean()).reset_index(0, drop=True)
    df['sma200'] = gb['close'].apply(lambda x: x.rolling(200, min_periods=200).mean()).reset_index(0, drop=True)
    
    # 250-day rolling high
    df['high250'] = gb['close'].apply(lambda x: x.rolling(250, min_periods=250).max()).reset_index(0, drop=True)
    
    # Volume SMA20
    df['vol_sma20'] = gb['volume'].apply(lambda x: x.rolling(20, min_periods=20).mean()).reset_index(0, drop=True)
    
    # Signals
    # Component A: Volatility Contraction
    df['sig_A'] = (df['atr5'] / df['atr20']) < 0.70
    
    # Component B: Trend
    df['sig_B'] = df['sig_A'] & (df['close'] > df['ema20']) & (df['ema20'] > df['ema50']) & (df['ema50'] > df['sma200'])
    
    # Component C: High Proximity
    df['sig_C'] = df['sig_B'] & (df['close'] >= 0.90 * df['high250'])
    
    # Component D: Volume Confirmation
    df['sig_D'] = df['sig_C'] & (df['volume'] > 1.20 * df['vol_sma20'])
    
    # Forward Returns (from Open[t+1] to Open[t+1+h])
    df['open_t1'] = gb['open'].shift(-1)
    for h in [1, 3, 5, 10, 20]:
        df[f'open_t{h+1}'] = gb['open'].shift(-(h+1))
        df[f'ret_{h}d'] = df[f'open_t{h+1}'] / df['open_t1'] - 1
        
    return df

def summarize_returns(rets: pd.Series):
    rets = rets.dropna()
    if len(rets) == 0:
        return None
    return {
        'count': len(rets),
        'mean': rets.mean(),
        'median': rets.median(),
        'hit_rate': (rets > 0).mean(),
        'std': rets.std()
    }

def main():
    print("Loading data...")
    hd = HistoricalData()
    univ_prov = Nifty50UniverseProvider()
    
    start_date = '2016-01-01'
    end_date = '2024-12-31'
    
    df = hd.query(start_date='2015-01-01', end_date=end_date)
    df.sort_values(['symbol', 'timestamp'], inplace=True)
    df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    
    print("Calculating signals...")
    df = calculate_signals(df)
    
    # Nifty 50 PIT filter
    print("Filtering PIT universe...")
    records = []
    # Build a quick lookup for PIT
    for date, group in df.groupby('date'):
        if date < start_date: continue
        try:
            pit_symbols = univ_prov.get_universe(date)
            valid = group[group['symbol'].isin(pit_symbols)]
            records.append(valid)
        except Exception:
            pass
            
    df_pit = pd.concat(records)
    
    # Exclude early NaNs
    df_pit = df_pit.dropna(subset=['atr20', 'sma200', 'high250', 'vol_sma20'])
    
    print("Evaluating...")
    
    # Regimes and Liquidity
    df_pit['year'] = pd.to_datetime(df_pit['date']).dt.year
    df_pit['is_oos'] = np.where(df_pit['year'] >= 2022, 'OOS', 'IS')
    
    # Simple market proxy regime using SMA200 of NIFTYBEES or similar if available. 
    # For now, evaluate base signals.
    
    horizons = [1, 3, 5, 10, 20]
    
    results = []
    
    # Baseline
    base_stats = {}
    for h in horizons:
        base_stats[h] = summarize_returns(df_pit[f'ret_{h}d'])
    
    for sig_name in ['sig_A', 'sig_B', 'sig_C', 'sig_D']:
        sig_df = df_pit[df_pit[sig_name] == True]
        for h in horizons:
            st = summarize_returns(sig_df[f'ret_{h}d'])
            if not st: continue
            
            b_st = base_stats[h]
            if not b_st: continue
            
            t_stat, p_val = stats.ttest_ind(sig_df[f'ret_{h}d'].dropna(), df_pit[f'ret_{h}d'].dropna(), equal_var=False)
            
            results.append({
                'Signal': sig_name,
                'Horizon': h,
                'Count': st['count'],
                'Sig_Mean': st['mean'],
                'Base_Mean': b_st['mean'],
                'Diff': st['mean'] - b_st['mean'],
                'Hit_Rate': st['hit_rate'],
                'P_Val': p_val
            })
            
    res_df = pd.DataFrame(results)
    
    os.makedirs('reports/vcp', exist_ok=True)
    res_df.to_csv('reports/vcp/vcp_component_results.csv', index=False)
    
    # Yearly Stability for Signal D 5d
    sigD_df = df_pit[df_pit['sig_D'] == True]
    yearly_res = []
    for yr, g in sigD_df.groupby('year'):
        st = summarize_returns(g['ret_5d'])
        if st:
            yearly_res.append({'Year': yr, 'Count': st['count'], 'Mean_5d': st['mean'], 'Hit_Rate': st['hit_rate']})
    pd.DataFrame(yearly_res).to_csv('reports/vcp/vcp_yearly.csv', index=False)
    
    # Write Markdown
    with open('reports/vcp/vcp_component_study.md', 'w') as f:
        f.write("# VCP Component Study\n\n")
        f.write("## Baseline\n")
        f.write(f"Universe: {len(df_pit)} daily observations\n")
        for h in horizons:
            f.write(f"- {h}D: {base_stats[h]['mean']:.4%} mean, {base_stats[h]['hit_rate']:.2%} hit\n")
            
        f.write("\n## Signals\n")
        for sig in ['sig_A', 'sig_B', 'sig_C', 'sig_D']:
            f.write(f"\n### {sig}\n")
            sig_data = res_df[res_df['Signal'] == sig]
            for _, r in sig_data.iterrows():
                f.write(f"- {r['Horizon']}D: {r['Count']} events | {r['Sig_Mean']:.4%} (vs {r['Base_Mean']:.4%}) | diff: {r['Diff']:.4%} | p: {r['P_Val']:.4f}\n")

    print("Complete.")

if __name__ == '__main__':
    main()
