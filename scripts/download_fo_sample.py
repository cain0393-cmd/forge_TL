import requests
import pandas as pd
from io import BytesIO
import zipfile
import os

def download_fo_sample():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    session = requests.Session()
    session.get('https://www.nseindia.com', headers=headers, timeout=10)
    
    os.makedirs('data/raw/fno_sample', exist_ok=True)
    
    dates = [
        ('2016-01-01', 'old'),
        ('2018-01-01', 'old'),
        ('2020-03-02', 'old'),
        ('2022-01-03', 'old'),
        ('2024-01-01', 'old'),
        ('2024-12-31', 'new')
    ]
    
    for d, fmt in dates:
        dt = pd.to_datetime(d)
        year = dt.strftime('%Y')
        mon = dt.strftime('%b').upper()
        day = dt.strftime('%d')
        date_nodash = dt.strftime('%Y%m%d')
        
        if fmt == 'old':
            url = f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{year}/{mon}/fo{day}{mon}{year}bhav.csv.zip"
        else:
            url = f"https://nsearchives.nseindia.com/content/historical/DERIVATIVES/{year}/{mon}/BhavCopy_NSE_FO_MAC_00000_{date_nodash}_F_0000.csv.zip"
            
        print(f"Fetching {url}")
        res = session.get(url, headers=headers, timeout=10)
        print(res.status_code)
        if res.status_code == 200:
            with zipfile.ZipFile(BytesIO(res.content)) as z:
                filename = z.namelist()[0]
                df = pd.read_csv(z.open(filename))
                out_path = f"data/raw/fno_sample/fno_{date_nodash}.csv"
                df.to_csv(out_path, index=False)
                print(f"Saved {out_path}")

if __name__ == '__main__':
    download_fo_sample()
