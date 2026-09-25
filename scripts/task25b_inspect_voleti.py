import requests
import json
import pandas as pd

def inspect_github(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Error fetching {url}: {r.status_code}")
        return None
    data = r.json()
    
    print(f"Repo: {data.get('full_name')}")
    print(f"Description: {data.get('description')}")
    print(f"License: {data.get('license')}")
    
    # get tree
    tree_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/main?recursive=1"
    r_tree = requests.get(tree_url)
    if r_tree.status_code == 200:
        tree = r_tree.json().get('tree', [])
        truncated = r_tree.json().get('truncated', False)
        print(f"Tree items: {len(tree)}, Truncated: {truncated}")
        
        # sample paths
        txt_files = [n for n in tree if n['path'].endswith('.txt') or n['path'].endswith('.csv')]
        print(f"Data files count: {len(txt_files)}")
        if txt_files:
            print(f"Sample paths: {[f['path'] for f in txt_files[:5]]}")
            print(f"Total size (MB): {sum(f.get('size', 0) for f in txt_files) / (1024*1024):.2f}")
    return True

inspect_github('voletiramu', 'nse-fno-1min-data')
