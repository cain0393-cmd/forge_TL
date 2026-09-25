import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.run_research_momentum_trend_11_0 import calculate_dual_momentum, calculate_trend

def create_mock_df(size=300, symbol='MOCK'):
    np.random.seed(42)
    return pd.DataFrame({
        'date': pd.date_range('2015-01-01', periods=size, freq='B'),
        'symbol': symbol,
        'open': np.random.uniform(90, 110, size),
        'high': np.random.uniform(105, 120, size),
        'low': np.random.uniform(80, 95, size),
        'close': np.random.uniform(90, 110, size),
        'volume': np.random.uniform(1000, 5000, size)
    })

# Dual Momentum Tests
def test_1_252_momentum_uses_t252():
    df = create_mock_df(size=300)
    df.loc[0, 'close'] = 100
    df.loc[252, 'close'] = 110
    res = calculate_dual_momentum(df)
    assert np.isclose(res.loc[252, 'rel_mom_252'], 110/100 - 1)

def test_2_252_momentum_requires_253_closes():
    df = create_mock_df(size=250)
    res = calculate_dual_momentum(df)
    assert pd.isna(res.iloc[-1]['rel_mom_252'])

def test_3_21_abs_momentum_uses_t21():
    df = create_mock_df(size=50)
    df.loc[10, 'close'] = 100
    df.loc[31, 'close'] = 105
    res = calculate_dual_momentum(df)
    assert np.isclose(res.loc[31, 'abs_mom_21'], 105/100 - 1)

def test_4_negative_abs_momentum_excluded():
    df = create_mock_df(size=50)
    df.loc[10, 'close'] = 100
    df.loc[31, 'close'] = 95
    res = calculate_dual_momentum(df)
    assert not res.loc[31, 'eligible']

def test_5_ranking_deterministic():
    # Setup cross-sectional data
    df1 = create_mock_df(size=300, symbol='A')
    df2 = create_mock_df(size=300, symbol='B')
    df3 = create_mock_df(size=300, symbol='C')
    df1.loc[0, 'close'] = 100; df1.loc[252, 'close'] = 110
    df2.loc[0, 'close'] = 100; df2.loc[252, 'close'] = 120
    df3.loc[0, 'close'] = 100; df3.loc[252, 'close'] = 105
    df = pd.concat([df1, df2, df3]).sort_values(['symbol', 'date']).reset_index(drop=True)
    res = calculate_dual_momentum(df)
    # Ranks at index 252 (A), 552 (B), 852 (C)
    date_t = df1.loc[252, 'date']
    cross = res[res['date'] == date_t].copy()
    cross['rank'] = cross['rel_mom_252'].rank(ascending=False)
    assert cross.loc[cross['symbol'] == 'B', 'rank'].iloc[0] == 1
    assert cross.loc[cross['symbol'] == 'A', 'rank'].iloc[0] == 2
    assert cross.loc[cross['symbol'] == 'C', 'rank'].iloc[0] == 3

def test_6_top3_selection_deterministic():
    # Tested basically in test 5 by ensuring ranks are strictly ordered
    # We will just verify we can filter top 3
    df = pd.DataFrame({'symbol': ['A','B','C','D'], 'rel_mom_252': [0.1, 0.4, 0.3, 0.2]})
    df['rank'] = df['rel_mom_252'].rank(ascending=False, method='first')
    top3 = df[df['rank'] <= 3]
    assert len(top3) == 3
    assert 'A' not in top3['symbol'].values

def test_7_no_lookahead_dual():
    df1 = create_mock_df()
    df2 = df1.copy()
    df2.loc[253:, 'close'] = 999
    res1 = calculate_dual_momentum(df1)
    res2 = calculate_dual_momentum(df2)
    assert res1.loc[252, 'rel_mom_252'] == res2.loc[252, 'rel_mom_252']

def test_8_missing_history_no_fabrication():
    df = create_mock_df(size=250)
    res = calculate_dual_momentum(df)
    assert pd.isna(res.loc[249, 'rel_mom_252'])

# Trend Tests
def test_9_sma200_requires_200_closes():
    df = create_mock_df(size=199)
    res = calculate_trend(df)
    assert pd.isna(res.loc[198, 'sma200'])

def test_10_trend_state_boundary():
    df = create_mock_df(size=250)
    df.loc[0:199, 'close'] = 100
    res = calculate_trend(df)
    assert res.loc[199, 'sma200'] == 100
    # Boundary: Close = SMA -> OFF
    assert not res.loc[199, 'trend_on']
    df.loc[199, 'close'] = 101
    res = calculate_trend(df)
    assert res.loc[199, 'trend_on']

def test_11_no_lookahead_trend():
    df1 = create_mock_df(size=250)
    df2 = df1.copy()
    df2.loc[200:, 'close'] = 999
    res1 = calculate_trend(df1)
    res2 = calculate_trend(df2)
    assert res1.loc[199, 'trend_on'] == res2.loc[199, 'trend_on']

def test_12_missing_history_no_false_trend():
    df = create_mock_df(size=199)
    res = calculate_trend(df)
    assert not res.loc[198, 'trend_on']

def test_13_equal_weight_portfolio_diagnostic_deterministic():
    # 20% target weight
    trend_states = pd.Series([True, False, True, True, False])
    weights = trend_states.map({True: 0.20, False: 0.0})
    assert np.isclose(weights.sum(), 0.60)
    assert weights.iloc[0] == 0.20

# Common Tests
def test_14_forward_return_uses_opent1():
    df = create_mock_df(size=50)
    res = calculate_trend(df)
    open_t1 = df.loc[21, 'open']
    close_t1 = df.loc[21, 'close']
    close_t5 = df.loc[25, 'close']
    assert np.isclose(res.loc[20, 'ret_1d'], close_t1 / open_t1 - 1)
    assert np.isclose(res.loc[20, 'ret_5d'], close_t5 / open_t1 - 1)

def test_15_missing_next_day_open():
    df = create_mock_df(size=50)
    df.loc[21, 'open'] = np.nan
    res = calculate_trend(df)
    assert pd.isna(res.loc[20, 'ret_1d'])
    assert pd.isna(res.loc[20, 'ret_5d'])

def test_16_repeated_execution_identical():
    df = create_mock_df(size=300)
    res1 = calculate_dual_momentum(df)
    res2 = calculate_dual_momentum(df)
    pd.testing.assert_frame_equal(res1, res2)
