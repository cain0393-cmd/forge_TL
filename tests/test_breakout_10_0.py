import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.run_research_breakout_10_0 import calculate_signals
from forge_tl.universe.nifty50 import Nifty50UniverseProvider

def create_mock_df(size=250):
    np.random.seed(42)
    return pd.DataFrame({
        'date': pd.date_range('2015-01-01', periods=size, freq='B'),
        'symbol': 'MOCK',
        'open': np.random.uniform(90, 110, size),
        'high': np.random.uniform(105, 120, size),
        'low': np.random.uniform(80, 95, size),
        'close': np.random.uniform(90, 110, size),
        'volume': np.random.uniform(1000, 5000, size)
    })

def test_1_previous_high_excludes_current_day():
    df = create_mock_df()
    # set t=100
    t = 100
    prev_max = df.iloc[50:100]['high'].max()
    df.loc[t, 'high'] = prev_max + 10 # High > previous high
    df.loc[t, 'close'] = prev_max - 5 # Close < previous high
    
    res = calculate_signals(df)
    assert not res.iloc[t]['sig_A']

def test_2_valid_breakout():
    df = create_mock_df()
    t = 100
    prev_max = df.iloc[50:100]['high'].max()
    df.loc[t, 'close'] = prev_max + 5 # Close > previous high
    
    res = calculate_signals(df)
    assert res.iloc[t]['sig_A']

def test_3_volume_confirmation():
    df = create_mock_df()
    t = 100
    prev_max = df.iloc[50:100]['high'].max()
    df.loc[t, 'close'] = prev_max + 5
    
    vol_mean_20 = df.iloc[80:100]['volume'].mean()
    
    # Under volume
    df.loc[t, 'volume'] = vol_mean_20 - 100
    res1 = calculate_signals(df)
    assert res1.iloc[t]['sig_A']
    assert not res1.iloc[t]['sig_B']
    
    # Over volume
    df.loc[t, 'volume'] = vol_mean_20 + 100
    res2 = calculate_signals(df)
    assert res2.iloc[t]['sig_B']

def test_4_trend_confirmation():
    df = create_mock_df(size=300)
    t = 250
    prev_max = df.iloc[200:250]['high'].max()
    df.loc[t, 'close'] = prev_max + 5
    
    sma_200 = df.iloc[51:251]['close'].mean() # 200 days ending at t
    
    # Under trend
    df.loc[t, 'close'] = sma_200 - 10
    # need to recalculate prev_max because we changed close, but if close is below sma_200 it might also be below prev_max.
    # To force signal C, let's just make sma_200 very high
    df.loc[51:250, 'close'] = 1000 # huge sma
    df.loc[t, 'close'] = prev_max + 5
    res1 = calculate_signals(df)
    assert not res1.iloc[t]['sig_C']
    
    # Over trend
    df.loc[51:250, 'close'] = 10 # low sma
    df.loc[t, 'close'] = prev_max + 5
    res2 = calculate_signals(df)
    assert res2.iloc[t]['sig_C']

def test_5_combined_signal():
    df = create_mock_df(size=300)
    t = 250
    prev_max = df.iloc[200:250]['high'].max()
    
    # Set conditions for D
    df.loc[51:250, 'close'] = 10 # SMA is low
    df.loc[t, 'close'] = prev_max + 5 # Close is high (A is true, C is true)
    
    vol_mean_20 = df.iloc[230:250]['volume'].mean()
    df.loc[t, 'volume'] = vol_mean_20 + 100 # Volume is high (B is true)
    
    res = calculate_signals(df)
    assert res.iloc[t]['sig_D']

def test_6_no_lookahead():
    df1 = create_mock_df()
    df2 = df1.copy()
    
    # Change future prices
    df2.loc[101:, 'open'] = 9999
    df2.loc[101:, 'close'] = 9999
    df2.loc[101:, 'high'] = 9999
    df2.loc[101:, 'volume'] = 9999
    
    res1 = calculate_signals(df1)
    res2 = calculate_signals(df2)
    
    assert res1.iloc[100]['sig_A'] == res2.iloc[100]['sig_A']
    assert res1.iloc[100]['sig_B'] == res2.iloc[100]['sig_B']
    assert res1.iloc[100]['sig_C'] == res2.iloc[100]['sig_C']
    assert res1.iloc[100]['sig_D'] == res2.iloc[100]['sig_D']

def test_7_forward_return():
    df = create_mock_df()
    res = calculate_signals(df)
    
    t = 100
    open_t1 = df.loc[101, 'open']
    close_t1 = df.loc[101, 'close']
    close_t5 = df.loc[105, 'close']
    
    assert np.isclose(res.loc[t, 'ret_1d'], close_t1 / open_t1 - 1)
    assert np.isclose(res.loc[t, 'ret_5d'], close_t5 / open_t1 - 1)

def test_8_pit_universe():
    # If a stock is not in PIT Nifty 50, it should be excluded from analysis.
    u = Nifty50UniverseProvider()
    univ = u.get_universe(pd.Timestamp('2024-01-01'))
    assert 'HDFCBANK' in univ
    assert 'RANDOMSTOCK' not in univ

def test_9_missing_next_day():
    df = create_mock_df()
    t = 100
    df.loc[101, 'open'] = np.nan
    
    res = calculate_signals(df)
    assert pd.isna(res.loc[t, 'ret_1d'])
    assert pd.isna(res.loc[t, 'ret_5d'])

def test_10_determinism():
    df = create_mock_df()
    res1 = calculate_signals(df)
    res2 = calculate_signals(df)
    pd.testing.assert_frame_equal(res1, res2)

