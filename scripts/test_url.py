import requests

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': '*/*'
}
session.get('https://www.nseindia.com', headers=headers, timeout=10)

urls = [
    'https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2024/DEC/fo31DEC2024bhav.csv.zip',
    'https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2024/DEC/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.csv.zip',
    'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.csv.zip',
    'https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2024/DEC/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.zip',
    'https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.zip',
    'https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2024/DEC/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.csv',
    'https://archives.nseindia.com/content/historical/DERIVATIVES/2024/DEC/BhavCopy_NSE_FO_MAC_00000_20241231_F_0000.csv.zip'
]

for url in urls:
    try:
        res = session.head(url, headers=headers, timeout=5)
        print(f"{url}: {res.status_code}")
    except Exception as e:
        print(f"{url}: {e}")
