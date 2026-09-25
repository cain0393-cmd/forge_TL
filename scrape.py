import urllib.request
import re

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = 'https://niftyindices.com/press-release'
try:
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8')
        links = re.findall(r'href=[\'\"](.*?\.pdf)[\'\"]', html)
        for link in links:
            if 'nifty' in link.lower() or 'index' in link.lower() or 'replacement' in link.lower() or 'change' in link.lower():
                print(link)
except Exception as e:
    print(f'Failed: {e}')
