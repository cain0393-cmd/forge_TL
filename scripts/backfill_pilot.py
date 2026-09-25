import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from forge_tl.data import NSEDownloader, NSEParser, MarketDataValidator, MarketDataDB
from forge_tl.historical import ParquetExporter
from forge_tl.config import config

def run_pilot():
    print("=== TASK 6.5 PILOT ===")
    pilot_dates = [
        "2016-01-01",  # Legacy format
        "2020-01-01",  # Legacy format
        "2024-07-08",  # Transition date / UDiFF
        "2024-07-09",  # Modern format
        "2024-08-01"   # Modern format
    ]

    db = MarketDataDB()
    total_valid = 0
    total_quarantined = 0

    os.makedirs('data/quarantined', exist_ok=True)
    os.makedirs('data/manifests', exist_ok=True)

    manifest_records = []

    for dt_str in pilot_dates:
        print(f"\nProcessing {dt_str}...")
        
        # 1. Equity
        eq_zip = NSEDownloader.download_equity(dt_str, config.RAW_DATA_DIR)
        if eq_zip:
            print(f"  [Equity] Downloaded: {eq_zip}")
            df_eq_raw = NSEParser.parse_equity(eq_zip)
            df_eq_valid, df_eq_quar = MarketDataValidator.validate_and_normalize_equity(df_eq_raw, dt_str)
            db.ingest(df_eq_valid)
            total_valid += len(df_eq_valid)
            total_quarantined += len(df_eq_quar)
            
            if not df_eq_quar.empty:
                q_path = os.path.join('data/quarantined', f'equity_{dt_str}.csv')
                df_eq_quar.to_csv(q_path, index=False)
                
            manifest_records.append({'date': dt_str, 'type': 'equity', 'status': 'success', 'file': eq_zip, 'rows': len(df_eq_valid)})
        else:
            print(f"  [Equity] Failed / Not found for {dt_str}")
            manifest_records.append({'date': dt_str, 'type': 'equity', 'status': 'missing'})

        # 2. Index
        idx_csv = NSEDownloader.download_index(dt_str, config.RAW_DATA_DIR)
        if idx_csv:
            print(f"  [Index] Downloaded: {idx_csv}")
            df_idx_raw = NSEParser.parse_index(idx_csv)
            df_idx_valid, df_idx_quar = MarketDataValidator.validate_and_normalize_index(df_idx_raw, dt_str)
            db.ingest(df_idx_valid)
            total_valid += len(df_idx_valid)
            total_quarantined += len(df_idx_quar)
            
            if not df_idx_quar.empty:
                q_path = os.path.join('data/quarantined', f'index_{dt_str}.csv')
                df_idx_quar.to_csv(q_path, index=False)
                
            manifest_records.append({'date': dt_str, 'type': 'index', 'status': 'success', 'file': idx_csv, 'rows': len(df_idx_valid)})
        else:
            print(f"  [Index] Failed / Not found for {dt_str}")
            manifest_records.append({'date': dt_str, 'type': 'index', 'status': 'missing'})
            
        # 3. MTO
        mto_dat = NSEDownloader.download_mto(dt_str, config.RAW_DATA_DIR)
        if mto_dat:
            print(f"  [MTO] Downloaded: {mto_dat}")
            # Just parsing to test
            df_mto = NSEParser.parse_mto(mto_dat)
            manifest_records.append({'date': dt_str, 'type': 'mto', 'status': 'success', 'file': mto_dat, 'rows': len(df_mto)})
        else:
            print(f"  [MTO] Failed / Not found for {dt_str}")
            manifest_records.append({'date': dt_str, 'type': 'mto', 'status': 'missing'})

    print("\n--- Pilot Complete ---")
    print(f"DuckDB row count: {db.get_row_count()}")
    print(f"Quarantined rows: {total_quarantined}")
    
    print("\nExporting Parquet...")
    ParquetExporter.export(db.db_path, config.PARQUET_DIR)
    print("Export Complete.")

    pd.DataFrame(manifest_records).to_csv(os.path.join('data/manifests', 'pilot_manifest.csv'), index=False)
    db.close()

if __name__ == '__main__':
    run_pilot()
