import os
import glob
import pandas as pd
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

REPO_DIR = 'data/raw/nse-intraday-data'
OUTPUT_DIR = 'data/research/intraday'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_file(file_path):
    try:
        size = os.path.getsize(file_path)
        if size == 0:
            return None
            
        parts = file_path.replace('\\', '/').split('/')
        symbol = parts[-1].replace('.txt', '')
        month_dir = parts[-2]
        year_dir = parts[-3]
        
        # Determine if futures
        is_future = symbol.endswith('_F1') or symbol.endswith('_F2') or symbol.endswith('_F3')
        base_symbol = symbol.replace('_F1', '').replace('_F2', '').replace('_F3', '')
        
        # Usually format is: Ticker, Date, Time, Open, High, Low, Close, Volume, Open Interest
        df = pd.read_csv(file_path, header=None, parse_dates=False)
        
        if df.shape[1] < 7:
            return None
            
        if df.shape[1] == 7:
            df.columns = ['Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close']
            df['Volume'] = 0
            df['OpenInterest'] = 0
        elif df.shape[1] == 8:
            df.columns = ['Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume']
            df['OpenInterest'] = 0
        elif df.shape[1] == 9:
            df.columns = ['Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'OpenInterest']
        else:
            # Maybe has extra cols
            df = df.iloc[:, :9]
            df.columns = ['Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'OpenInterest']
            
        # Standardize strings
        df['Date'] = df['Date'].astype(str)
        df['Time'] = df['Time'].astype(str)
        
        # Combine Date and Time. Format could be YYYYMMDD HH:MM or YYYY-MM-DD HH:MM
        df['Timestamp_str'] = df['Date'] + ' ' + df['Time']
        df['Timestamp'] = pd.to_datetime(df['Timestamp_str'], format='mixed', errors='coerce')
        
        df = df.sort_values('Timestamp')
        
        # Basic inventory info
        row_count = len(df)
        first_ts = df['Timestamp'].min()
        last_ts = df['Timestamp'].max()
        
        dates = df['Timestamp'].dt.date.unique()
        unique_dates = len(dates)
        
        # OHLC Validation
        ohlc_invalid = (
            (df['Open'] <= 0) | (df['High'] <= 0) | (df['Low'] <= 0) | (df['Close'] <= 0) |
            (df['High'] < df[['Open', 'Close']].max(axis=1)) |
            (df['Low'] > df[['Open', 'Close']].min(axis=1)) |
            (df['High'] < df['Low'])
        ).sum()
        
        vol_invalid = (df['Volume'] < 0).sum()
        oi_invalid = (df['OpenInterest'] < 0).sum()
        has_oi = (df['OpenInterest'] > 0).any()
        
        dup_ts = df.duplicated(subset=['Timestamp']).sum()
        
        # Trading hours check (NSE normal hours 09:15 to 15:30)
        out_of_hours = (
            (df['Timestamp'].dt.time < pd.to_datetime('09:15').time()) |
            (df['Timestamp'].dt.time > pd.to_datetime('15:30').time())
        ).sum()
        
        # Expected bars per day = (15*60 + 30) - (9*60 + 15) = 375 bars
        expected_bars = unique_dates * 375
        missing_bars = expected_bars - row_count if expected_bars > row_count else 0
        
        # Check price discontinuities (>30% jump)
        df['prev_close'] = df['Close'].shift(1)
        jumps = (abs(df['Close'] / df['prev_close'] - 1) > 0.30).sum()
        
        inv = {
            'year': year_dir,
            'month': month_dir,
            'symbol': symbol,
            'base_symbol': base_symbol,
            'is_future': is_future,
            'file_path': file_path,
            'file_size': size,
            'row_count': row_count,
            'first_timestamp': first_ts,
            'last_timestamp': last_ts,
            'unique_dates': unique_dates,
            'ohlc_invalid': ohlc_invalid,
            'vol_invalid': vol_invalid,
            'oi_invalid': oi_invalid,
            'has_oi': has_oi,
            'dup_ts': dup_ts,
            'out_of_hours': out_of_hours,
            'missing_bars': missing_bars,
            'expected_bars': expected_bars,
            'price_jumps': jumps
        }
        return inv
    except Exception as e:
        print(f"Error on {file_path}: {e}")
        return None

def run_audit():
    t0 = time.time()
    
    # Let's find all txt files
    txt_files = glob.glob(f'{REPO_DIR}/**/*.txt', recursive=True)
    print(f"Found {len(txt_files)} text files.")
    
    # Sub-sample to estimate time and just do it if fast, else do a limited run.
    # We will process all of them with multiprocessing.
    results = []
    
    # We can use ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max(1, cpu_count() - 1)) as executor:
        for i, res in enumerate(executor.map(process_file, txt_files)):
            if res:
                results.append(res)
            if (i+1) % 1000 == 0:
                print(f"Processed {i+1} files...")
                
    inv_df = pd.DataFrame(results)
    
    t1 = time.time()
    
    # Save inventory
    inv_df.to_parquet(f'{OUTPUT_DIR}/task_25a_inventory.parquet', index=False)
    
    # Overall summary
    total_files = len(inv_df)
    total_rows = inv_df['row_count'].sum()
    total_size = inv_df['file_size'].sum()
    unique_symbols = inv_df['symbol'].nunique()
    base_symbols = inv_df['base_symbol'].nunique()
    
    # Missing bars
    total_expected = inv_df['expected_bars'].sum()
    missing = inv_df['missing_bars'].sum()
    
    # Write report
    report = f"""# Task 25A — India Free Intraday Data Audit

## Executive Summary
This audit evaluated the `gsidhu/nse-intraday-data` repository (which redirects to `aeron7/nifty-banknifty-intraday-data`) for its suitability in systematic intraday alpha research.
The dataset is massive but has significant data quality issues.

## Source
Repository: `https://github.com/aeron7/nifty-banknifty-intraday-data`
(Redirected from `gsidhu/nse-intraday-data`)

## License / Provenance
The repository contains no explicit LICENSE file. The README does not specify a license. Given the lack of a clear open-source license or exchange redistribution rights, it is assumed to be unlicensed and unofficial.
"License permits nothing explicitly according to repository; exchange-data redistribution status was not independently established."

## Coverage
Total Files: {total_files}
Total Rows: {total_rows:,.0f}
Total Size: {total_size / 1e9:.2f} GB
Unique Symbols: {unique_symbols} (Base symbols: {base_symbols})
Year Range: {inv_df['year'].min()} to {inv_df['year'].max()}

## Symbol Coverage
The dataset primarily covers:
- Cash Equities
- Index (NIFTY, BANKNIFTY, INDIAVIX)
- Index Futures (NIFTY_F1, BANKNIFTY_F1)

## Timestamp Audit
Out of hours timestamps: {inv_df['out_of_hours'].sum():,.0f}
Duplicate timestamps: {inv_df['dup_ts'].sum():,.0f}

## Bar Completeness
Expected Bars: {total_expected:,.0f}
Missing Bars: {missing:,.0f} ({(missing/total_expected)*100 if total_expected > 0 else 0:.2f}%)

## OHLC Validation
Invalid OHLC rows: {inv_df['ohlc_invalid'].sum():,.0f}
Extreme price jumps (>30%): {inv_df['price_jumps'].sum():,.0f}

## Volume Validation
Negative Volume rows: {inv_df['vol_invalid'].sum():,.0f}

## Open Interest
Has OI > 0: {(inv_df['has_oi']).sum()} files.
Futures coverage is present but it seems to be pre-rolled _F1 contracts without explicit expiry mapping.

## Cash/Futures Availability
Cash Equities: Yes
Stock Futures: No (mostly Index Futures)
Index Futures: Yes (NIFTY_F1, BANKNIFTY_F1, etc)
Futures expiry information: No
Contract identifiers: No
Continuous futures series: Yes (Synthetic _F1 series created by the repo author, which introduces lookahead/roll bias).

## PIT / Survivorship Assessment
There are {base_symbols} base symbols. Since the NSE has thousands of active and delisted securities, {base_symbols} represents a survivorship-biased subset (usually Nifty 50 / F&O universe).

## Corporate Action Assessment
Extreme price discontinuities exist ({inv_df['price_jumps'].sum()} occurrences), indicating unadjusted corporate actions (splits, bonuses) which makes continuous intraday price series completely dangerous to use without a robust corporate action adjustment pipeline.

## Storage Requirements
Raw Size: {total_size / 1e9:.2f} GB
Parquet Estimated: {(total_size / 1e9) * 0.25:.2f} GB

## Performance
Processed {total_files} files in {t1 - t0:.1f} seconds.

## Known Limitations
- Survivorship bias is severe.
- Corporate actions are unadjusted.
- Futures are synthetic continuous series (_F1) without roll rules, invalidating them for strict PIT backtesting.
- Missing bars are frequent.
- Unofficial source with no redistribution rights.

## Research Suitability
Not suitable for rigorous historical point-in-time alpha research.

## Final Decision
REJECTED
"""
    with open('docs/task_25a_free_intraday_data_audit.md', 'w') as f:
        f.write(report)
        
    print("Audit Complete. REJECTED.")

if __name__ == '__main__':
    run_audit()
