import pytest
import pandas as pd
from forge_tl.backtest import BacktestEngine, OrderStatus, OrderSide
from forge_tl.strategies.dual_momentum import DualMomentumStrategy
from forge_tl.strategies.trend_following import TrendFollowingStrategy
from forge_tl.strategies.mean_reversion import MeanReversionStrategy
from forge_tl.strategies.pead import PEADStrategy
from forge_tl.strategies.base import UniverseProvider, EarningsEventProvider, EarningsEvent

def _create_synthetic_data(symbols, rows=300):
    data = []
    dates = pd.date_range(start='2020-01-01', periods=rows, freq='B')
    for sym in symbols:
        price = 100.0
        for dt in dates:
            data.append({
                'timestamp': dt,
                'symbol': sym,
                'open': price,
                'high': price + 1,
                'low': price - 1,
                'close': price,
                'volume': 1000
            })
    df = pd.DataFrame(data)
    return df

def test_dual_momentum():
    df = _create_synthetic_data(['BANKBEES', 'ITBEES'], rows=300)
    dates = df['timestamp'].unique()
    
    # Rebalances happen when bar_count % 21 == 0.
    # At index 272, bar_count = 273. 273 % 21 == 0.
    # It has 273 closes. len(hist) = 273, which is >= 253.
    t = 272
    t_252 = t - 252 # index 20
    t_21 = t - 21 # index 251
    
    # Default all closes to 100
    df['close'] = 100.0
    
    # BANKBEES: passes both
    # Close[t-252] = 100, Close[t] = 120 (M252 = +20%)
    # Close[t-21] = 110, Close[t] = 120 (M21 = +9.09%)
    df.loc[(df['symbol'] == 'BANKBEES') & (df['timestamp'] == dates[t_252]), 'close'] = 100.0
    df.loc[(df['symbol'] == 'BANKBEES') & (df['timestamp'] == dates[t_21]), 'close'] = 110.0
    df.loc[(df['symbol'] == 'BANKBEES') & (df['timestamp'] == dates[t]), 'close'] = 120.0
    
    # ITBEES: superior relative momentum, fails absolute momentum
    # Close[t-252] = 100, Close[t] = 130 (M252 = +30%)
    # Close[t-21] = 140, Close[t] = 130 (M21 = -7.14%)
    df.loc[(df['symbol'] == 'ITBEES') & (df['timestamp'] == dates[t_252]), 'close'] = 100.0
    df.loc[(df['symbol'] == 'ITBEES') & (df['timestamp'] == dates[t_21]), 'close'] = 140.0
    df.loc[(df['symbol'] == 'ITBEES') & (df['timestamp'] == dates[t]), 'close'] = 130.0
    
    engine = BacktestEngine(df, initial_capital=100000.0)
    strategy = DualMomentumStrategy(momentum_window=252, rebalance_bars=21, top_n=1)
    engine.set_strategy(strategy)
    res = engine.run()
    
    # BANKBEES should be selected, ITBEES should fail
    # Execution occurs strictly after bar 272
    buy_orders = [o for o in res['orders'] if o.status == OrderStatus.FILLED and o.side == OrderSide.BUY]
    assert len(buy_orders) == 1
    assert buy_orders[0].symbol == 'BANKBEES'
    assert buy_orders[0].created_at == dates[t]
    assert buy_orders[0].side == OrderSide.BUY

def test_trend_following():
    df = _create_synthetic_data(['NIFTYBEES'], rows=250)
    
    # First 200 days flat at 100. SMA200 = 100.
    # Day 201: close 105 -> BUY
    # Day 210: close 95 -> SELL
    closes = [100.0] * 200 + [105.0] * 9 + [95.0] * 41
    df.loc[df['symbol'] == 'NIFTYBEES', 'close'] = closes
    # To avoid zero-division or fill failures, ensure open is reasonable
    df.loc[df['symbol'] == 'NIFTYBEES', 'open'] = closes
    
    engine = BacktestEngine(df, initial_capital=100000.0)
    strategy = TrendFollowingStrategy(sma_window=200)
    engine.set_strategy(strategy)
    res = engine.run()
    
    trades = res['trades']
    assert len(trades) >= 1
    t = trades[0]
    
    # Buy executes after day 200 (index 200)
    assert t.entry_timestamp > df['timestamp'].unique()[200]
    # Sell executes after day 209 (index 209)
    assert t.exit_timestamp > df['timestamp'].unique()[209]

class MockUniverseProvider(UniverseProvider):
    def get_universe(self, timestamp: pd.Timestamp):
        return ['SYM_A', 'SYM_B']

def test_mean_reversion():
    df = _create_synthetic_data(['SYM_A', 'SYM_B'], rows=50)
    dates = df['timestamp'].unique()
    
    closes = [100.0] * 50
    # Steady uptrend
    for i in range(1, 30):
        closes[i] = closes[i-1] * 1.05
    # Crash
    closes[30] = closes[29] * 0.5
    for i in range(31, 50):
        closes[i] = closes[i-1] * 1.05
        
    df.loc[df['symbol'] == 'SYM_A', 'close'] = closes
    df.loc[df['symbol'] == 'SYM_B', 'close'] = [100.0]*50
    
    engine = BacktestEngine(df, initial_capital=100000.0)
    strategy = MeanReversionStrategy(MockUniverseProvider(), mean_window=20, return_window=5, entry_z=-2.0, exit_z=0.0, max_holdings=5)
    engine.set_strategy(strategy)
    res = engine.run()
    
    trades = [t for t in res['trades'] if t.symbol == 'SYM_A']
    assert len(trades) >= 1
    # Entry should be at or after the drop sequence starts
    assert trades[0].entry_timestamp > dates[29]
    # Exit should be within 5 bars
    bars_held = 0
    for dt in dates:
        if trades[0].entry_timestamp < dt <= trades[0].exit_timestamp:
            bars_held += 1
    assert bars_held <= 5


class MockEarningsProvider(EarningsEventProvider):
    def __init__(self, events):
        self.events = events
    def get_events_available_by(self, timestamp: pd.Timestamp):
        return [e for e in self.events if e.available_timestamp <= timestamp]

def test_pead_timing():
    df = _create_synthetic_data(['PEAD_A', 'PEAD_B', 'PEAD_C'], rows=50)
    dates = df['timestamp'].unique()
    
    # Case A: available_timestamp occurs normally
    event_a_ts = dates[10]
    avail_a_ts = dates[11]
    
    # Case B: available_timestamp is after the final bar (no trading)
    event_b_ts = dates[45]
    avail_b_ts = dates[-1] + pd.Timedelta(days=1)
    
    # Case C: event is early, available is much later
    event_c_ts = dates[5]
    avail_c_ts = dates[25]
    
    events = [
        EarningsEvent('1', 'PEAD_A', event_a_ts, event_a_ts, avail_a_ts, 15.0),
        EarningsEvent('2', 'PEAD_B', event_b_ts, event_b_ts, avail_b_ts, 15.0),
        EarningsEvent('3', 'PEAD_C', event_c_ts, event_c_ts, avail_c_ts, 15.0)
    ]
    
    provider = MockEarningsProvider(events)
    engine = BacktestEngine(df, initial_capital=100000.0)
    strategy = PEADStrategy(provider, surprise_threshold=10.0, holding_bars=5, allocation_pct=0.1)
    engine.set_strategy(strategy)
    res = engine.run()
    
    trades_a = [t for t in res['trades'] if t.symbol == 'PEAD_A']
    trades_b = [t for t in res['trades'] if t.symbol == 'PEAD_B']
    trades_c = [t for t in res['trades'] if t.symbol == 'PEAD_C']
    
    # A should trade normally, executing strictly AFTER avail_a_ts
    assert len(trades_a) == 1
    assert trades_a[0].entry_timestamp > avail_a_ts
    
    # B should never trade (information available after dataset ends)
    assert len(trades_b) == 0
    # Also check pending orders to see if an order was placed
    orders_b = [o for o in res['orders'] if o.symbol == 'PEAD_B']
    assert len(orders_b) == 0
    
    # C should trade, but only AFTER avail_c_ts, NOT event_c_ts
    assert len(trades_c) == 1
    assert trades_c[0].entry_timestamp > avail_c_ts
