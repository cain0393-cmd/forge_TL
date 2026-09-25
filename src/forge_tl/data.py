import os
import requests
import zipfile
import pandas as pd
import duckdb
import time
import logging
import hashlib
from dataclasses import dataclass
from datetime import datetime
from forge_tl.config import config

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class DownloadResult:
    path: str | None
    status: str
    http_status: int | None = None
    error: str | None = None
    attempts: int = 0


class NSEDownloader:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    @staticmethod
    def get_equity_url(date_str: str) -> str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if dt >= datetime(2024, 7, 8):
            return f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{dt:%Y%m%d}_F_0000.csv.zip"
        mon = dt.strftime("%b").upper()
        return f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{dt.year}/{mon}/cm{dt:%d}{mon}{dt:%Y}bhav.csv.zip"

    @staticmethod
    def get_index_url(date_str: str) -> str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"https://nsearchives.nseindia.com/content/indices/ind_close_all_{dt:%d%m%Y}.csv"

    @staticmethod
    def get_mto_url(date_str: str) -> str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"https://nsearchives.nseindia.com/archives/equities/mto/MTO_{dt:%d%m%Y}.DAT"

    @staticmethod
    def _download_with_retry(url: str, output_path: str, max_retries: int = 3, min_interval: float = 1.0) -> DownloadResult:
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return DownloadResult(output_path, "success", attempts=0)

        session = requests.Session()
        last_error = None
        last_status = None
        for attempt in range(1, max_retries + 1):
            try:
                time.sleep(min_interval)
                session.get("https://www.nseindia.com", headers=NSEDownloader.HEADERS, timeout=15)
                time.sleep(min_interval)
                response = session.get(url, headers=NSEDownloader.HEADERS, timeout=30)
                last_status = response.status_code
                if response.status_code == 200 and response.content:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    tmp_path = output_path + ".part"
                    with open(tmp_path, 'wb') as f:
                        f.write(response.content)
                    os.replace(tmp_path, output_path)
                    return DownloadResult(output_path, "success", 200, attempts=attempt)
                if response.status_code in (404, 410):
                    return DownloadResult(None, "not_available", response.status_code, attempts=attempt)
                if response.status_code in (401, 403, 408, 425, 429) or response.status_code >= 500:
                    last_error = f"HTTP {response.status_code}"
                else:
                    return DownloadResult(None, "http_error", response.status_code, attempts=attempt)
            except requests.RequestException as e:
                last_error = str(e)
            except Exception as e:
                last_error = str(e)
            if attempt < max_retries:
                time.sleep(2 ** (attempt - 1))
        return DownloadResult(None, "download_error", last_status, last_error, max_retries)

    @staticmethod
    def download_result(kind: str, date_str: str, raw_dir: str) -> DownloadResult:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if kind == "equity":
            path = os.path.join(raw_dir, "equity", str(dt.year), f"{dt.month:02d}", f"BhavCopy_{date_str}.zip")
            url = NSEDownloader.get_equity_url(date_str)
        elif kind == "index":
            path = os.path.join(raw_dir, "index", str(dt.year), f"{dt.month:02d}", f"ind_close_all_{date_str}.csv")
            url = NSEDownloader.get_index_url(date_str)
        elif kind == "mto":
            path = os.path.join(raw_dir, "mto", str(dt.year), f"{dt.month:02d}", f"MTO_{date_str}.DAT")
            url = NSEDownloader.get_mto_url(date_str)
        else:
            raise ValueError(f"Unsupported download kind: {kind}")
        return NSEDownloader._download_with_retry(url, path)

    @staticmethod
    def download_equity(date_str: str, raw_dir: str) -> str | None:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        path = os.path.join(raw_dir, "equity", str(dt.year), f"{dt.month:02d}", f"BhavCopy_{date_str}.zip")
        return NSEDownloader._download_with_retry(NSEDownloader.get_equity_url(date_str), path).path

    @staticmethod
    def download_index(date_str: str, raw_dir: str) -> str | None:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        path = os.path.join(raw_dir, "index", str(dt.year), f"{dt.month:02d}", f"ind_close_all_{date_str}.csv")
        return NSEDownloader._download_with_retry(NSEDownloader.get_index_url(date_str), path).path

    @staticmethod
    def download_mto(date_str: str, raw_dir: str) -> str | None:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        path = os.path.join(raw_dir, "mto", str(dt.year), f"{dt.month:02d}", f"MTO_{date_str}.DAT")
        return NSEDownloader._download_with_retry(NSEDownloader.get_mto_url(date_str), path).path

    @staticmethod
    def file_sha256(path: str) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()

class NSEParser:
    @staticmethod
    def parse_equity(zip_path: str) -> pd.DataFrame:
        with zipfile.ZipFile(zip_path, 'r') as z:
            target_csv = None
            for f in z.namelist():
                name_lower = f.lower()
                if name_lower.startswith('bhavcopy_nse_cm') and name_lower.endswith('.csv'):
                    target_csv = f
                    break
                elif name_lower.startswith('cm') and name_lower.endswith('bhav.csv'):
                    target_csv = f
                    break
            
            if not target_csv:
                raise Exception(f"Could not identify the intended CM Bhavcopy payload in the archive {zip_path}.")
            
            with z.open(target_csv) as f:
                df = pd.read_csv(f)
        return df

    @staticmethod
    def parse_index(csv_path: str) -> pd.DataFrame:
        return pd.read_csv(csv_path)

    @staticmethod
    def parse_mto(dat_path: str) -> pd.DataFrame:
        rows = []
        with open(dat_path, 'r', encoding='latin-1') as f:
            for line in f:
                parts = [p.strip() for p in line.rstrip('\n\r').split(',')]
                if parts and parts[0] == '20' and len(parts) >= 7:
                    rows.append(parts)
        return pd.DataFrame(rows, columns=[
            'record_type', 'sr_no', 'symbol', 'series',
            'quantity_traded', 'deliverable_quantity', 'delivery_pct'
        ])

class MarketDataValidator:
    REQUIRED_COLS = ["timestamp", "symbol", "open", "high", "low", "close", "volume"]

    @staticmethod
    def validate_and_normalize_equity(df: pd.DataFrame, date_str: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Returns (valid_df, quarantined_df)"""
        df = df.copy()
        df.columns = df.columns.str.strip()

        col_map = {
            # Modern UDiFF
            "TradDt": "timestamp",
            "TckrSymb": "symbol",
            "OpnPric": "open",
            "HghPric": "high",
            "LwPric": "low",
            "ClsPric": "close",
            "TtlTradgVol": "volume",
            "SctySrs": "SctySrs",
            
            # Legacy
            "TIMESTAMP": "timestamp",
            "SYMBOL": "symbol",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close",
            "TOTTRDQTY": "volume",
            "SERIES": "SctySrs"
        }

        actual_cols = df.columns.tolist()
        mapped_cols = {}
        for expected, canonical in col_map.items():
            for ac in actual_cols:
                if ac.lower() == expected.lower():
                    mapped_cols[ac] = canonical
                    break
            
        df = df.rename(columns=mapped_cols)

        if "SctySrs" in df.columns:
            df = df[df["SctySrs"] == "EQ"].copy()
            df = df.drop(columns=["SctySrs"])

        for col in MarketDataValidator.REQUIRED_COLS:
            if col not in df.columns:
                raise Exception(f"Missing required canonical column: {col}")

        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=False)
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Identify invalid rows
        invalid_mask = pd.Series(False, index=df.index)
        
        # Null checks
        invalid_mask |= df['timestamp'].isnull()
        invalid_mask |= df['symbol'].isnull()
        for col in ['open', 'high', 'low', 'close', 'volume']:
            invalid_mask |= df[col].isnull()
            
        # Negative checks
        for col in ['open', 'high', 'low', 'close', 'volume']:
            invalid_mask |= (df[col] <= 0) if col != 'volume' else (df[col] < 0)

        # Impossible OHLC relationships
        invalid_mask |= (df['high'] < df['low'])
        invalid_mask |= (df['high'] < df['open'])
        invalid_mask |= (df['high'] < df['close'])
        invalid_mask |= (df['low'] > df['open'])
        invalid_mask |= (df['low'] > df['close'])

        valid_df = df[~invalid_mask][MarketDataValidator.REQUIRED_COLS].copy()
        quarantined_df = df[invalid_mask].copy()

        return valid_df, quarantined_df

    @staticmethod
    def validate_and_normalize_index(df: pd.DataFrame, date_str: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df.columns = df.columns.str.strip()

        col_map = {
            "Index Name": "symbol",
            "Index Date": "timestamp",
            "Open Index Value": "open",
            "High Index Value": "high",
            "Low Index Value": "low",
            "Closing Index Value": "close",
            "Volume": "volume"
        }
        
        actual_cols = df.columns.tolist()
        mapped_cols = {}
        for expected, canonical in col_map.items():
            for ac in actual_cols:
                if ac.lower() == expected.lower():
                    mapped_cols[ac] = canonical
                    break
        df = df.rename(columns=mapped_cols)

        # Timestamps for indices often dd-mm-yyyy format in old files
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', dayfirst=True)

        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
        else:
            df['volume'] = 0

        # For index, we only care about Nifty 50 and India VIX
        if 'symbol' in df.columns:
            df['symbol'] = df['symbol'].str.strip().str.upper()
            df = df[df['symbol'].isin(['NIFTY 50', 'INDIA VIX'])].copy()

        invalid_mask = pd.Series(False, index=df.index)
        invalid_mask |= df['timestamp'].isnull()
        for col in ['open', 'high', 'low', 'close']:
            invalid_mask |= df[col].isnull()
            invalid_mask |= df[col] <= 0
        invalid_mask |= df['high'] < df['low']
        invalid_mask |= df['high'] < df['open']
        invalid_mask |= df['high'] < df['close']
        invalid_mask |= df['low'] > df['open']
        invalid_mask |= df['low'] > df['close']
        
        valid_df = df[~invalid_mask].copy()
        if not valid_df.empty:
            valid_df = valid_df[MarketDataValidator.REQUIRED_COLS]
            
        quarantined_df = df[invalid_mask].copy()
        return valid_df, quarantined_df

class MarketDataDB:
    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path else config.DB_PATH
        self.conn = duckdb.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS market_bars (
                timestamp DATE,
                symbol VARCHAR,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE,
                PRIMARY KEY (timestamp, symbol)
            )
        """)

    def ingest(self, df: pd.DataFrame):
        if df.empty:
            return

        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
        df = df.drop_duplicates(subset=["timestamp", "symbol"], keep="last")

        self.conn.execute("CREATE TEMP TABLE tmp_ingest AS SELECT * FROM df")
        self.conn.execute("""
            INSERT INTO market_bars 
            SELECT * FROM tmp_ingest 
            ON CONFLICT (timestamp, symbol) DO UPDATE SET 
                open = excluded.open,
                high = excluded.high,
                low = excluded.low,
                close = excluded.close,
                volume = excluded.volume
        """)
        self.conn.execute("DROP TABLE tmp_ingest")

    def query(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        query = "SELECT * FROM market_bars WHERE symbol = ?"
        params = [symbol]
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        query += " ORDER BY timestamp ASC"
        return self.conn.execute(query, params).df()

    def get_row_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM market_bars").fetchone()[0]

    def close(self):
        self.conn.close()
