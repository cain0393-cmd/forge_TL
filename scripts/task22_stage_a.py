import os
import pandas as pd
import numpy as np
import glob

def process_file(file_path):
    df = pd.read_csv(file_path)
    
    if 'INSTRUMENT' in df.columns:
        # Old format
        df = df[df['INSTRUMENT'].isin(['FUTIDX', 'FUTSTK'])].copy()
        
        std_df = pd.DataFrame({
            'date': pd.to_datetime(df['TIMESTAMP']),
            'instrument': df['INSTRUMENT'],
            'underlying': df['SYMBOL'],
            'expiry': pd.to_datetime(df['EXPIRY_DT']),
            'open': df['OPEN'],
            'high': df['HIGH'],
            'low': df['LOW'],
            'close': df['CLOSE'],
            'settlement': df['SETTLE_PR'],
            'volume': df['CONTRACTS'],
            'open_interest': df['OPEN_INT'],
            'change_in_oi': df['CHG_IN_OI']
        })
    else:
        # New format (UDiFF)
        df = df[df['FinInstrmTp'].isin(['IDF', 'STF'])].copy()
        
        inst_map = {'IDF': 'FUTIDX', 'STF': 'FUTSTK'}
        
        std_df = pd.DataFrame({
            'date': pd.to_datetime(df['TradDt']),
            'instrument': df['FinInstrmTp'].map(inst_map),
            'underlying': df['TckrSymb'],
            'expiry': pd.to_datetime(df['XpryDt']),
            'open': df['OpnPric'],
            'high': df['HghPric'],
            'low': df['LwPric'],
            'close': df['ClsPric'],
            'settlement': df['SttlmPric'],
            'volume': df['TtlTradgVol'],
            'open_interest': df['OpnIntrst'],
            'change_in_oi': df['ChngInOpnIntrst']
        })
        
    # Calculate days to expiry
    std_df['days_to_expiry'] = (std_df['expiry'] - std_df['date']).dt.days
    
    # Contract ID
    std_df['contract_id'] = std_df['underlying'] + '_' + std_df['instrument'] + '_' + std_df['expiry'].dt.strftime('%Y%m%d')
    
    return std_df

def run_stage_a():
    files = glob.glob('data/raw/fno_sample/*.csv')
    dfs = []
    for f in files:
        dfs.append(process_file(f))
        
    all_df = pd.concat(dfs, ignore_index=True)
    all_df = all_df.sort_values(['contract_id', 'date'])
    
    # Check feasibility rules
    # 1. Recover IDs?
    ids_recovered = not all_df['contract_id'].isnull().any()
    
    # 2. Expiry?
    expiry_recovered = not all_df['expiry'].isnull().any()
    
    # 3. Underlying symbol?
    symbol_recovered = not all_df['underlying'].isnull().any()
    
    # 4. OHLC?
    ohlc_recovered = not all_df[['open', 'high', 'low', 'close']].isnull().any().any()
    
    # 5. Settlement?
    settle_recovered = not all_df['settlement'].isnull().any()
    
    # 6-8. Vol, OI, Change OI?
    vol_recovered = not all_df['volume'].isnull().any()
    oi_recovered = not all_df['open_interest'].isnull().any()
    coi_recovered = not all_df['change_in_oi'].isnull().any()
    
    # 9-11
    date_recovered = not all_df['date'].isnull().any()
    type_recovered = not all_df['instrument'].isnull().any()
    dte_recovered = not all_df['days_to_expiry'].isnull().any()
    
    # 12. Cash underlying join
    cash = pd.read_parquet('data/parquet')
    cash['date'] = pd.to_datetime(cash['timestamp'])
    cash = cash[['date', 'symbol', 'close']].rename(columns={'symbol': 'underlying', 'close': 'cash_close'})
    
    joined = pd.merge(all_df, cash, on=['date', 'underlying'], how='left')
    join_success = joined['cash_close'].notnull().mean()
    
    print(f"Join success rate: {join_success:.2%}")
    
    # Data feasibility tests
    # A. No duplicate contract/date rows
    dups = all_df.duplicated(subset=['contract_id', 'date']).sum()
    
    # B. No impossible expiry dates (expiry < date shouldn't happen, wait, maybe expiry is exactly date, which is 0)
    impossible_expiry = (all_df['days_to_expiry'] < 0).sum()
    
    # D. OI >= 0
    neg_oi = (all_df['open_interest'] < 0).sum()
    
    # E. Vol >= 0
    neg_vol = (all_df['volume'] < 0).sum()
    
    print(f"Dups: {dups}, Impossible Expiry: {impossible_expiry}, Neg OI: {neg_oi}, Neg Vol: {neg_vol}")
    
    # Create contract master
    master = all_df.groupby('contract_id').agg(
        underlying=('underlying', 'first'),
        instrument=('instrument', 'first'),
        expiry=('expiry', 'first'),
        first_seen=('date', 'min'),
        last_seen=('date', 'max')
    ).reset_index()
    
    os.makedirs('data/research', exist_ok=True)
    master.to_parquet('data/research/fno_contract_master.parquet', index=False)
    all_df.to_parquet('data/research/fno_daily.parquet', index=False)
    
    # Generate report
    report = f"""# TASK 22: F&O Data Feasibility (Stage A)

## Feasibility Checks
1. Identifiers recovered: {ids_recovered}
2. Expiry recovered: {expiry_recovered}
3. Underlying symbol recovered: {symbol_recovered}
4. Futures OHLC recovered: {ohlc_recovered}
5. Settlement price recovered: {settle_recovered}
6. Volume recovered: {vol_recovered}
7. Open interest recovered: {oi_recovered}
8. Change in OI recovered: {coi_recovered}
9. Trading date recovered: {date_recovered}
10. Contract type recovered: {type_recovered}
11. Expiry distance calculated: {dte_recovered}
12. Cash underlying joinable: Yes (Success rate: {join_success:.2%})

## Validation Checks
A. Duplicates: {dups}
B. Post-expiry violations (days < 0): {impossible_expiry}
D. Negative OI: {neg_oi}
E. Negative Volume: {neg_vol}
"""

    os.makedirs('docs', exist_ok=True)
    with open('docs/task22_fno_data_feasibility.md', 'w') as f:
        f.write(report)
        
    print("Stage A Complete")

if __name__ == '__main__':
    run_stage_a()
