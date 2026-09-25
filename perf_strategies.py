import time
import pandas as pd
from forge_tl.historical import HistoricalData
from forge_tl.backtest import BacktestEngine
from forge_tl.strategies.base import UniverseProvider, EarningsEventProvider
from forge_tl.universe.nifty50 import Nifty50UniverseProvider
from forge_tl.strategies.dual_momentum import DualMomentumStrategy
from forge_tl.strategies.trend_following import TrendFollowingStrategy
from forge_tl.strategies.mean_reversion import MeanReversionStrategy
from forge_tl.strategies.pead import PEADStrategy

class EmptyEarningsEventProvider(EarningsEventProvider):
    def get_events_available_by(self, timestamp: pd.Timestamp):
        return []

def run_integration():
    hd = HistoricalData()
    print("Loading data...")
    df = hd.query()
    print(f"Data rows: {len(df)}")
    
    if df.empty:
        print("No data available.")
        return
        
    strategies = [
        ("Dual Momentum", DualMomentumStrategy()),
        ("Trend Following", TrendFollowingStrategy()),
        ("Mean Reversion", MeanReversionStrategy(Nifty50UniverseProvider())),
        ("PEAD", PEADStrategy(EmptyEarningsEventProvider()))
    ]
    
    print("\n--- Integration Performance ---")
    for name, strat in strategies:
        # Run 1
        eng1 = BacktestEngine(df, initial_capital=50000.0)
        eng1.set_strategy(strat)
        res1 = eng1.run()
        
        # Run 2 for Determinism Check
        eng2 = BacktestEngine(df, initial_capital=50000.0)
        eng2.set_strategy(strat) # Strategy has state? We should instantiate a new one for determinism check
        
        if name == "Dual Momentum":
            strat2 = DualMomentumStrategy()
        elif name == "Trend Following":
            strat2 = TrendFollowingStrategy()
        elif name == "Mean Reversion":
            strat2 = MeanReversionStrategy(Nifty50UniverseProvider())
        else:
            strat2 = PEADStrategy(EmptyEarningsEventProvider())
            
        eng2.set_strategy(strat2)
        res2 = eng2.run()
        
        # Check Determinism
        assert res1['metrics']['number_of_trades'] == res2['metrics']['number_of_trades']
        assert res1['metrics']['total_return'] == res2['metrics']['total_return']
        assert len(res1['orders']) == len(res2['orders'])
        
        m = res1['metrics']
        print(f"\n[{name}]")
        print(f"Trades: {m['number_of_trades']}")
        print(f"Total Return: {m['total_return']*100:.2f}%")
        print(f"Sharpe: {m['sharpe_ratio']:.2f}")
        print(f"Throughput: {m['rows_per_second']:.0f} rows/s")
        print("Determinism: PASS")

if __name__ == "__main__":
    run_integration()
