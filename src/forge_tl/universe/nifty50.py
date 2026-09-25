from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Set


class UnsupportedUniverseDate(ValueError):
    """
    Raised when a requested date falls outside the supported
    point-in-time Nifty 50 universe coverage.
    """

    pass


PROJECT_ROOT = Path(__file__).resolve().parents[3]

LEDGER_PATH = (
    PROJECT_ROOT
    / "data"
    / "universe"
    / "nifty50_event_ledger.csv"
)

ANCHOR_DATE = "2016-03-31"

SUPPORTED_START = date(2016, 3, 31)
SUPPORTED_END = date(2024, 12, 31)


# NSE Factbook 2016, Table 4-15:
# Composition of Nifty 50 Index as on March 31, 2016.
#
# IMPORTANT:
# This is the frozen anchor.
#
# TATAMTRDVR is NOT in the anchor. It becomes a constituent
# through the historical event ledger effective 2016-04-01.
#
# INFRATEL is also NOT in this anchor.

ANCHOR_CONSTITUENTS: Set[str] = {
    "ACC",
    "ADANIPORTS",
    "AMBUJACEM",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BANKBARODA",
    "BHEL",
    "BPCL",
    "BHARTIARTL",
    "BOSCH",
    "CAIRN",
    "CIPLA",
    "COALINDIA",
    "DRREDDY",
    "GAIL",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFC",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "ICICIBANK",
    "IDEA",
    "INDUSINDBK",
    "INFY",
    "ITC",
    "KOTAKBANK",
    "LT",
    "LUPIN",
    "M&M",
    "MARUTI",
    "NTPC",
    "ONGC",
    "POWERGRID",
    "PNB",
    "RELIANCE",
    "SBIN",
    "SUNPHARMA",
    "TATAMOTORS",
    "TATAPOWER",
    "TATASTEEL",
    "TCS",
    "TECHM",
    "ULTRACEMCO",
    "VEDL",
    "WIPRO",
    "YESBANK",
    "ZEE",
}
SYMBOL_ALIASES = {
    "BOSCHLTD": "BOSCH",
    "ZEEL": "ZEE",
}


def _normalise_date(
    value: str | date | datetime,
) -> date:
    """
    Convert supported date-like values into datetime.date.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return datetime.strptime(
            value[:10],
            "%Y-%m-%d",
        ).date()

    raise TypeError(
        f"Unsupported date type: {type(value).__name__}"
    )


def _normalise_symbol(value: str) -> str:
    """
    Normalize a canonical symbol.
    """

    return value.strip().upper()


class Nifty50UniverseProvider:
    """
    Point-in-time Nifty 50 universe provider.

    Reconstruction:

        official 2016-03-31 anchor
                    +
        chronological historical event replay

    No current-universe fallback is used.

    Effective-date rule:

        event.effective_date <= requested_date

    Results are cached by requested date.
    """

    def __init__(
        self,
        ledger_path: Path | str = LEDGER_PATH,
    ) -> None:
        self.ledger_path = Path(ledger_path)

        self._events: List[Dict[str, str]] | None = None

        self._membership_cache: Dict[
            str,
            frozenset[str],
        ] = {}

        self._load_ledger()

    # ------------------------------------------------------------------
    # Ledger loading
    # ------------------------------------------------------------------

    def _load_ledger(self) -> List[Dict[str, str]]:
        """
        Load and validate the historical Nifty 50 event ledger.

        The ledger is loaded once and cached.
        """

        if self._events is not None:
            return self._events

        if not self.ledger_path.exists():
            raise FileNotFoundError(
                f"Nifty 50 event ledger not found: "
                f"{self.ledger_path}"
            )

        events: List[Dict[str, str]] = []

        with self.ledger_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:

            reader = csv.DictReader(handle)

            required_columns = {
                "effective_date",
                "event_type",
                "canonical_symbol",
            }

            fieldnames = set(
                reader.fieldnames or []
            )

            missing = required_columns - fieldnames

            if missing:
                raise ValueError(
                    "Ledger missing required columns: "
                    f"{sorted(missing)}"
                )

            for row_number, row in enumerate(
                reader,
                start=2,
            ):
                effective_date = (
                    row.get("effective_date") or ""
                ).strip()

                event_type = (
                    row.get("event_type") or ""
                ).strip().upper()

                canonical_symbol = _normalise_symbol(
                    row.get("canonical_symbol") or ""
                )

                canonical_symbol = SYMBOL_ALIASES.get(
                    canonical_symbol,
                    canonical_symbol,
                )

                if not effective_date:
                    raise ValueError(
                        f"Missing effective_date at "
                        f"ledger row {row_number}"
                    )

                if not canonical_symbol:
                    raise ValueError(
                        f"Missing canonical_symbol at "
                        f"ledger row {row_number}"
                    )

                try:
                    parsed_date = _normalise_date(
                        effective_date
                    )
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Invalid effective_date at "
                        f"ledger row {row_number}: "
                        f"{effective_date!r}"
                    ) from exc

                # Valid operations include:
                #
                # INCLUSION
                # EXCLUSION
                # ACCELERATED_EXCLUSION
                #
                # The operation is identified semantically.

                if (
                    "INCLUSION" not in event_type
                    and "EXCLUSION" not in event_type
                ):
                    raise ValueError(
                        f"Unsupported event_type at "
                        f"ledger row {row_number}: "
                        f"{event_type!r}"
                    )

                events.append(
                    {
                        "date": parsed_date.isoformat(),
                        "type": event_type,
                        "symbol": canonical_symbol,
                    }
                )

        events.sort(
            key=lambda event: (
                event["date"],
                event["type"],
                event["symbol"],
            )
        )

        self._events = events

        return self._events

    # ------------------------------------------------------------------
    # Membership reconstruction
    # ------------------------------------------------------------------

    def get_membership(
        self,
        as_of: str | date | datetime,
    ) -> Set[str]:
        """
        Return Nifty 50 membership applicable on `as_of`.
        """

        requested_date = _normalise_date(as_of)

        if requested_date < SUPPORTED_START:
            raise UnsupportedUniverseDate(
                "Pre-anchor dates are not supported"
            )

        if requested_date > SUPPORTED_END:
            raise UnsupportedUniverseDate(
                "Dates beyond 2024-12-31 are not supported"
            )

        date_key = requested_date.isoformat()

        cached = self._membership_cache.get(
            date_key
        )

        if cached is not None:
            return set(cached)

        membership = set(
            ANCHOR_CONSTITUENTS
        )

        for event in self._load_ledger():

            if event["date"] > date_key:
                break

            event_type = event["type"]
            symbol = event["symbol"]

            if "INCLUSION" in event_type:
                membership.add(symbol)

            elif "EXCLUSION" in event_type:
                membership.discard(symbol)

            else:
                raise ValueError(
                    f"Unsupported event type during replay: "
                    f"{event_type!r}"
                )

        result = frozenset(membership)

        self._membership_cache[
            date_key
        ] = result

        return set(result)

    # ------------------------------------------------------------------
    # Convenience API
    # ------------------------------------------------------------------

    def get_universe(
        self,
        as_of: str | date | datetime,
    ) -> List[str]:
        """
        Return deterministic sorted Nifty 50 symbols.
        """

        return sorted(
            self.get_membership(as_of)
        )

    def is_member(
        self,
        symbol: str,
        as_of: str | date | datetime,
    ) -> bool:
        """
        Return whether a symbol belonged to Nifty 50
        on the requested date.
        """

        normalized_symbol = _normalise_symbol(
            symbol
        )

        return (
            normalized_symbol
            in self.get_membership(as_of)
        )


__all__ = [
    "Nifty50UniverseProvider",
    "UnsupportedUniverseDate",
    "ANCHOR_DATE",
    "ANCHOR_CONSTITUENTS",
    "SUPPORTED_START",
    "SUPPORTED_END",
]