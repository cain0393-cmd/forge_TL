import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from forge_tl.data import NSEParser

raw_dir = 'd:/forge_TL/data/raw/mto'
output_dir = 'd:/forge_TL/data/research/delivery'

def run():
    files = glob.glob(os.path.join(raw_dir, '**', '*.DAT'), recursive=True)
    files.sort()
    
    print(f"Found {len(files)} MTO files.")
    
    all_dfs = []
    
    for f in files:
        basename = os.path.basename(f)
        # MTO_2016-01-01.DAT
        date_str = basename[4:14]
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            continue
            
        if not ('2016-01-01' <= date_str <= '2024-12-31'):
            continue
            
        try:
            df = NSEParser.parse_mto(f)
            df['date'] = date_str
            all_dfs.append(df)
        except Exception as e:
            print(f"Error parsing {f}: {e}")
            
    print(f"Parsed {len(all_dfs)} files.")
    
    full_df = pd.concat(all_dfs, ignore_index=True)
    
    # Check what series we have
    print("Series counts:", full_df['series'].value_counts().head(10))
    
    # Save the raw concatenated df for validation
    full_df.to_parquet('d:/forge_TL/scratch/mto_raw.parquet')

if __name__ == '__main__':
    run()
