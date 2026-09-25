import pandas as pd
from typing import Dict, List
from forge_tl.backtest import BacktestEngine, Order, OrderSide, OrderType
from .base import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, sma_window: int = 200):
        super().__init__()
        self.sma_window = sma_window
        self.universe = ['NIFTYBEES', 'JUNIORBEES', 'GOLDBEES', 'SILVERBEES', 'SETF10GILT']
        self.history: Dict[str, List[float]] = {s: [] for s in self.universe}
        
    def on_bar(self, ts: pd.Timestamp, bars: Dict[str, dict], eng: BacktestEngine):
        # Update history
        for sym in self.universe:
            if sym in bars:
                self.history[sym].append(bars[sym]['close'])
                if len(self.history[sym]) > self.sma_window + 1:
                    self.history[sym].pop(0)
                    
        # Calculate eligible assets first
        eligible = []
        for sym in self.universe:
            hist = self.history[sym]
            if len(hist) < self.sma_window:
                continue
            
            current_close = hist[-1]
            sma = sum(hist[-self.sma_window:]) / self.sma_window
            
            if current_close > sma:
                eligible.append(sym)
                
        # Daily rebalance / signal check
        if eligible:
            weight_per_asset = 1.0 / len(eligible)
            target_value_per_asset = eng.portfolio.equity * weight_per_asset
        else:
            target_value_per_asset = 0.0
        
        # Exit non-eligible first
        for sym, pos in list(eng.portfolio.positions.items()):
            if sym not in eligible:
                eng.submit_order(Order(sym, OrderSide.SELL, pos.quantity, OrderType.MARKET, ts))
                
        # Rebalance eligible
        for sym in eligible:
            if sym not in bars:
                continue
                
            current_close = bars[sym]['close']
            if sym in eng.portfolio.positions:
                pos = eng.portfolio.positions[sym]
                current_value = pos.quantity * current_close
                diff = target_value_per_asset - current_value
                if abs(diff) > current_close:
                    qty = int(abs(diff) / current_close)
                    if diff > 0:
                        eng.submit_order(Order(sym, OrderSide.BUY, qty, OrderType.MARKET, ts))
                    elif diff < 0:
                        eng.submit_order(Order(sym, OrderSide.SELL, qty, OrderType.MARKET, ts))
            else:
                qty = int(target_value_per_asset / current_close)
                if qty > 0:
                    eng.submit_order(Order(sym, OrderSide.BUY, qty, OrderType.MARKET, ts))
