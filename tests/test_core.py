import pytest
import os
from forge_tl.config import load_config
from forge_tl.core import Portfolio

def test_config_loading():
    config = load_config()
    assert config.STARTING_CAPITAL == 50000.0

def test_portfolio_default_capital():
    portfolio = Portfolio()
    assert portfolio.get_capital() == 50000.0
