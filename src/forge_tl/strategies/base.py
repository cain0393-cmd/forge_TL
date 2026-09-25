import pandas as pd
from typing import List, Dict, Optional
from forge_tl.backtest import Strategy, BacktestEngine

class UniverseProvider:
    """Provides point-in-time universe membership."""
    def get_universe(self, timestamp: pd.Timestamp) -> List[str]:
        return []

class EarningsEvent:
    def __init__(self, event_id: str, symbol: str, period_end: pd.Timestamp, event_timestamp: pd.Timestamp, available_timestamp: pd.Timestamp, surprise_pct: float):
        self.event_id = event_id
        self.symbol = symbol
        self.period_end = period_end
        self.event_timestamp = event_timestamp
        self.available_timestamp = available_timestamp
        self.surprise_pct = surprise_pct

class EarningsEventProvider:
    """Provides historical earnings events."""
    def get_events_available_by(self, timestamp: pd.Timestamp) -> List[EarningsEvent]:
        """Returns all events where available_timestamp <= timestamp"""
        return []

class BaseStrategy(Strategy):
    """
    Common minimal strategy interface.
    Provides standard helper variables, leaving explicit logic to the implementations.
    """
    def __init__(self):
        self.symbol_history: Dict[str, pd.DataFrame] = {}
        
    def on_bar(self, ts: pd.Timestamp, bars: Dict[str, dict], eng: BacktestEngine):
        pass
