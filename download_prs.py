import urllib.request
import re
import os
import time

html = open('pr_page.html', encoding='utf-8').read()
links = re.findall(r'href=[\"\'](/Press_Release/[^\"\']*?\.pdf)[\"\']', html)

target_links = []
for link in links:
    if '2016' in link or '2017' in link or '2018' in link:
        target_links.append(link)

print(f'Found {len(target_links)} links for 2016-2018')

req_headers = {'User-Agent': 'Mozilla/5.0'}

if not os.path.exists('prs'):
    os.makedirs('prs')

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
            print(f'Downloaded {filename}')
            time.sleep(0.5)
        except Exception as e:
            print(f'Failed {filename}: {e}')
