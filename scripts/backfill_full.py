import csv
import hashlib
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from forge_tl.config import config
from forge_tl.data import NSEDownloader, NSEParser, MarketDataValidator, MarketDataDB
from forge_tl.historical import ParquetExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

START_DATE = '2016-01-01'
END_DATE = '2024-12-31'
BATCH_SIZE = 25
MAX_WORKERS = 3
REQUEST_INTERVAL_SECONDS = 1.5
MANIFEST = os.path.join('data', 'manifests', 'download_manifest.csv')

class RateLimiter:
    def __init__(self, interval):
        self.interval = interval
        self.lock = threading.Lock()
        self.last = 0.0

    def wait(self):
        with self.lock:
            now = time.monotonic()
            delay = self.interval - (now - self.last)
            if delay > 0:
                time.sleep(delay)
            self.last = time.monotonic()

limiter = RateLimiter(REQUEST_INTERVAL_SECONDS)


def candidate_dates(start, end):
    d = datetime.strptime(start, '%Y-%m-%d')
    e = datetime.strptime(end, '%Y-%m-%d')
    while d <= e:
        if d.weekday() < 5:
            yield d.strftime('%Y-%m-%d')
        d += timedelta(days=1)


def sha256(path):
    return NSEDownloader.file_sha256(path) if path and os.path.exists(path) else ''


def load_manifest():
    if not os.path.exists(MANIFEST):
        return {}
    df = pd.read_csv(MANIFEST)
    out = {}
    for _, r in df.iterrows():
        out[(str(r['date']), str(r['type']))] = r.to_dict()
    return out


def save_manifest(rows):
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    fields = ['date','type','source_url','status','http_status','file','file_size','sha256','attempts','rows','error']
    existing = load_manifest()
    for row in rows:
        existing[(row['date'], row['type'])] = row
    ordered = sorted(existing.values(), key=lambda x: (x['date'], x['type']))
    with open(MANIFEST, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in ordered:
            w.writerow({k: r.get(k, '') for k in fields})


def download_one(date_str, kind, existing):
    key = (date_str, kind)
    old = existing.get(key)
    if old and old.get('status') == 'success' and old.get('file') and os.path.exists(old['file']):
        return old
    limiter.wait()
    result = NSEDownloader.download_result(kind, date_str, config.RAW_DATA_DIR)
    url = {'equity': NSEDownloader.get_equity_url, 'index': NSEDownloader.get_index_url, 'mto': NSEDownloader.get_mto_url}[kind](date_str)
    path = result.path or (old.get('file') if old else '')
    return {
        'date': date_str,
        'type': kind,
        'source_url': url,
        'status': result.status,
        'http_status': result.http_status or '',
        'file': path or '',
        'file_size': os.path.getsize(path) if path and os.path.exists(path) else 0,
        'sha256': sha256(path),
        'attempts': result.attempts,
        'rows': 0,
        'error': result.error or '',
    }


def process_record(db, record):
    if record['status'] != 'success':
        return record
    date_str, kind, path = record['date'], record['type'], record['file']
    try:
        if kind == 'equity':
            raw = NSEParser.parse_equity(path)
            valid, quar = MarketDataValidator.validate_and_normalize_equity(raw, date_str)
            if not quar.empty:
                q = os.path.join('data', 'quarantined', f'equity_{date_str}.csv')
                os.makedirs(os.path.dirname(q), exist_ok=True)
                quar.to_csv(q, index=False)
            db.ingest(valid)
            record['rows'] = len(valid)
        elif kind == 'index':
            raw = NSEParser.parse_index(path)
            valid, quar = MarketDataValidator.validate_and_normalize_index(raw, date_str)
            if not quar.empty:
                q = os.path.join('data', 'quarantined', f'index_{date_str}.csv')
                os.makedirs(os.path.dirname(q), exist_ok=True)
                quar.to_csv(q, index=False)
            db.ingest(valid)
            record['rows'] = len(valid)
        elif kind == 'mto':
            # Raw MTO is retained and source-validated; it is not part of market_bars.
            record['rows'] = len(NSEParser.parse_mto(path))
    except Exception as e:
        record['status'] = 'parse_error'
        record['error'] = str(e)
    return record


def run_backfill(start_date=START_DATE, end_date=END_DATE):
    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    existing = load_manifest()
    dates = list(candidate_dates(start_date, end_date))
    db = MarketDataDB()
    logging.info('Candidate weekdays: %d', len(dates))

    for offset in range(0, len(dates), BATCH_SIZE):
        batch = dates[offset:offset+BATCH_SIZE]
        jobs = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
            for d in batch:
                for kind in ('equity', 'index', 'mto'):
                    jobs.append(ex.submit(download_one, d, kind, existing))
            records = [f.result() for f in as_completed(jobs)]

        processed = []
        for r in sorted(records, key=lambda x: (x['date'], x['type'])):
            r = process_record(db, r)
            processed.append(r)
        save_manifest(processed)
        existing = load_manifest()
        logging.info('Progress: %d/%d candidate dates', min(offset+BATCH_SIZE, len(dates)), len(dates))

    ParquetExporter.export(db.db_path, config.PARQUET_DIR)
    logging.info('Backfill complete. DuckDB rows: %d', db.get_row_count())
    db.close()

if __name__ == '__main__':
    run_backfill()
