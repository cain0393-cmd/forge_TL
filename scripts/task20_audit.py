import pandas as pd
import numpy as np
from pathlib import Path
from forge_tl.universe.nifty50 import Nifty50UniverseProvider
import glob

def run_audit():
    print("Loading data...")
    df = pd.read_parquet('data/parquet')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Load PIT Nifty 50 provider
    provider = Nifty50UniverseProvider()
    
    # We only care about PIT Nifty 50. Let's filter first to speed up.
    dates = df['timestamp'].unique()
    dates = np.sort(dates)
    
    print("Filtering to PIT Nifty 50...")
    # This might be slow if we do it row by row. Better to create a membership mask.
    # Or just get the universe for each date, and join.
    universe_records = []
    for d in dates:
        dt = pd.to_datetime(d)
        if dt.date() >= pd.to_datetime('2016-03-31').date() and dt.date() <= pd.to_datetime('2024-12-31').date():
            members = provider.get_universe(dt.date())
            for m in members:
                universe_records.append({'timestamp': dt, 'symbol': m})
                
    universe_df = pd.DataFrame(universe_records)
    
    pit_df = pd.merge(df, universe_df, on=['timestamp', 'symbol'], how='inner')
    
    print(f"Total PIT rows: {len(pit_df)}")
    
    # Check for missing OHLC
    missing = pit_df[['open', 'high', 'low', 'close']].isna().sum()
    print("Missing OHLC:")
    print(missing)
    
    # Check for zero/negative prices
    neg_prices = (pit_df[['open', 'high', 'low', 'close']] <= 0).sum()
    print("\nZero or Negative Prices:")
    print(neg_prices)
    
    # Check for zero volume
    zero_vol = (pit_df['volume'] == 0).sum()
    print(f"\nZero Volume count: {zero_vol}")
    
    # Duplicates
    dups = pit_df.duplicated(subset=['timestamp', 'symbol']).sum()
    print(f"\nDuplicate symbol/date: {dups}")
    
    # Impossible OHLC
    impossible = ((pit_df['high'] < pit_df['low']) | 
                  (pit_df['high'] < pit_df['open']) | 
                  (pit_df['high'] < pit_df['close']) | 
                  (pit_df['low'] > pit_df['open']) | 
                  (pit_df['low'] > pit_df['close'])).sum()
    print(f"\nImpossible OHLC: {impossible}")
    
    # Sort for returns
    pit_df = pit_df.sort_values(['symbol', 'timestamp'])
    
    # Jumps (Corporate Actions proxies)
    # Overnight return < -30%
    pit_df['prev_close'] = pit_df.groupby('symbol')['close'].shift(1)
    pit_df['on_ret'] = pit_df['open'] / pit_df['prev_close'] - 1
    
    jumps_down = (pit_df['on_ret'] < -0.30).sum()
    jumps_up = (pit_df['on_ret'] > 0.50).sum()
    
    print(f"\nJumps down (< -30%): {jumps_down}")
    print(f"Jumps up (> +50%): {jumps_up}")
    
    print("\nSample jumps down:")
    print(pit_df[pit_df['on_ret'] < -0.30][['timestamp', 'symbol', 'prev_close', 'open', 'on_ret']].head(10))

if __name__ == '__main__':
    run_audit()
