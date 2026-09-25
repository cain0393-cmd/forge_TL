import pytest
import pandas as pd
from forge_tl.data import NSEDownloader, MarketDataValidator, MarketDataDB
import os

def test_nse_url_generation():
    url = NSEDownloader.get_equity_url("2026-08-20")
    assert url == "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20260820_F_0000.csv.zip"

def test_instrument_filtering_and_validation():
    # Mock data
    data = {
        "TradDt": ["2026-08-20", "2026-08-20", "2026-08-20"],
        "TckrSymb": ["RELIANCE", "TCS", "NIFTY"],
        "OpnPric": [2500.0, 3500.0, 20000.0],
        "HghPric": [2550.0, 3550.0, 20100.0],
        "LwPric": [2450.0, 3450.0, 19900.0],
        "ClsPric": [2520.0, 3520.0, 20050.0],
        "TtlTradgVol": [10000, 5000, 0],
        "SctySrs": ["EQ", "EQ", "XX"] # XX should be filtered out
    }
    df = pd.DataFrame(data)
    df_canonical, _ = MarketDataValidator.validate_and_normalize_equity(df, "2026-08-20")
    
    assert len(df_canonical) == 2
    assert "NIFTY" not in df_canonical["symbol"].values
    
    # Check columns
    assert list(df_canonical.columns) == ["timestamp", "symbol", "open", "high", "low", "close", "volume"]

def test_validation_rejection():
    # Missing required column
    data = {
        "TradDt": ["2026-08-20"],
        "SctySrs": ["EQ"]
    }
    with pytest.raises(Exception):
        MarketDataValidator.validate_and_normalize_equity(pd.DataFrame(data), "2026-08-20")

    # Negative price
    data = {
        "TradDt": ["2026-08-20"],
        "TckrSymb": ["RELIANCE"],
        "OpnPric": [-2500.0],
        "HghPric": [2550.0],
        "LwPric": [2450.0],
        "ClsPric": [2520.0],
        "TtlTradgVol": [10000],
        "SctySrs": ["EQ"]
    }
    
    # We should test quarantine rather than an exception, as we changed the behavior
    valid_df, quar_df = MarketDataValidator.validate_and_normalize_equity(pd.DataFrame(data), "2026-08-20")
    assert len(valid_df) == 0
    assert len(quar_df) == 1

def test_duckdb_idempotency_exact_rerun():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    import forge_tl.config as config
    config.config.DB_PATH = os.path.join(tmp_path, "test.duckdb")
    
    db = MarketDataDB()
    
    data = {
        "timestamp": ["2026-08-20", "2026-08-20"],
        "symbol": ["RELIANCE", "TCS"],
        "open": [2500.0, 3500.0],
        "high": [2550.0, 3550.0],
        "low": [2450.0, 3450.0],
        "close": [2520.0, 3520.0],
        "volume": [10000, 5000]
    }
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    db.ingest(df)
    assert db.get_row_count() == 2
    
    # Ingest again
    db.ingest(df)
    assert db.get_row_count() == 2 # Should not increase
    
    # Query
    res = db.query("RELIANCE")
    assert len(res) == 1
    assert res.iloc[0]["symbol"] == "RELIANCE"

def test_duckdb_idempotency_partial_symbol():
    import tempfile
    tmp_path = tempfile.mkdtemp()
    import forge_tl.config as config
    config.config.DB_PATH = os.path.join(tmp_path, "test.duckdb")
    
    db = MarketDataDB()
    
    data1 = {
        "timestamp": ["2026-08-20", "2026-08-20", "2026-08-20"],
        "symbol": ["SYMBOL_A", "SYMBOL_B", "SYMBOL_C"],
        "open": [10.0, 20.0, 30.0],
        "high": [11.0, 21.0, 31.0],
        "low": [9.0, 19.0, 29.0],
        "close": [10.5, 20.5, 30.5],
        "volume": [100, 200, 300]
    }
    df1 = pd.DataFrame(data1)
    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    
    db.ingest(df1)
    assert db.get_row_count() == 3
    
    # Ingest only SYMBOL_A with updated prices
    data2 = {
        "timestamp": ["2026-08-20"],
        "symbol": ["SYMBOL_A"],
        "open": [10.0],
        "high": [11.0],
        "low": [9.0],
        "close": [10.8], # Updated
        "volume": [100]
    }
    df2 = pd.DataFrame(data2)
    df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    
    db.ingest(df2)
    
    assert db.get_row_count() == 3
    
    # Check SYMBOL_A is updated
    res_a = db.query("SYMBOL_A")
    assert res_a.iloc[0]["close"] == 10.8
    
    # Check SYMBOL_B remains
    res_b = db.query("SYMBOL_B")
    assert res_b.iloc[0]["close"] == 20.5
    
    # Check SYMBOL_C remains
    res_c = db.query("SYMBOL_C")
    assert res_c.iloc[0]["close"] == 30.5


def test_index_missing_ohlc_quarantine():
    import pandas as pd
    from forge_tl.data import MarketDataValidator
    
    # Mock index data resembling the 2021-02-12 INDIA VIX anomaly
    data = {
        'Index Name': ['INDIA VIX'],
        'Index Date': ['12-02-2021'],
        'Open Index Value': [None],
        'High Index Value': [None],
        'Low Index Value': [None],
        'Closing Index Value': [23.05],
        'Volume': [0]
    }
    df = pd.DataFrame(data)
    
    valid_df, quar_df = MarketDataValidator.validate_and_normalize_index(df, '2021-02-12')
    
    # Assert it was rejected from the valid dataframe
    assert len(valid_df) == 0
    # Assert it was placed in the quarantine dataframe
    assert len(quar_df) == 1
    assert quar_df.iloc[0]['close'] == 23.05
    assert quar_df.iloc[0]['symbol'] == 'INDIA VIX'
