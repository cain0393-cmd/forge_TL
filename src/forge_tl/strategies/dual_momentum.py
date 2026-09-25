import pandas as pd
from typing import Dict, List

from forge_tl.backtest import BacktestEngine, Order, OrderSide, OrderType
from .base import BaseStrategy


class DualMomentumStrategy(BaseStrategy):
    def __init__(
        self,
        momentum_window: int = 252,
        rebalance_bars: int = 21,
        top_n: int = 3,
    ):
        super().__init__()

        self.momentum_window = momentum_window
        self.rebalance_bars = rebalance_bars
        self.top_n = top_n

        # Frozen sector-ETF baseline universe.
        # MID150BEES is intentionally excluded because it is
        # broad mid-cap exposure rather than a sector ETF.
        self.universe = [
            "BANKBEES",
            "ITBEES",
            "PHARMABEES",
            "FMCGBEES",
            "AUTOBEES",
            "INFRABEES",
        ]

        self.history: Dict[str, List[float]] = {
            symbol: [] for symbol in self.universe
        }

        self.bar_count = 0

    def on_bar(
        self,
        ts: pd.Timestamp,
        bars: Dict[str, dict],
        eng: BacktestEngine,
    ):
        # ---------------------------------------------------------
        # Update historical close prices.
        #
        # A 252-session momentum calculation requires:
        #
        #   Close[t] / Close[t-252] - 1
        #
        # Therefore at least 253 observations are required.
        # ---------------------------------------------------------
        for symbol in self.universe:
            if symbol in bars:
                self.history[symbol].append(bars[symbol]["close"])

                max_history = self.momentum_window + 1

                if len(self.history[symbol]) > max_history:
                    self.history[symbol].pop(0)

        self.bar_count += 1

        # ---------------------------------------------------------
        # Rebalance every N trading bars.
        # ---------------------------------------------------------
        if self.bar_count % self.rebalance_bars != 0:
            return

        # ---------------------------------------------------------
        # Calculate momentum and determine eligible assets.
        # ---------------------------------------------------------
        eligible = []

        for symbol in self.universe:
            hist = self.history[symbol]

            # Need Close[t] and Close[t-252].
            if len(hist) < self.momentum_window + 1:
                continue

            current_close = hist[-1]

            # Exact t-252 observation.
            past_close = hist[-(self.momentum_window + 1)]

            # Exact 252-session relative momentum.
            relative_momentum = (
                current_close / past_close
            ) - 1.0

            # Exact t-21 observation.
            # Since 253 observations are required, this index exists.
            past_close_21 = hist[-22]

            # Absolute momentum:
            #
            # Close[t] / Close[t-21] - 1 > 0
            #
            absolute_momentum = (
                current_close / past_close_21
            ) - 1.0

            if absolute_momentum > 0:
                eligible.append(
                    (symbol, relative_momentum)
                )

        # ---------------------------------------------------------
        # Rank by relative momentum, descending.
        #
        # Alphabetical symbol ordering is the deterministic
        # tie-breaker.
        # ---------------------------------------------------------
        eligible.sort(
            key=lambda item: (-item[1], item[0])
        )

        # ---------------------------------------------------------
        # Select top N eligible assets.
        # ---------------------------------------------------------
        selected = [
            item[0]
            for item in eligible[: self.top_n]
        ]

        # ---------------------------------------------------------
        # Equal-weight target allocation.
        #
        # If fewer than top_n assets qualify, the remaining
        # capital remains in cash.
        # ---------------------------------------------------------
        if selected:
            weight_per_asset = 1.0 / self.top_n
            target_value_per_asset = (
                eng.portfolio.equity * weight_per_asset
            )
        else:
            target_value_per_asset = 0.0

        # ---------------------------------------------------------
        # First exit holdings that are no longer selected.
        # ---------------------------------------------------------
        for symbol, position in list(
            eng.portfolio.positions.items()
        ):
            if symbol not in selected:
                eng.submit_order(
                    Order(
                        symbol,
                        OrderSide.SELL,
                        position.quantity,
                        OrderType.MARKET,
                        ts,
                    )
                )

        # ---------------------------------------------------------
        # Rebalance already-held selected assets.
        # ---------------------------------------------------------
        for symbol, position in list(
            eng.portfolio.positions.items()
        ):
            if symbol not in selected:
                continue

            if symbol not in bars:
                continue

            current_value = (
                position.quantity
                * bars[symbol]["close"]
            )

            difference = (
                target_value_per_asset
                - current_value
            )

            if abs(difference) > bars[symbol]["close"]:
                quantity = int(
                    abs(difference)
                    / bars[symbol]["close"]
                )

                if quantity <= 0:
                    continue

                if difference > 0:
                    eng.submit_order(
                        Order(
                            symbol,
                            OrderSide.BUY,
                            quantity,
                            OrderType.MARKET,
                            ts,
                        )
                    )

                elif difference < 0:
                    eng.submit_order(
                        Order(
                            symbol,
                            OrderSide.SELL,
                            quantity,
                            OrderType.MARKET,
                            ts,
                        )
                    )

        # ---------------------------------------------------------
        # Enter newly selected assets.
        # ---------------------------------------------------------
        for symbol in selected:
            if symbol in eng.portfolio.positions:
                continue

            if symbol not in bars:
                continue

            price = bars[symbol]["close"]

            quantity = int(
                target_value_per_asset / price
            )

            if quantity > 0:
                eng.submit_order(
                    Order(
                        symbol,
                        OrderSide.BUY,
                        quantity,
                        OrderType.MARKET,
                        ts,
                    )
                )