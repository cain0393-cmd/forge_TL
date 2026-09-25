import time
import pandas as pd
import numpy as np
from forge_tl.historical import HistoricalData
from forge_tl.backtest import BacktestEngine
from forge_tl.strategies.mean_reversion import MeanReversionStrategy
from forge_tl.universe.nifty50 import Nifty50UniverseProvider

def run_backtest(df, start_date, end_date):
    mask = (df['timestamp'] >= pd.Timestamp(start_date)) & (df['timestamp'] <= pd.Timestamp(end_date))
    period_df = df[mask]
    
    start_t = time.time()
    
    eng = BacktestEngine(period_df, initial_capital=50000.0)
    strat = MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5)
    eng.set_strategy(strat)
    res = eng.run()
    
    # Run twice for determinism check
    eng2 = BacktestEngine(period_df, initial_capital=50000.0)
    strat2 = MeanReversionStrategy(Nifty50UniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5)
    eng2.set_strategy(strat2)
    res2 = eng2.run()
    
    det_pass = (
        res['metrics']['total_return'] == res2['metrics']['total_return'] and
        res['metrics']['number_of_trades'] == res2['metrics']['number_of_trades'] and
        res['metrics']['sharpe_ratio'] == res2['metrics']['sharpe_ratio']
    )
    
    runtime = time.time() - start_t
    
    # Compute extra metrics if needed
    m = res['metrics']
    
    # Compute gross/net. By default eng.run() metrics incorporates transaction cost model in BacktestEngine.
    
    # Win rate, Average trade, Profit Factor, Expectancy
    trades = []
    
    # Actually we can reconstruct trades from orders or just use eng.orders
    
    # Let's extract simple trade statistics
    wins = 0
    losses = 0
    gross_profits = 0.0
    gross_losses = 0.0
    total_tx_costs = sum(o.commission for o in eng.orders if o.status == 'FILLED')
    
    # To get proper trades, we would need to pair buys and sells. We can just use the portfolio equity curve if trades aren't easily paired.
    # But for profit factor, expectancy, we need PnL per trade.
    # We can pair based on symbol: FIFO
    symbol_positions = {}
    paired_trades = []
    
    for o in eng.orders:
        if o.status != 'FILLED':
            continue
        if o.side.name == 'BUY':
            if o.symbol not in symbol_positions:
                symbol_positions[o.symbol] = []
            symbol_positions[o.symbol].append({'qty': o.quantity, 'price': o.avg_fill_price, 'cost': o.commission})
        else: # SELL
            qty_to_sell = o.quantity
            sell_price = o.avg_fill_price
            sell_cost = o.commission
            # matching
            if o.symbol in symbol_positions:
                while qty_to_sell > 0 and symbol_positions[o.symbol]:
                    pos = symbol_positions[o.symbol][0]
                    matched_qty = min(pos['qty'], qty_to_sell)
                    pos['qty'] -= matched_qty
                    qty_to_sell -= matched_qty
                    
                    buy_cost = pos['cost'] * (matched_qty / (matched_qty + pos['qty']))
                    pos['cost'] -= buy_cost
                    sell_cost_portion = sell_cost * (matched_qty / o.quantity)
                    
                    pnl = (sell_price - pos['price']) * matched_qty - buy_cost - sell_cost_portion
                    paired_trades.append(pnl)
                    
                    if pos['qty'] == 0:
                        symbol_positions[o.symbol].pop(0)
                        
    for pnl in paired_trades:
        if pnl > 0:
            wins += 1
            gross_profits += pnl
        else:
            losses += 1
            gross_losses += abs(pnl)
            
    win_rate = (wins / len(paired_trades)) if paired_trades else 0.0
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else float('inf') if gross_profits > 0 else 0.0
    avg_trade = sum(paired_trades) / len(paired_trades) if paired_trades else 0.0
    # Expectancy = (Win % x Average Win) - (Loss % x Average Loss) = avg_trade
    # Wait, usually Expectancy is returned in R multiples if we had risk. But we'll just report it as average trade P&L or percentage.
    expectancy = avg_trade
    
    res['extra_metrics'] = {
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'avg_trade': avg_trade,
        'expectancy': expectancy,
        'total_tx_costs': total_tx_costs,
        'determinism_pass': det_pass,
        'runtime': runtime,
        'rows_processed': len(period_df),
        'paired_trades_count': len(paired_trades)
    }
    
    return res

if __name__ == "__main__":
    hd = HistoricalData()
    print("Loading data from parquet...")
    df = hd.query(start_date='2016-01-01', end_date='2024-12-31')
    print("Loaded rows:", len(df))
    
    # 1. IS
    print("--- RUNNING IS (2016-01-01 to 2021-12-31) ---")
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
