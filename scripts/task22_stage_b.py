import os
import pandas as pd
import numpy as np

def run_stage_b():
    print("Loading data...")
    df = pd.read_parquet('data/research/fno_daily.parquet')
    
    # We only have a few dates, so we use the cross-section of stock futures
    df = df[df['instrument'] == 'FUTSTK'].copy()
    
    # Cash returns for forward evaluation
    cash = pd.read_parquet('data/parquet')
    cash['date'] = pd.to_datetime(cash['timestamp'])
    
    # Determine the 'front' contract for each underlying on each date
    # "nearest valid future expiry with positive remaining life"
    df = df[df['days_to_expiry'] > 0].copy()
    
    # Sort by days_to_expiry to find front month
    df = df.sort_values(['date', 'underlying', 'days_to_expiry'])
    df['contract_rank'] = df.groupby(['date', 'underlying']).cumcount()
    front = df[df['contract_rank'] == 0].copy()
    
    # Join with cash to get basis and forward returns
    # We need cash[t], cash[t+1], cash[t+5]
    cash = cash.sort_values(['symbol', 'date'])
    cash['cash_ret_1'] = cash.groupby('symbol')['close'].shift(-1) / cash['close'] - 1
    cash['cash_ret_5'] = cash.groupby('symbol')['close'].shift(-5) / cash['close'] - 1
    
    cash_subset = cash[['date', 'symbol', 'close', 'cash_ret_1', 'cash_ret_5']].rename(columns={'symbol': 'underlying', 'close': 'cash_close'})
    
    front = pd.merge(front, cash_subset, on=['date', 'underlying'], how='inner')
    
    # Signal C: Basis
    front['basis'] = front['close'] / front['cash_close'] - 1
    
    # Signal A: Price x OI (We don't have history before the 6 dates in our sample, so we can't easily compute OI change unless we had t-1).
    # Wait, our sample is isolated days. We DO have change_in_oi from the bhavcopy itself!
    # "change_in_oi can be recovered?" Yes! The bhavcopy contains CHG_IN_OI / ChngInOpnIntrst!
    # Let's calculate OI Shock as (change_in_oi / open_interest)
    # Be careful: if OI is 0, this is infinity. 
    front['oi_prev'] = front['open_interest'] - front['change_in_oi']
    front['oi_pct_change'] = np.where(front['oi_prev'] > 0, front['change_in_oi'] / front['oi_prev'], np.nan)
    
    # Cross-sectional quintiles for Basis and OI Shock
    front['basis_q'] = front.groupby('date')['basis'].transform(lambda x: pd.qcut(x, 5, labels=False, duplicates='drop'))
    front['oi_q'] = front.groupby('date')['oi_pct_change'].transform(lambda x: pd.qcut(x, 5, labels=False, duplicates='drop'))
    
    # Results storage
    results = []
    
    def analyze_signal(name, cond):
        subset = front[cond].copy()
        if len(subset) == 0:
            return
            
        res = {
            'Signal': name,
            'N': len(subset),
            'ret_1_mean': subset['cash_ret_1'].mean(),
            'ret_5_mean': subset['cash_ret_5'].mean(),
        }
        results.append(res)
        
    # Analyze Basis
    analyze_signal('High Basis (Top 20%)', front['basis_q'] == 4)
    analyze_signal('Low Basis (Bottom 20%)', front['basis_q'] == 0)
    
    # Analyze OI Shock
    analyze_signal('High OI Increase (Top 20%)', front['oi_q'] == 4)
    analyze_signal('High OI Decrease (Bottom 20%)', front['oi_q'] == 0)
    
    res_df = pd.DataFrame(results)
    res_df.to_csv('data/research/task22_results.csv', index=False)
    print(res_df)
    
    # Because this is just a limited 6-day sample, we can't legitimately claim ALPHA_SURVIVES
    # or that the results are statistically robust for OOS.
    # The prompt says: "If one or more mechanisms survive: PROMISING_NEEDS_DEEPER_TEST".
    
    report = f"""# TASK 22: F&O Alpha Study (Stage B)

## Methodology
Using the 6-day feasibility sample, a limited cross-sectional study of single-stock futures was performed.
Signals tested:
- Basis (Top vs Bottom Quintile)
- Daily OI Change (Top vs Bottom Quintile)

## Results Summary
```csv
{res_df.to_csv(index=False)}
```

Due to the limited sample size (6 days, ~900 cross-sectional observations), the results provide an indication of signal direction but lack the statistical power and continuous time-series properties required to establish a tradable alpha. 

A deeper continuous historical study is blocked by the inability to efficiently download 2,250 daily F&O Bhavcopy zip files without a dedicated automated bulk downloader, which the prompt specifically advised against ("deliberately designed to avoid another multi-hour blind download").
"""
    with open('docs/task22_fno_alpha_study.md', 'w') as f:
        f.write(report)
        
    print("Stage B Complete")

if __name__ == '__main__':
    run_stage_b()
