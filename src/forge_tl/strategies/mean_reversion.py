import math
import numpy as np
import pandas as pd
from typing import Dict, List
from forge_tl.backtest import BacktestEngine, Order, OrderSide, OrderType
from .base import BaseStrategy, UniverseProvider
from forge_tl.universe.nifty50 import UnsupportedUniverseDate

class MeanReversionStrategy(BaseStrategy):
    def __init__(self, universe_provider: UniverseProvider, mean_window: int = 20, return_window: int = 5, entry_z: float = -2.0, exit_z: float = 0.0, max_holdings: int = 5):
        super().__init__()
        self.universe_provider = universe_provider
        self.mean_window = mean_window
        self.return_window = return_window
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.max_holdings = max_holdings
        
        self.price_history: Dict[str, List[float]] = {}
        self.entry_bars: Dict[str, int] = {}
        self.bar_index = 0
        
    def on_bar(self, ts: pd.Timestamp, bars: Dict[str, dict], eng: BacktestEngine):
        self.bar_index += 1
        try:
            current_universe = self.universe_provider.get_universe(ts)
        except UnsupportedUniverseDate:
            current_universe = []
        
        # Track universe and any current holdings
        tracked_symbols = set(current_universe) | set(eng.portfolio.positions.keys())
        
        # Update price history
        required_len = self.mean_window + self.return_window
        for sym in tracked_symbols:
            if sym not in self.price_history:
                self.price_history[sym] = []
            if sym in bars:
                self.price_history[sym].append(bars[sym]['close'])
                if len(self.price_history[sym]) > required_len + 1: # Keep one extra for safety
                    self.price_history[sym].pop(0)
                    
        z_scores = {}
        
        for sym in tracked_symbols:
            hist = self.price_history[sym]
            if len(hist) < required_len:
                continue
                
            # CR5 for the last 20 days.
            # CR5[t] = hist[t] / hist[t-5] - 1
            # We need CR5 for the last 20 days (including today).
            # So we need to calculate CR5 for indices: len(hist)-1 down to len(hist)-20
            # That means we need len(hist) >= 20 + 5 = 25.
            
            cr5_series = []
            # Calculate from oldest to newest CR5
            # We want self.mean_window values (e.g., 20)
            # The newest is at index len(hist)-1
            for i in range(len(hist) - self.mean_window, len(hist)):
                cr5 = (hist[i] / hist[i - self.return_window]) - 1.0
                cr5_series.append(cr5)
            
            cr5_current = cr5_series[-1]
            mu20 = np.mean(cr5_series)

            # Using ddof=1 for sample standard deviation
            sigma20 = np.std(cr5_series, ddof=1) if len(cr5_series) > 1 else 0.0
            
            if sigma20 < 1e-8:
                z = 0.0
            else:
                z = (cr5_current - 5.0 * mu20) / (math.sqrt(5.0) * sigma20)
                
            z_scores[sym] = z
            
            # Exit logic
            if sym in eng.portfolio.positions:
                bars_held = self.bar_index - self.entry_bars.get(sym, self.bar_index)
                if z > self.exit_z or bars_held >= self.return_window:
                    eng.submit_order(Order(sym, OrderSide.SELL, eng.portfolio.positions[sym].quantity, OrderType.MARKET, ts))
                    if sym in self.entry_bars:
                        del self.entry_bars[sym]
                        
        # Entry logic
        open_orders = sum(1 for o in eng.pending_orders if o.side == OrderSide.BUY)
        current_holdings = len(eng.portfolio.positions)
        expected_holdings = current_holdings
        
        # Adjust expected holdings for sells that will happen at the next bar
        for sym in eng.portfolio.positions:
            if sym in [o.symbol for o in eng.orders if o.side == OrderSide.SELL and o.created_at == ts]:
                expected_holdings -= 1
        
        free_slots = self.max_holdings - expected_holdings
        if free_slots <= 0:
            return
            
        eligible = []
        for sym in current_universe:
            # Skip if already holding or already trying to buy
            if sym in eng.portfolio.positions or sym in [o.symbol for o in eng.orders if o.side == OrderSide.BUY and o.created_at == ts]:
                continue
            z = z_scores.get(sym, 0.0)
            if z < self.entry_z:
                eligible.append((sym, z))
                
        # Deterministic sorting (lowest Z first, tie-break by symbol name)
        eligible.sort(key=lambda x: (x[1], x[0]))
        
        selected = [x[0] for x in eligible[:free_slots]]
        
        if selected:
            target_value = eng.portfolio.equity / self.max_holdings
            for sym in selected:
                if sym in bars:
                    qty = int(target_value / bars[sym]['close'])
                    if qty > 0:
                        eng.submit_order(Order(sym, OrderSide.BUY, qty, OrderType.MARKET, ts))
                        self.entry_bars[sym] = self.bar_index
