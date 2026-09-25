import pandas as pd
import numpy as np

def test_forward_return_starts_after_signal():
    df = pd.DataFrame({
        'open': [100, 101, 102, 103],
        'close': [100.5, 101.5, 102.5, 103.5]
    })
    
    # Forward return for day 0 (starts at open of day 1)
    # Open[t+1] -> Close[t+1] for 1d
    open_t1 = df['open'].shift(-1)
    close_t1 = df['close'].shift(-1)
    
    ret_1d = close_t1 / open_t1 - 1
    
    # Day 0: 101.5 / 101 - 1
    assert np.isclose(ret_1d.iloc[0], 101.5 / 101.0 - 1)
    
    # No same-day tradable return used
    # The return formulation explicitly relies entirely on shift(-X)
    assert not np.isclose(ret_1d.iloc[0], 100.5 / 100.0 - 1)

def test_rolling_baseline_excludes_t():
    df = pd.DataFrame({
        'delivery_pct': [10, 20, 30, 40]
    })
    
    # Rolling mean of size 2, MUST exclude t
    d_pct = df['delivery_pct'].shift(1)
    roll = d_pct.rolling(2, min_periods=1).mean()
    
    # Day 0: NaN
    assert pd.isna(roll.iloc[0])
    # Day 1: mean([10]) = 10
    assert roll.iloc[1] == 10
    # Day 2: mean([10, 20]) = 15
    assert roll.iloc[2] == 15
    # Day 3: mean([20, 30]) = 25
    assert roll.iloc[3] == 25

def test_abnormal_calculations():
    df = pd.DataFrame({
        'delivery_vol': [100, 200, 300, 400],
        'traded_vol': [1000, 2000, 3000, 4000]
    })
    
    d_vol = df['delivery_vol'].shift(1)
    t_vol = df['traded_vol'].shift(1)
    
    del_mean_2 = d_vol.rolling(2, min_periods=1).mean()
    trd_mean_2 = t_vol.rolling(2, min_periods=1).mean()
    
    abn_del = df['delivery_vol'] / del_mean_2
    abn_trd = df['traded_vol'] / trd_mean_2
    
    # Day 2: del = 300. baseline = mean(100, 200) = 150. abn = 2.0
    assert abn_del.iloc[2] == 2.0
    # Day 2: trd = 3000. baseline = mean(1000, 2000) = 1500. abn = 2.0
    assert abn_trd.iloc[2] == 2.0

def test_quantile_assignment():
    df = pd.DataFrame({
        'sig': [10, 20, 30, 40, 50]
    })
    
    q = pd.qcut(df['sig'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    assert q.iloc[0] == 'Q1'
    assert q.iloc[-1] == 'Q5'

def test_missing_future_price_handling():
    df = pd.DataFrame({
        'open': [100, 101, np.nan, 103],
        'close': [100.5, 101.5, 102.5, 103.5]
    })
    open_t1 = df['open'].shift(-1)
    close_t1 = df['close'].shift(-1)
    ret_1d = close_t1 / open_t1 - 1
    
    # Day 1: open_t1 = NaN, so ret_1d should be NaN
    assert pd.isna(ret_1d.iloc[1])
