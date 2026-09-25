import csv
import os
import sys
from pathlib import Path

import pandas as pd
import duckdb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from forge_tl.config import config

REQUIRED = [
    'BANKBEES', 'ITBEES', 'PHARMABEES', 'FMCGBEES', 'AUTOBEES', 'INFRABEES',
    'NIFTYBEES', 'JUNIORBEES', 'GOLDBEES', 'SILVERBEES', 'SETF10GILT',
    'NIFTY 50', 'INDIA VIX'
]

def manifest_report(path='data/manifests/download_manifest.csv'):
    print('\n--- Download Manifest Status ---')
    if not os.path.exists(path):
        print('Manifest not found.')
        return
    df = pd.read_csv(path)
    if df.empty:
        print('Manifest is empty.')
        return
    print(df.groupby(['type', 'status']).size().to_string())


def generate_coverage_report():
    print('=== TASK 6.5 COVERAGE REPORT ===')
    conn = duckdb.connect(config.DB_PATH, read_only=True)
    stats = conn.execute('''
        SELECT MIN(timestamp) earliest_date,
               MAX(timestamp) latest_date,
               COUNT(DISTINCT timestamp) trading_dates,
               COUNT(*) total_rows,
               COUNT(DISTINCT symbol) unique_symbols
        FROM market_bars
    ''').df()
    print('\n--- Market Bars ---')
    print(stats.to_string(index=False))

    symbols = ', '.join("'" + s.replace("'", "''") + "'" for s in REQUIRED)
    cov = conn.execute(f'''
        SELECT symbol, MIN(timestamp) first_seen, MAX(timestamp) last_seen,
               COUNT(*) observation_count
        FROM market_bars
        WHERE symbol IN ({symbols})
        GROUP BY symbol ORDER BY symbol
    ''').df()
    print('\n--- Required Symbol Coverage ---')
    print(cov.to_string(index=False) if not cov.empty else 'No required symbols found.')

    dup = conn.execute('''
        SELECT COUNT(*) FROM (
            SELECT timestamp, symbol FROM market_bars
            GROUP BY timestamp, symbol HAVING COUNT(*) > 1
        )
    ''').fetchone()[0]
    print(f'\nDuplicate (timestamp,symbol) groups: {dup}')
    conn.close()

    q_rows = 0
    q_dir = Path('data/quarantined')
    if q_dir.exists():
        for p in q_dir.glob('*.csv'):
            try:
                q_rows += len(pd.read_csv(p))
            except Exception:
                pass
    print(f'Quarantined rows: {q_rows}')
    manifest_report()

if __name__ == '__main__':
    generate_coverage_report()
