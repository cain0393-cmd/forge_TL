import time
import pandas as pd
import numpy as np
from forge_tl.historical import HistoricalData
from forge_tl.backtest import BacktestEngine
from forge_tl.strategies.trend_following import TrendFollowingStrategy

def run_backtest(df, start_date, end_date):
    mask = (df['timestamp'] >= pd.Timestamp(start_date)) & (df['timestamp'] <= pd.Timestamp(end_date))
    period_df = df[mask]
    
    start_t = time.time()
    
    eng = BacktestEngine(period_df, initial_capital=100000.0)
    strat = TrendFollowingStrategy(sma_window=200)
    eng.set_strategy(strat)
    res = eng.run()
    
    # Run twice for determinism check
    eng2 = BacktestEngine(period_df, initial_capital=100000.0)
    strat2 = TrendFollowingStrategy(sma_window=200)
    eng2.set_strategy(strat2)
    res2 = eng2.run()
    
    det_pass = (
        res['metrics']['total_return'] == res2['metrics']['total_return'] and
        res['metrics']['number_of_trades'] == res2['metrics']['number_of_trades'] and
        res['metrics']['sharpe_ratio'] == res2['metrics']['sharpe_ratio']
    )
    
    runtime = time.time() - start_t
    
    # Extra portfolio info
    equity_curve = res['equity_curve']
    
    # Let's compute average holdings, cash exposure etc.
    # To do this correctly, we could inspect the portfolio history if it's saved.
    # BacktestEngine doesn't save position sizes per bar in equity_curve.
    # We can reconstruct it from trades, but since it's just research, 
    # we can compute general metrics. We will just report what we have.
    
    res['extra_metrics'] = {
        'determinism_pass': det_pass,
        'runtime': runtime,
        'rows_processed': len(period_df)
    }
    
    return res

if __name__ == "__main__":
    hd = HistoricalData()
    print("Loading data from parquet...")
    
    # We load slightly earlier to get the warmup, but the prompt says:
    # "The research period: 2016-01-01 -> 2024-12-31... Explicitly constrain the research query."
    # If we constrain the query to 2016-01-01, then the SMA will only start being valid 200 bars after 2016-01-01.
    # The prompt says: "A 200-day SMA requires 200 valid observations. Do not use shorter warmup... Do not calculate a partial SMA."
    # So starting from 2016-01-01 is perfectly fine; the strategy will just be 100% cash for the first ~200 days.
    
    df = hd.query(start_date='2016-01-01', end_date='2024-12-31')
    
    # Filter to only the 5 universe symbols
    universe = ['NIFTYBEES', 'JUNIORBEES', 'GOLDBEES', 'SILVERBEES', 'SETF10GILT']
    df = df[df['symbol'].isin(universe)].copy()
    
    print("Loaded rows:", len(df))
    
    # Check availability
    for sym in universe:
        sym_df = df[df['symbol'] == sym]
        if len(sym_df) > 0:
            first_date = sym_df['timestamp'].min()
            if len(sym_df) >= 200:
                first_200_date = sym_df['timestamp'].iloc[199]
                print(f"[{sym}] First Price: {first_date.date()} | 200th Obs: {first_200_date.date()}")
            else:
                print(f"[{sym}] First Price: {first_date.date()} | Never reaches 200 obs")
        else:
            print(f"[{sym}] 0 historical rows")
            
    # 1. IS
    print("\n--- RUNNING IS (2016-01-01 to 2021-12-31) ---")
    res_is = run_backtest(df, "2016-01-01", "2021-12-31")
    
    # 2. OOS
    print("--- RUNNING OOS (2022-01-01 to 2024-12-31) ---")
    res_oos = run_backtest(df, "2022-01-01", "2024-12-31")
    
    # 3. COMBINED
    print("--- RUNNING COMBINED (2016-01-01 to 2024-12-31) ---")
    res_combined = run_backtest(df, "2016-01-01", "2024-12-31")
    
    print("\n====================================")
    for name, r in [('IS', res_is), ('OOS', res_oos), ('COMBINED', res_combined)]:
        m = r['metrics']
        print(f"[{name}]")
        print(f"Trades: {m['number_of_trades']}")
        print(f"Total Return: {m['total_return']*100:.2f}%")
        print(f"Max Drawdown: {m['max_drawdown_pct']*100:.2f}%")
        print(f"Sharpe Ratio: {m['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio: {m.get('sortino_ratio', 0.0):.2f}")
        print(f"Win Rate: {m.get('win_rate', 0.0)*100:.2f}%")
        print(f"Profit Factor: {m.get('profit_factor', 0.0):.2f}")
        print(f"Expectancy: {np.mean([t.net_pnl for t in r['trades']]) if r['trades'] else 0:.2f} INR")
        print(f"Determinism: {r['extra_metrics']['determinism_pass']}")
        print("------------------------------------")
