import pytest
import pandas as pd
from datetime import datetime
from forge_tl.backtest import (
    BacktestEngine, Order, OrderSide, OrderType, OrderStatus, 
    TransactionCostModel, SlippageModel, Strategy
)

def _get_mock_data():
    return pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03']),
        'symbol': ['AAPL', 'AAPL', 'AAPL'],
        'open': [100.0, 110.0, 120.0],
        'high': [105.0, 115.0, 125.0],
        'low': [95.0, 105.0, 115.0],
        'close': [102.0, 112.0, 122.0],
        'volume': [1000, 2000, 1500]
    })

def test_1_buy_order():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(BuyStrategy())
    res = engine.run()
    
    # Fill occurs on 2026-01-02 at open=110.0
    assert res['metrics']['final_cash'] == 10000.0 - (10 * 110.0)
    assert engine.portfolio.positions['AAPL'].quantity == 10
    
def test_2_sell_order():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    
    class BuySellStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 5, OrderType.MARKET, ts))
                
    engine.set_strategy(BuySellStrategy())
    res = engine.run()
    
    # Buy filled on 01-02 @ 110.0. Cash = 10000 - 1100 = 8900. Pos = 10
    # Sell filled on 01-03 @ 120.0. Cash = 8900 + 600 = 9500. Pos = 5
    assert res['metrics']['final_cash'] == 9500.0
    assert engine.portfolio.positions['AAPL'].quantity == 5
    assert len(res['trades']) == 1
    assert res['trades'][0].net_pnl == (120.0 - 110.0) * 5

def test_3_insufficient_cash():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=1000.0) # only 1000 cash
    
    class BrokeStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                # Cost would be 10 * 110 = 1100 > 1000
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(BrokeStrategy())
    res = engine.run()
    
    assert res['orders'][0].status == OrderStatus.REJECTED
    assert res['metrics']['final_cash'] == 1000.0
    assert 'AAPL' not in engine.portfolio.positions

def test_4_oversell():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    
    class OversellStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 15, OrderType.MARKET, ts)) # Only own 10
                
    engine.set_strategy(OversellStrategy())
    res = engine.run()
    
    assert res['orders'][1].status == OrderStatus.REJECTED
    assert engine.portfolio.positions['AAPL'].quantity == 10

def test_5_transaction_costs():
    df = _get_mock_data()
    # High brokerage to make it obvious
    cost_model = TransactionCostModel(brokerage_pct=0.01)
    engine = BacktestEngine(df, initial_capital=10000.0, cost_model=cost_model)
    
    class BuySellStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(BuySellStrategy())
    res = engine.run()
    
    # Buy @ 110 (value 1100). Cost = 11.
    # Sell @ 120 (value 1200). Cost = 12.
    assert res['trades'][0].gross_pnl == (120 - 110) * 10
    assert res['trades'][0].net_pnl == 100 - 23 # Both entry (11) and exit (12) costs
    assert res['metrics']['final_cash'] == 10000.0 - 1100 - 11 + 1200 - 12

def test_6_slippage():
    df = _get_mock_data()
    slippage_model = SlippageModel(slippage_pct=0.05)
    engine = BacktestEngine(df, initial_capital=10000.0, slippage_model=slippage_model)
    
    class SlippageStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(SlippageStrategy())
    res = engine.run()
    
    # Fill at open=110. Slippage = 5%. Price = 110 * 1.05 = 115.5
    assert engine.portfolio.positions['AAPL'].average_entry_price == 110.0 * 1.05

def test_7_limit_orders():
    df = _get_mock_data() # Day 2 (Open 110, High 115, Low 105)
    
    # Limit Buy above open (111) -> fills at open (110)
    engine1 = BacktestEngine(df, initial_capital=10000.0)
    class LimitBuyOpenStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.LIMIT, ts, limit_price=111.0))
    engine1.set_strategy(LimitBuyOpenStrategy())
    engine1.run()
    assert engine1.portfolio.positions['AAPL'].average_entry_price == 110.0
    
    # Limit Buy inside bar (108) -> fills at limit (108)
    engine2 = BacktestEngine(df, initial_capital=10000.0)
    class LimitBuyIntraStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.LIMIT, ts, limit_price=108.0))
    engine2.set_strategy(LimitBuyIntraStrategy())
    engine2.run()
    assert engine2.portfolio.positions['AAPL'].average_entry_price == 108.0
    
    # Limit Buy below low (100) -> no fill
    engine3 = BacktestEngine(df, initial_capital=10000.0)
    class LimitBuyNoFillStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.LIMIT, ts, limit_price=100.0))
    engine3.set_strategy(LimitBuyNoFillStrategy())
    res3 = engine3.run()
    assert 'AAPL' not in engine3.portfolio.positions
    assert res3['orders'][0].status == OrderStatus.PENDING

def test_8_equity():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(BuyStrategy())
    res = engine.run()
    
    eq_curve = res['equity_curve']
    # Day 1: Cash 10000
    # Day 2: Buy 10 @ 110. Close is 112. Equity = 8900 + 10*112 = 10020
    assert eq_curve.loc[pd.Timestamp('2026-01-02'), 'equity'] == 10020.0
    # Day 3: Close is 122. Equity = 8900 + 10*122 = 10120
    assert eq_curve.loc[pd.Timestamp('2026-01-03'), 'equity'] == 10120.0

def test_9_drawdown():
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-01', '2026-01-02', '2026-01-03', '2026-01-04']),
        'symbol': ['AAPL']*4,
        'open': [100.0, 110.0, 100.0, 90.0],
        'high': [105.0, 115.0, 105.0, 95.0],
        'low': [95.0, 105.0, 95.0, 85.0],
        'close': [100.0, 110.0, 100.0, 90.0],
        'volume': [1000]*4
    })
    engine = BacktestEngine(df, initial_capital=10000.0)
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
    engine.set_strategy(BuyStrategy())
    res = engine.run()
    
    # Day 2: Buy 10 @ 110. Cash = 8900. Close = 110. Eq = 10000
    # Day 3: Close = 100. Eq = 8900 + 1000 = 9900
    # Day 4: Close = 90. Eq = 8900 + 900 = 9800
    # Max peak = 10000. Min Eq = 9800. DD = -200, DD_pct = -0.02
    assert res['metrics']['max_drawdown'] == -200.0
    assert res['metrics']['max_drawdown_pct'] == pytest.approx(-0.02)

def test_10_look_ahead_bias_prevention():
    # Strict test ensuring close[t] signal cannot fill at open[t]
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-01', '2026-01-02']),
        'symbol': ['AAPL', 'AAPL'],
        'open': [100.0, 110.0],
        'high': [105.0, 115.0],
        'low': [95.0, 105.0],
        'close': [102.0, 112.0],
        'volume': [1000, 2000]
    })
    engine = BacktestEngine(df, initial_capital=10000.0)
    class LookaheadStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
    engine.set_strategy(LookaheadStrategy())
    engine.run()
    
    # If the fill happened at Day 1 Open, entry price would be 100.
    # Since it's processed on Day 2, fill MUST be at Day 2 Open (110).
    assert engine.portfolio.positions['AAPL'].average_entry_price == 110.0

def test_11_chronological_sorting():
    # Intentionally shuffle data
    df = pd.DataFrame({
        'timestamp': pd.to_datetime(['2026-01-02', '2026-01-01']),
        'symbol': ['AAPL', 'AAPL'],
        'open': [110.0, 100.0],
        'high': [115.0, 105.0],
        'low': [105.0, 95.0],
        'close': [112.0, 102.0],
        'volume': [2000, 1000]
    })
    engine = BacktestEngine(df, initial_capital=10000.0)
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
    engine.set_strategy(BuyStrategy())
    engine.run()
    
    # Engine must sort chronologically internally, so it still fills at 110.0 on Day 2
    assert engine.portfolio.positions['AAPL'].average_entry_price == 110.0

def test_12_deterministic_replay():
    df = _get_mock_data()
    
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
    
    engine1 = BacktestEngine(df.copy(), initial_capital=10000.0)
    engine1.set_strategy(BuyStrategy())
    res1 = engine1.run()
    
    engine2 = BacktestEngine(df.copy(), initial_capital=10000.0)
    engine2.set_strategy(BuyStrategy())
    res2 = engine2.run()
    
    pd.testing.assert_frame_equal(res1['equity_curve'], res2['equity_curve'])
    for key, val in res1['metrics'].items():
        if key not in ('runtime_seconds', 'rows_per_second'):
            assert val == res2['metrics'][key]

def test_13_no_negative_cash():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=1000.0)
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                # Fills at 110, so 100 qty costs 11000
                eng.submit_order(Order('AAPL', OrderSide.BUY, 100, OrderType.MARKET, ts))
    engine.set_strategy(BuyStrategy())
    res = engine.run()
    assert res['metrics']['final_cash'] >= 0

def test_14_no_negative_position():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    class SellStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
    engine.set_strategy(SellStrategy())
    engine.run()
    assert 'AAPL' not in engine.portfolio.positions

def test_15_same_bar_fill_prevention():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    
    class MaliciousStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                # 1. Provide an explicit invalid eligible_at equal to created_at
                order_invalid = Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, created_at=ts, eligible_at=ts)
                eng.submit_order(order_invalid)
                
                # 2. Provide a valid order with default explicit eligible_at
                order_valid = Order('AAPL', OrderSide.BUY, 5, OrderType.MARKET, created_at=ts)
                eng.submit_order(order_valid)
                
    engine.set_strategy(MaliciousStrategy())
    res = engine.run()
    
    # The invalid order should be deterministically rejected by the engine before even entering pending
    assert res['orders'][0].status == OrderStatus.REJECTED
    # The valid order should fill on '2026-01-02' Open which is 110.0
    assert engine.portfolio.positions['AAPL'].average_entry_price == 110.0
    assert engine.portfolio.positions['AAPL'].quantity == 5

def test_16_trade_entry_timestamp():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    class Strategy16(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(Strategy16())
    res = engine.run()
    
    trade = res['trades'][0]
    # Order created 01-01. Filled 01-02.
    assert trade.entry_timestamp == pd.Timestamp('2026-01-02')
    # Sell Order created 01-02. Filled 01-03.
    assert trade.exit_timestamp == pd.Timestamp('2026-01-03')

def test_17_trade_costs_and_pnl():
    df = _get_mock_data()
    cost_model = TransactionCostModel(brokerage_pct=0.01)
    engine = BacktestEngine(df, initial_capital=10000.0, cost_model=cost_model)
    class Strategy17(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(Strategy17())
    res = engine.run()
    
    trade = res['trades'][0]
    # Buy 10 @ 110 = 1100. Cost = 11
    # Sell 10 @ 120 = 1200. Cost = 12
    assert trade.entry_cost == 11.0
    assert trade.exit_cost == 12.0
    assert trade.transaction_cost == 23.0
    assert trade.gross_pnl == (1200 - 1100)
    assert trade.net_pnl == (100 - 23.0)

def test_18_realized_pnl():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    class Strategy18(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
                
    engine.set_strategy(Strategy18())
    res = engine.run()
    
    trade = res['trades'][0]
    assert trade.gross_pnl == 100.0 # 10 * (120 - 110)
    assert res['metrics']['net_pnl'] == 100.0 # No costs

def test_19_sharpe_ratio():
    # Synthetic flat returns
    df = pd.DataFrame({
        'timestamp': pd.date_range('2026-01-01', periods=10, freq='D'),
        'symbol': ['AAPL']*10,
        'open': [100.0]*10,
        'high': [100.0]*10,
        'low': [100.0]*10,
        'close': [100.0]*10,
        'volume': [1000]*10
    })
    engine = BacktestEngine(df, initial_capital=10000.0)
    res = engine.run()
    assert res['metrics']['sharpe_ratio'] == 0.0

def test_20_sortino_ratio():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    res = engine.run()
    # If there are no trades, returns are 0. Sortino should be 0.
    assert res['metrics']['sortino_ratio'] == 0.0

def test_21_runtime_metrics():
    df = _get_mock_data()
    engine = BacktestEngine(df, initial_capital=10000.0)
    res = engine.run()
    
    assert 'runtime_seconds' in res['metrics']
    assert res['metrics']['runtime_seconds'] >= 0
    assert res['metrics']['rows_processed'] == 3
    assert 'rows_per_second' in res['metrics']

def test_22_deterministic_ids_and_replay():
    df = _get_mock_data()
    
    class BuyStrategy(Strategy):
        def on_bar(self, ts, bars, eng):
            if ts == pd.Timestamp('2026-01-01'):
                eng.submit_order(Order('AAPL', OrderSide.BUY, 10, OrderType.MARKET, ts))
            elif ts == pd.Timestamp('2026-01-02'):
                eng.submit_order(Order('AAPL', OrderSide.SELL, 10, OrderType.MARKET, ts))
                
    engine1 = BacktestEngine(df.copy(), initial_capital=10000.0)
    engine1.set_strategy(BuyStrategy())
    res1 = engine1.run()
    
    engine2 = BacktestEngine(df.copy(), initial_capital=10000.0)
    engine2.set_strategy(BuyStrategy())
    res2 = engine2.run()
    
    # Check IDs
    assert res1['orders'][0].order_id == "ORDER-000001"
    assert res1['trades'][0].trade_id == "TRADE-000001"
    assert res1['orders'][0].order_id == res2['orders'][0].order_id
    assert res1['trades'][0].trade_id == res2['trades'][0].trade_id
    
    # Check Replay completely deterministic
    pd.testing.assert_frame_equal(res1['equity_curve'], res2['equity_curve'])
    for key, val in res1['metrics'].items():
        if key not in ('runtime_seconds', 'rows_per_second'):
            assert val == res2['metrics'][key]
