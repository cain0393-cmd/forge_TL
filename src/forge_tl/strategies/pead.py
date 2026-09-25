import pandas as pd
from typing import Dict, List, Set
from forge_tl.backtest import BacktestEngine, Order, OrderSide, OrderType
from .base import BaseStrategy, EarningsEventProvider

class PEADStrategy(BaseStrategy):
    def __init__(self, event_provider: EarningsEventProvider, surprise_threshold: float = 10.0, holding_bars: int = 20, allocation_pct: float = 0.05):
        super().__init__()
        self.event_provider = event_provider
        self.surprise_threshold = surprise_threshold
        self.holding_bars = holding_bars
        self.allocation_pct = allocation_pct
        
        self.entry_bars: Dict[str, int] = {}
        self.bar_index = 0
        self.processed_events: Set[str] = set()
        
    def on_bar(self, ts: pd.Timestamp, bars: Dict[str, dict], eng: BacktestEngine):
        self.bar_index += 1
        
        # Check Exits first
        for sym in list(eng.portfolio.positions.keys()):
            bars_held = self.bar_index - self.entry_bars.get(sym, self.bar_index)
            if bars_held >= self.holding_bars:
                eng.submit_order(Order(sym, OrderSide.SELL, eng.portfolio.positions[sym].quantity, OrderType.MARKET, ts))
                if sym in self.entry_bars:
                    del self.entry_bars[sym]
                    
        # Check new earnings events that have become available by this timestamp
        events = self.event_provider.get_events_available_by(ts)
        
        for event in events:
            if event.event_id in self.processed_events:
                continue
                
            self.processed_events.add(event.event_id)
            
            # The event is processed at this exact bar `ts`.
            # Orders are submitted at `ts`, making them eligible > ts.
            if event.surprise_pct > self.surprise_threshold:
                if event.symbol in bars:
                    target_value = eng.portfolio.equity * self.allocation_pct
                    qty = int(target_value / bars[event.symbol]['close'])
                    if qty > 0:
                        eng.submit_order(Order(event.symbol, OrderSide.BUY, qty, OrderType.MARKET, ts))
                        self.entry_bars[event.symbol] = self.bar_index + 1
