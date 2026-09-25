import requests
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime
import time
from calendar import month_abbr

def get_fo_bhavcopy(date_str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    dt = pd.to_datetime(date_str)
    
    # Check if weekend
    if dt.weekday() >= 5:
        print(f"{date_str} is a weekend.")
        return None
        
    year = dt.strftime('%Y')
    mon = dt.strftime('%b').upper()
    day = dt.strftime('%d')
    
    # Create a session to get cookies
    session = requests.Session()
    session.get('https://www.nseindia.com', headers=headers, timeout=10)
    
    # Old format (pre-Jul 2024)
    # URL: https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2022/JAN/fo03JAN2022bhav.csv.zip
    url_old = f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{year}/{mon}/fo{day}{mon}{year}bhav.csv.zip"
    
    # New format (post-Jul 2024)
    # URL: https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.csv.zip
    date_nodash = dt.strftime('%Y%m%d')
    url_new = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_MAC_00000_{date_nodash}_F_0000.csv.zip"
    
    try:
        if dt >= pd.to_datetime('2024-07-08'):
            print(f"Trying new format for {date_str}: {url_new}")
            res = session.get(url_new, headers=headers, timeout=10)
        else:
            print(f"Trying old format for {date_str}: {url_old}")
            res = session.get(url_old, headers=headers, timeout=10)
            
        if res.status_code == 200:
            with zipfile.ZipFile(BytesIO(res.content)) as z:
                filename = z.namelist()[0]
                df = pd.read_csv(z.open(filename))
                return df
        else:
            print(f"Status code {res.status_code} for {date_str}")
            
    except Exception as e:
        print(f"Error for {date_str}: {e}")
        
    return None

if __name__ == '__main__':
    dates = ['2016-01-01', '2018-01-01', '2020-03-02', '2022-01-03', '2024-01-01', '2024-12-31']
    for d in dates:
        df = get_fo_bhavcopy(d)
        if df is not None:
            print(f"Success for {d}. Shape: {df.shape}")
            print(df.columns.tolist())
            print(df.head(1))
            print("-" * 50)
        time.sleep(2)
