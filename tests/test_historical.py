import os
import tempfile

import duckdb
import pandas as pd

import forge_tl.config as config
from forge_tl.data import MarketDataDB
from forge_tl.historical import ParquetExporter, HistoricalData


def test_parquet_export_and_query():
    tmp_path = tempfile.mkdtemp()

    config.config.DB_PATH = os.path.join(
        tmp_path,
        "test.duckdb",
    )

    config.config.PARQUET_DIR = os.path.join(
        tmp_path,
        "parquet",
    )

    db = MarketDataDB()

    data = {
        "timestamp": [
            "2026-08-20",
            "2026-08-20",
            "2026-08-21",
        ],
        "symbol": [
            "RELIANCE",
            "TCS",
            "RELIANCE",
        ],
        "open": [
            2500.0,
            3500.0,
            2510.0,
        ],
        "high": [
            2550.0,
            3550.0,
            2560.0,
        ],
        "low": [
            2450.0,
            3450.0,
            2460.0,
        ],
        "close": [
            2520.0,
            3520.0,
            2550.0,
        ],
        "volume": [
            10000,
            5000,
            11000,
        ],
    }

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    db.ingest(df)

    ParquetExporter.export()

    hd = HistoricalData()

    # Query all
    res_all = hd.query()
    assert len(res_all) == 3

    # Query one symbol
    res_tcs = hd.query(symbols="TCS")
    assert len(res_tcs) == 1
    assert res_tcs.iloc[0]["symbol"] == "TCS"

    # Query multiple symbols
    res_multi = hd.query(
        symbols=["TCS", "RELIANCE"]
    )
    assert len(res_multi) == 3

    # Query by date
    res_date = hd.query(
        start_date="2026-08-21"
    )

    assert len(res_date) == 1
    assert (
        res_date.iloc[0]["timestamp"].strftime(
            "%Y-%m-%d"
        )
        == "2026-08-21"
    )


def test_parquet_export_idempotency():
    tmp_path = tempfile.mkdtemp()

    config.config.DB_PATH = os.path.join(
        tmp_path,
        "test.duckdb",
    )

    config.config.PARQUET_DIR = os.path.join(
        tmp_path,
        "parquet",
    )

    db = MarketDataDB()

    data = {
        "timestamp": [
            "2026-08-20",
            "2026-08-20",
            "2026-08-21",
        ],
        "symbol": [
            "RELIANCE",
            "TCS",
            "RELIANCE",
        ],
        "open": [
            2500.0,
            3500.0,
            2510.0,
        ],
        "high": [
            2550.0,
            3550.0,
            2560.0,
        ],
        "low": [
            2450.0,
            3450.0,
            2460.0,
        ],
        "close": [
            2520.0,
            3520.0,
            2550.0,
        ],
        "volume": [
            10000,
            5000,
            11000,
        ],
    }

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    db.ingest(df)

    # First export
    ParquetExporter.export()

    hd = HistoricalData()

    res1 = hd.query()
    assert len(res1) == 3

    # Second export
    ParquetExporter.export()

    # Third export
    ParquetExporter.export()

    res2 = hd.query()

    assert len(res2) == 3

    # There must never be duplicate logical bars.
    dups = hd.detect_duplicates()

    assert dups.empty


def test_parquet_export_empty_source_removes_stale_data():
    tmp_path = tempfile.mkdtemp()

    db_path = os.path.join(
        tmp_path,
        "test.duckdb",
    )

    parquet_dir = os.path.join(
        tmp_path,
        "parquet",
    )

    config.config.DB_PATH = db_path
    config.config.PARQUET_DIR = parquet_dir

    db = MarketDataDB()

    data = {
        "timestamp": [
            "2026-08-20",
        ],
        "symbol": [
            "TEST",
        ],
        "open": [
            100.0,
        ],
        "high": [
            105.0,
        ],
        "low": [
            99.0,
        ],
        "close": [
            103.0,
        ],
        "volume": [
            1000,
        ],
    }

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Put data into DuckDB.
    db.ingest(df)

    # First export.
    ParquetExporter.export(
        db_path=db_path,
        parquet_dir=parquet_dir,
    )

    # Confirm Parquet actually contains the data.
    hd = HistoricalData(
        parquet_dir=parquet_dir
    )

    result_before = hd.query()

    assert len(result_before) == 1
    assert result_before.iloc[0]["symbol"] == "TEST"

    # Clear DuckDB.
    conn = duckdb.connect(db_path)

    try:
        conn.execute(
            "DELETE FROM market_bars"
        )
    finally:
        conn.close()

    # Export again from the now-empty DuckDB.
    ParquetExporter.export(
        db_path=db_path,
        parquet_dir=parquet_dir,
    )

    # The old Parquet data must NOT remain.
    assert (
        not os.path.exists(parquet_dir)
        or not any(
            parquet_dir_path.is_file()
            and parquet_dir_path.suffix == ".parquet"
            for parquet_dir_path
            in __import__("pathlib").Path(
                parquet_dir
            ).rglob("*")
        )
    )

    result_after = hd.query()

    assert result_after.empty


def test_duplicate_detection():
    tmp_path = tempfile.mkdtemp()

    config.config.PARQUET_DIR = os.path.join(
        tmp_path,
        "parquet",
    )

    os.makedirs(
        config.config.PARQUET_DIR,
        exist_ok=True,
    )

    # Create duplicate data.
    data = {
        "timestamp": [
            "2026-08-20",
            "2026-08-20",
        ],
        "symbol": [
            "RELIANCE",
            "RELIANCE",
        ],
        "open": [
            2500.0,
            2500.0,
        ],
        "high": [
            2550.0,
            2550.0,
        ],
        "low": [
            2450.0,
            2450.0,
        ],
        "close": [
            2520.0,
            2520.0,
        ],
        "volume": [
            10000,
            10000,
        ],
        "year": [
            2026,
            2026,
        ],
    }

    df = pd.DataFrame(data)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df.to_parquet(
        os.path.join(
            config.config.PARQUET_DIR,
            "data.parquet",
        ),
        index=False,
    )

    hd = HistoricalData()

    dups = hd.detect_duplicates()

    assert len(dups) == 1
    assert dups.iloc[0]["cnt"] == 2