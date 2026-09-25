import os
import glob
import pandas as pd
import numpy as np
import zipfile
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from functools import partial

RAW_DIR = 'data/raw/fno'

def process_zip(zip_path):
    try:
        with zipfile.ZipFile(zip_path) as z:
            filename = z.namelist()[0]
            df = pd.read_csv(z.open(filename))
            
        if 'INSTRUMENT' in df.columns:
            # Old format
            df = df[df['INSTRUMENT'].isin(['FUTIDX', 'FUTSTK'])].copy()
            std_df = pd.DataFrame({
                'trade_date': pd.to_datetime(df['TIMESTAMP'], format='mixed', dayfirst=True),
                'instrument': df['INSTRUMENT'],
                'symbol': df['SYMBOL'],
                'underlying': df['SYMBOL'],
                'expiry': pd.to_datetime(df['EXPIRY_DT'], format='mixed', dayfirst=True),
                'strike': df['STRIKE_PR'],
                'option_type': df['OPTION_TYP'],
                'open': df['OPEN'],
                'high': df['HIGH'],
                'low': df['LOW'],
                'close': df['CLOSE'],
                'settlement': df['SETTLE_PR'],
                'volume': df['CONTRACTS'],
                'turnover': df['VAL_INLAKH'],
                'open_interest': df['OPEN_INT'],
                'change_in_oi': df['CHG_IN_OI']
            })
        elif 'FinInstrmTp' in df.columns:
            # New format (UDiFF)
            df = df[df['FinInstrmTp'].isin(['IDF', 'STF'])].copy()
            inst_map = {'IDF': 'FUTIDX', 'STF': 'FUTSTK'}
            std_df = pd.DataFrame({
                'trade_date': pd.to_datetime(df['TradDt']),
                'instrument': df['FinInstrmTp'].map(inst_map),
                'symbol': df['TckrSymb'],
                'underlying': df['TckrSymb'],
                'expiry': pd.to_datetime(df['XpryDt']),
                'strike': df['StrkPric'],
                'option_type': df['OptnTp'],
                'open': df['OpnPric'],
                'high': df['HghPric'],
                'low': df['LwPric'],
                'close': df['ClsPric'],
                'settlement': df['SttlmPric'],
                'volume': df['TtlTradgVol'],
                'turnover': df['TtlTrfVal'],
                'open_interest': df['OpnIntrst'],
                'change_in_oi': df['ChngInOpnIntrst']
            })
        else:
            return None
            
        std_df['days_to_expiry'] = (std_df['expiry'] - std_df['trade_date']).dt.days
        std_df['contract_id'] = std_df['underlying'] + '_' + std_df['instrument'] + '_' + std_df['expiry'].dt.strftime('%Y%m%d')
        
        return std_df
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")
        return None

def build_datasets():
    zips = glob.glob(f'{RAW_DIR}/*.zip')
    print(f"Processing {len(zips)} zip files...")
    
    dfs = []
    with ProcessPoolExecutor(max_workers=max(1, cpu_count() - 1)) as executor:
        for i, df in enumerate(executor.map(process_zip, zips)):
            if df is not None:
                dfs.append(df)
            if (i+1) % 500 == 0:
                print(f"Processed {i+1} files")
                
    if not dfs:
        print("No data processed!")
        return
        
    all_df = pd.concat(dfs, ignore_index=True)
    all_df = all_df.sort_values(['contract_id', 'trade_date'])
    
    print("Building contract master...")
    master = all_df.groupby('contract_id').agg(
        underlying=('underlying', 'first'),
        instrument=('instrument', 'first'),
        expiry=('expiry', 'first'),
        first_seen=('trade_date', 'min'),
        last_seen=('trade_date', 'max')
    ).reset_index()
    
    os.makedirs('data/research', exist_ok=True)
    all_df.to_parquet('data/research/fno_daily.parquet', index=False)
    master.to_parquet('data/research/fno_contract_master.parquet', index=False)
    print("Datasets built successfully.")

if __name__ == '__main__':
    build_datasets()
