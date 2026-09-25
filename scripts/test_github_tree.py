import requests
import json
import pandas as pd
import io

r = requests.get('https://api.github.com/repos/gsidhu/nse-intraday-data/git/trees/main?recursive=1')
res = r.json()
print("Truncated:", res.get('truncated'))

# Just fetch one file using raw.githubusercontent.com
url = "https://raw.githubusercontent.com/aeron7/nifty-banknifty-intraday-data/main/2012/DEC2012/NIFTY.txt"
resp = requests.get(url)
print("Content sample:")
print(resp.text[:500])

df = pd.read_csv(io.StringIO(resp.text), header=None)
print("Shape:", df.shape)
