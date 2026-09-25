from typing import Optional
from .config import config

class Portfolio:
    def __init__(self, capital: Optional[float] = None):
        self.capital = capital if capital is not None else config.STARTING_CAPITAL

    def get_capital(self) -> float:
        return self.capital
