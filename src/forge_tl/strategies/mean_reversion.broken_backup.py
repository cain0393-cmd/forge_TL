from __future__ import annotations

import math
from typing import Dict, List

import pandas as pd

from forge_tl.backtest import (
    BacktestEngine,
    Order,
    OrderSide,
    OrderType,
)

from forge_tl.universe.nifty50 import (
    Nifty50UniverseProvider,
    UnsupportedUniverseDate,
)

from .base import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Statistical Mean Reversion strategy.

    Signal construction:

        daily_return[t] =
            close[t] / close[t-1] - 1

        CR5 =
            product(1 + daily_return[-5:]) - 1

        mu20 =
            mean(last 20 daily returns)

        sigma20 =
            sample standard deviation of last 20 daily returns

        Z =
            (CR5 - 5 * mu20)
            /
            (sqrt(5) * sigma20)

    Entry:
        Z < entry_z

    Exit:
        Z > exit_z
        OR
        holding period >= max_holding_bars

    Baseline parameters:

        mean_window = 20
        return_window = 5
        entry_z = -2.0
        exit_z = 0.0
        max_holding_bars = 5
        max_holdings = 5

    Universe:
        Point-in-time Nifty 50.

    Execution:
        Orders are submitted at the current bar and filled
        according to the BacktestEngine's next-bar execution
        semantics.
    """

    def __init__(
        self,
        universe_provider: Nifty50UniverseProvider | None = None,
        mean_window: int = 20,
        return_window: int = 5,
        entry_z: float = -2.0,
        exit_z: float = 0.0,
        max_holding_bars: int = 5,
        max_holdings: int = 5,
    ) -> None:

        super().__init__()

        self.universe_provider = (
            universe_provider
            if universe_provider is not None
            else Nifty50UniverseProvider()
        )

        self.mean_window = mean_window
        self.return_window = return_window

        self.entry_z = entry_z
        self.exit_z = exit_z

        self.max_holding_bars = (
            max_holding_bars
        )

        self.max_holdings = max_holdings

        # Symbol -> historical closes
        self.history: Dict[
            str,
            List[float],
        ] = {}

        # Symbol -> bar number on which entry was submitted
        self.entry_bars: Dict[
            str,
            int,
        ] = {}

        self.bar_count = 0

    # ------------------------------------------------------------------
    # Statistical calculation
    # ------------------------------------------------------------------

    def _calculate_z_score(
        self,
        closes: List[float],
    ) -> float | None:
        """
        Calculate the baseline statistical mean-reversion Z-score.

        The strategy requires:

            mean_window + 1

        closes in order to produce `mean_window` daily returns.
        """

        required_closes = (
            self.mean_window + 1
        )

        if len(closes) < required_closes:
            return None

        # --------------------------------------------------------------
        # Convert prices into daily returns.
        #
        # Explicit Python floats are used here so Pylance does not
        # treat Pandas aggregation results as generic Scalar values.
        # --------------------------------------------------------------

        recent_closes = closes[
            -required_closes:
        ]

        daily_returns: List[float] = []

        for index in range(
            1,
            len(recent_closes),
        ):
            previous_close = float(
                recent_closes[index - 1]
            )

            current_close = float(
                recent_closes[index]
            )

            if previous_close <= 0:
                return None

            daily_return = (
                current_close
                / previous_close
            ) - 1.0

            daily_returns.append(
                float(daily_return)
            )

        # We need at least `mean_window` returns.
        if len(daily_returns) < self.mean_window:
            return None

        # --------------------------------------------------------------
        # 5-day compounded cumulative return
        # --------------------------------------------------------------

        if (
            len(daily_returns)
            < self.return_window
        ):
            return None

        last_returns = daily_returns[
            -self.return_window:
        ]

        cr_product = 1.0

        for daily_return in last_returns:
            cr_product *= (
                1.0 + daily_return
            )

        cr5 = cr_product - 1.0

        # --------------------------------------------------------------
        # 20-day mean and standard deviation
        # --------------------------------------------------------------

        last_mean_returns = daily_returns[
            -self.mean_window:
        ]

        mu20 = (
            sum(last_mean_returns)
            / len(last_mean_returns)
        )

        # Sample standard deviation, matching
        # Pandas Series.std() default ddof=1.
        if len(last_mean_returns) < 2:
            return None

        squared_deviations = [
            (value - mu20) ** 2
            for value in last_mean_returns
        ]

        variance = (
            sum(squared_deviations)
            / (len(last_mean_returns) - 1)
        )

        sigma20 = math.sqrt(
            variance
        )

        if (
            not math.isfinite(sigma20)
            or sigma20 <= 0.0
        ):
            return None

        # --------------------------------------------------------------
        # Required Z-score
        # --------------------------------------------------------------

        z_score = (
            cr5
            - self.return_window * mu20
        ) / (
            math.sqrt(
                self.return_window
            )
            * sigma20
        )

        if not math.isfinite(z_score):
            return None

        return float(z_score)

    # ------------------------------------------------------------------
    # Strategy event
    # ------------------------------------------------------------------

    def on_bar(
        self,
        ts: pd.Timestamp,
        bars: Dict[str, dict],
        eng: BacktestEngine,
    ) -> None:

        self.bar_count += 1

        # --------------------------------------------------------------
        # Point-in-time Nifty 50 universe
        #
        # ONLY unsupported date coverage is converted into an empty
        # universe.
        #
        # Ordinary ValueError must propagate. This prevents malformed
        # ledgers/configuration/provider errors from being silently
        # interpreted as "no stocks available".
        # --------------------------------------------------------------

        try:
            current_universe = (
                self.universe_provider
                .get_universe(ts)
            )

        except UnsupportedUniverseDate:
            current_universe = []

        # --------------------------------------------------------------
        # Update historical prices.
        # --------------------------------------------------------------

        for symbol in current_universe:

            if symbol not in bars:
                continue

            close = bars[symbol].get(
                "close"
            )

            if close is None:
                continue

            try:
                close_value = float(close)
            except (TypeError, ValueError):
                continue

            if (
                not math.isfinite(
                    close_value
                )
                or close_value <= 0.0
            ):
                continue

            if symbol not in self.history:
                self.history[symbol] = []

            self.history[symbol].append(
                close_value
            )

            # Keep only enough history for the signal.
            max_history = (
                self.mean_window + 1
            )

            if (
                len(self.history[symbol])
                > max_history
            ):
                self.history[symbol] = (
                    self.history[symbol][
                        -max_history:
                    ]
                )

        # --------------------------------------------------------------
        # Exit existing positions
        # --------------------------------------------------------------

        for symbol, position in list(
            eng.portfolio.positions.items()
        ):

            if position.quantity <= 0:
                continue

            if symbol not in bars:
                continue

            if symbol not in self.history:
                continue

            z_score = self._calculate_z_score(
                self.history[symbol]
            )

            if z_score is None:
                continue

            entry_bar = self.entry_bars.get(
                symbol
            )

            if entry_bar is None:
                holding_bars = 0
            else:
                holding_bars = (
                    self.bar_count
                    - entry_bar
                )

            should_exit = (
                z_score > self.exit_z
                or
                holding_bars
                >= self.max_holding_bars
            )

            if not should_exit:
                continue

            eng.submit_order(
                Order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=position.quantity,
                    order_type=OrderType.MARKET,
                    created_at=ts,
                )
            )

            self.entry_bars.pop(
                symbol,
                None,
            )

        # --------------------------------------------------------------
        # Determine currently held positions.
        # --------------------------------------------------------------

        held_symbols = {
            symbol
            for symbol, position
            in eng.portfolio.positions.items()
            if position.quantity > 0
        }

        # --------------------------------------------------------------
        # Respect maximum holdings.
        # --------------------------------------------------------------

        available_slots = (
            self.max_holdings
            - len(held_symbols)
        )

        if available_slots <= 0:
            return

        # --------------------------------------------------------------
        # Generate entry candidates.
        # --------------------------------------------------------------

        candidates = []

        for symbol in current_universe:

            if symbol in held_symbols:
                continue

            if symbol not in bars:
                continue

            if symbol not in self.history:
                continue

            z_score = self._calculate_z_score(
                self.history[symbol]
            )

            if z_score is None:
                continue

            if z_score < self.entry_z:
                candidates.append(
                    (
                        symbol,
                        z_score,
                    )
                )

        # --------------------------------------------------------------
        # Deterministic ranking.
        #
        # Most negative Z-score first.
        # Symbol breaks ties deterministically.
        # --------------------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item[1],
                item[0],
            )
        )

        selected = candidates[
            :available_slots
        ]

        if not selected:
            return

        # --------------------------------------------------------------
        # Equal allocation.
        #
        # Maximum five holdings means each position receives
        # approximately 1 / max_holdings of equity.
        # --------------------------------------------------------------

        allocation_per_position = (
            eng.portfolio.equity
            / self.max_holdings
        )

        for symbol, _z_score in selected:

            if symbol not in bars:
                continue

            price = bars[symbol].get(
                "close"
            )

            if price is None:
                continue

            try:
                price_value = float(price)
            except (TypeError, ValueError):
                continue

            if (
                not math.isfinite(
                    price_value
                )
                or price_value <= 0.0
            ):
                continue

            quantity = int(
                allocation_per_position
                / price_value
            )

            if quantity <= 0:
                continue

            eng.submit_order(
                Order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    quantity=quantity,
                    order_type=OrderType.MARKET,
                    created_at=ts,
                )
            )

            self.entry_bars[
                symbol
            ] = self.bar_count