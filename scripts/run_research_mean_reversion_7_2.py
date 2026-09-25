import os
import time
import pandas as pd
import numpy as np
from forge_tl.historical import HistoricalData
from forge_tl.backtest import BacktestEngine
from forge_tl.strategies.mean_reversion import MeanReversionStrategy
from forge_tl.universe.nifty50 import Nifty50UniverseProvider

def calculate_drawdowns(equity_curve):
    peak = equity_curve.expanding(min_periods=1).max()
    drawdown = (equity_curve / peak) - 1.0
    return drawdown

def generate_report(res, df_regime, start_date, end_date):
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    
    trades = res['trades']
    eq = res['equity_curve']['equity']
    
    metrics = {}
    
    # CAPITAL & RETURN
    start_cap = 50000.0
    end_cap = eq.iloc[-1] if not eq.empty else start_cap
    metrics['Starting Capital'] = start_cap
    metrics['Ending Capital'] = end_cap
    metrics['Peak Equity'] = eq.max() if not eq.empty else start_cap
    metrics['Minimum Equity'] = eq.min() if not eq.empty else start_cap
    
    tot_ret = (end_cap / start_cap) - 1.0
    days = (end_ts - start_ts).days
    years = max(days / 365.25, 0.0001)
    cagr = ((end_cap / start_cap) ** (1/years) - 1.0) if end_cap > 0 else -1.0
    metrics['Total Return'] = tot_ret
    metrics['CAGR'] = cagr
    
    daily_rets = eq.pct_change().dropna()
    ann_vol = daily_rets.std() * np.sqrt(252) if len(daily_rets) > 0 else 0.0
    metrics['Annualized Volatility'] = ann_vol
    
    # RISK
    metrics['Sharpe Ratio'] = res['metrics'].get('sharpe_ratio', 0.0)
    metrics['Sortino Ratio'] = res['metrics'].get('sortino_ratio', 0.0)
    
    dds = calculate_drawdowns(eq)
    max_dd = dds.min() if not dds.empty else 0.0
    avg_dd = dds[dds < 0].mean() if len(dds[dds < 0]) > 0 else 0.0
    metrics['Max Drawdown'] = max_dd
    metrics['Average Drawdown'] = avg_dd
    
    metrics['Calmar Ratio'] = (cagr / abs(max_dd)) if max_dd < 0 else float('inf')
    
    is_dd = dds < 0
    dd_durs = []
    cur_dur = 0
    for b in is_dd:
        if b: cur_dur += 1
        else:
            if cur_dur > 0: dd_durs.append(cur_dur)
            cur_dur = 0
    if cur_dur > 0: dd_durs.append(cur_dur)
    metrics['Max Drawdown Duration'] = max(dd_durs) if dd_durs else 0
    
    # TRADES
    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl <= 0]
    metrics['Total Trades'] = len(trades)
    metrics['Winning Trades'] = len(wins)
    metrics['Losing Trades'] = len(losses)
    metrics['Win Rate'] = len(wins) / len(trades) if trades else 0.0
    
    metrics['Average Trade Return'] = np.mean([t.net_pnl for t in trades]) if trades else 0.0
    metrics['Average Winning Trade'] = np.mean([t.net_pnl for t in wins]) if wins else 0.0
    metrics['Average Losing Trade'] = np.mean([t.net_pnl for t in losses]) if losses else 0.0
    
    gross_profits = sum([t.net_pnl for t in wins])
    gross_losses = abs(sum([t.net_pnl for t in losses]))
    metrics['Profit Factor'] = (gross_profits / gross_losses) if gross_losses > 0 else (float('inf') if gross_profits > 0 else 0.0)
    metrics['Payoff Ratio'] = abs(metrics['Average Winning Trade'] / metrics['Average Losing Trade']) if metrics['Average Losing Trade'] != 0 else float('inf')
    
    metrics['Expectancy'] = metrics['Average Trade Return']
    metrics['Expectancy (R)'] = metrics['Average Trade Return'] / 500.0 # 1% risk = 500 INR
    
    hps = [(t.exit_timestamp - t.entry_timestamp).days for t in trades]
    metrics['Average Holding Period'] = np.mean(hps) if hps else 0.0
    metrics['Max Holding Period'] = np.max(hps) if hps else 0.0
    
    # EXECUTION
    orders = res['orders']
    metrics['Filled Orders'] = len([o for o in orders if o.status.name == 'FILLED'])
    metrics['Rejected Orders'] = len([o for o in orders if o.status.name == 'REJECTED'])
    metrics['Cancelled Orders'] = len([o for o in orders if o.status.name == 'CANCELLED'])
    metrics['Total Turnover'] = sum([t.entry_price * t.entry_quantity + t.exit_price * t.entry_quantity for t in trades])
    metrics['Total Transaction Costs'] = sum([t.entry_cost + t.exit_cost for t in trades])
    
    return metrics, trades, eq

def run():
    print("Loading historical data...")
    hd = HistoricalData()
    df = hd.query(start_date='2016-01-01', end_date='2024-12-31')
    print(f"Loaded {len(df)} rows")
    
    print("Computing regimes...")
    nifty = df[df['symbol'] == 'NIFTY 50'].set_index('timestamp').sort_index()
    vix = df[df['symbol'] == 'INDIA VIX'].set_index('timestamp').sort_index()
    
    nifty['ema200'] = nifty['close'].ewm(span=200, adjust=False).mean()
    regime_df = pd.DataFrame(index=nifty.index)
    regime_df['nifty'] = nifty['close']
    regime_df['ema200'] = nifty['ema200']
    
    vix_close = vix['close']
    vix_close = vix_close[~vix_close.index.duplicated(keep='last')]
    regime_df = regime_df.join(vix_close.rename('vix'), how='left')
    regime_df['vix'] = regime_df['vix'].ffill()
    
    def assign_regime(row):
        n = row['nifty']
        e = row['ema200']
        v = row['vix']
        if pd.isna(n) or pd.isna(e) or pd.isna(v): return 'Unknown'
        if n > e and v <= 16.5: return 'Bull'
        if (n > e and 16.5 < v <= 19) or (n < e and v <= 16.5): return 'Neutral'
        return 'Bear'
    
    regime_df['regime'] = regime_df.apply(assign_regime, axis=1)
    
    print("Running combined backtest...")
    t0 = time.time()
    eng = BacktestEngine(df, initial_capital=50000.0)
    strat = MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5)
    eng.set_strategy(strat)
    res_comb = eng.run()
    runtime = time.time() - t0
    print(f"Backtest took {runtime:.2f}s")
    
    print("Checking determinism...")
    eng2 = BacktestEngine(df, initial_capital=50000.0)
    strat2 = MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5)
    eng2.set_strategy(strat2)
    res_comb2 = eng2.run()
    det_pass = (res_comb['metrics']['total_return'] == res_comb2['metrics']['total_return'] and
                res_comb['metrics']['number_of_trades'] == res_comb2['metrics']['number_of_trades'])
    print(f"Determinism Pass: {det_pass}")
    
    print("Computing metrics...")
    
    # We can compute IS and OOS directly from the combined trades & equity curve to save runtime!
    # Wait, the equity curve for IS will correctly reflect the first 6 years if we slice it, 
    # but starting capital for OOS would normally reset to 50000. 
    # Let's run IS and OOS backtests separately to be absolutely faithful to capital boundaries.
    
    df_is = df[(df['timestamp'] >= '2016-01-01') & (df['timestamp'] <= '2021-12-31')]
    eng_is = BacktestEngine(df_is, initial_capital=50000.0)
    eng_is.set_strategy(MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5))
    res_is = eng_is.run()
    
    df_oos = df[(df['timestamp'] >= '2022-01-01') & (df['timestamp'] <= '2024-12-31')]
    eng_oos = BacktestEngine(df_oos, initial_capital=50000.0)
    eng_oos.set_strategy(MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5))
    res_oos = eng_oos.run()
    
    is_m, is_t, is_eq = generate_report(res_is, regime_df, '2016-01-01', '2021-12-31')
    oos_m, oos_t, oos_eq = generate_report(res_oos, regime_df, '2022-01-01', '2024-12-31')
    comb_m, comb_t, comb_eq = generate_report(res_comb, regime_df, '2016-01-01', '2024-12-31')
    
    # Yearly
    yearly_rows = []
    for yr in range(2016, 2025):
        try:
            yr_eq = comb_eq[comb_eq.index.year == yr]
            yr_trades = [t for t in comb_t if t.entry_timestamp.year == yr]
            if not yr_eq.empty:
                s_cap = yr_eq.iloc[0]
                e_cap = yr_eq.iloc[-1]
                ret = (e_cap / s_cap) - 1.0
                daily = yr_eq.pct_change().dropna()
                sharpe = (daily.mean() / daily.std()) * np.sqrt(252) if daily.std() > 0 else 0
                dds = calculate_drawdowns(yr_eq)
                max_dd = dds.min() if not dds.empty else 0.0
                
                wins = [t for t in yr_trades if t.net_pnl > 0]
                losses = [t for t in yr_trades if t.net_pnl <= 0]
                wr = len(wins)/len(yr_trades) if yr_trades else 0
                pf = (sum([t.net_pnl for t in wins]) / abs(sum([t.net_pnl for t in losses]))) if sum([t.net_pnl for t in losses]) != 0 else float('inf')
                exp = np.mean([t.net_pnl for t in yr_trades]) if yr_trades else 0
                
                yearly_rows.append({
                    'Year': yr, 'Return': ret, 'Sharpe': sharpe, 'Max DD': max_dd,
                    'Trades': len(yr_trades), 'Win Rate': wr, 'Profit Factor': pf, 'Expectancy': exp
                })
        except Exception as e:
            pass
    yearly_df = pd.DataFrame(yearly_rows)
    
    # Regime
    regime_rows = []
    for t in comb_t:
        entry_ts = t.entry_timestamp
        # find closest regime before or on entry
        reg = regime_df[regime_df.index <= entry_ts]['regime'].iloc[-1] if not regime_df[regime_df.index <= entry_ts].empty else 'Unknown'
        t.regime = reg
        
    for reg in ['Bull', 'Neutral', 'Bear', 'Unknown']:
        r_trades = [t for t in comb_t if getattr(t, 'regime', 'Unknown') == reg]
        if not r_trades: continue
        wins = [t for t in r_trades if t.net_pnl > 0]
        losses = [t for t in r_trades if t.net_pnl <= 0]
        wr = len(wins)/len(r_trades)
        pf = (sum([t.net_pnl for t in wins]) / abs(sum([t.net_pnl for t in losses]))) if sum([t.net_pnl for t in losses]) != 0 else float('inf')
        exp = np.mean([t.net_pnl for t in r_trades])
        ret_sum = sum([t.net_pnl for t in r_trades])
        regime_rows.append({
            'Regime': reg, 'Trades': len(r_trades), 'Net PnL': ret_sum,
            'Win Rate': wr, 'Profit Factor': pf, 'Expectancy': exp
        })
    regime_df_out = pd.DataFrame(regime_rows)
    
    os.makedirs('reports/mean_reversion', exist_ok=True)
    yearly_df.to_csv('reports/mean_reversion/mean_reversion_yearly.csv', index=False)
    regime_df_out.to_csv('reports/mean_reversion/mean_reversion_regime.csv', index=False)
    pd.DataFrame([is_m, oos_m, comb_m], index=['IS', 'OOS', 'COMB']).to_csv('reports/mean_reversion/mean_reversion_metrics.csv')
    
    print("\n--- RESULTS ---")
    print(pd.DataFrame([is_m, oos_m, comb_m], index=['IS', 'OOS', 'COMB'])[['Total Trades', 'Total Return', 'Max Drawdown', 'Sharpe Ratio', 'Profit Factor']])
    print("\n--- YEARLY ---")
    print(yearly_df)
    print("\n--- REGIMES ---")
    print(regime_df_out)
    print(f"\nOOS Retention: {oos_m['Sharpe Ratio'] / is_m['Sharpe Ratio'] if is_m['Sharpe Ratio'] > 0 else 0}")
    
if __name__ == "__main__":
    run()
