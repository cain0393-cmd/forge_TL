import urllib.request
import re
import os
import time

html = open('pr_page.html', encoding='utf-8').read()
links = re.findall(r'href=[\"\'](/Press_Release/[^\"\']*?\.pdf)[\"\']', html)

target_links = []
for link in links:
    if any(str(year) in link for year in range(2019, 2025)):
        target_links.append(link)

print(f'Found {len(target_links)} links for 2019-2024')

req_headers = {'User-Agent': 'Mozilla/5.0'}

for link in target_links:
    filename = link.split('/')[-1]
    path = os.path.join('prs', filename)
    if not os.path.exists(path):
        try:
            url = 'https://niftyindices.com' + link
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                with open(path, 'wb') as f:
                    f.write(response.read())
            print(f"Downloaded {filename}")
        except Exception as e:
            pass
