import csv

with open('data/universe/nifty50_event_ledger.csv') as f:
    reader = csv.DictReader(f)
    events = list(reader)

count = 50
print('2016-03-31 Count:', count)

events.sort(key=lambda x: x['effective_date'])

for e in events:
    if e['event_type'] in ['EXCLUSION', 'ACCELERATED_EXCLUSION']:
        count -= 1
        print(f"{e['effective_date']} EXCLUDE {e['canonical_symbol']} -> {count}")
    elif e['event_type'] in ['INCLUSION', 'ACCELERATED_INCLUSION']:
        count += 1
        print(f"{e['effective_date']} INCLUDE {e['canonical_symbol']} -> {count}")
