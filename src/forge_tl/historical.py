import os
import shutil

import duckdb
import pandas as pd

from .config import config


class ParquetExporter:
    @staticmethod
    def export(db_path: str = None, parquet_dir: str = None):
        if db_path is None:
            db_path = config.DB_PATH
        if parquet_dir is None:
            parquet_dir = config.PARQUET_DIR

        conn = duckdb.connect(db_path)

        try:
            # Read the complete current state of DuckDB.
            # Ordering makes the exported dataset deterministic.
            df = conn.execute(
                """
                SELECT *,
                       YEAR(timestamp) AS year
                FROM market_bars
                ORDER BY timestamp ASC, symbol ASC
                """
            ).df()
        finally:
            conn.close()

        # Always remove the existing Parquet dataset first.
        #
        # This is intentionally done BEFORE the empty-data check.
        # Otherwise, an empty DuckDB source could leave stale Parquet
        # data from a previous export.
        if os.path.exists(parquet_dir):
            shutil.rmtree(parquet_dir)

        # If DuckDB contains no rows, the correct Parquet state is
        # simply an empty/non-existent dataset.
        if df.empty:
            return

        os.makedirs(parquet_dir, exist_ok=True)

        # Write the current DuckDB state as a partitioned Parquet dataset.
        df.to_parquet(
            parquet_dir,
            partition_cols=["year"],
            engine="pyarrow",
            index=False,
        )


class HistoricalData:
    def __init__(self, parquet_dir: str = None):
        self.parquet_dir = (
            parquet_dir if parquet_dir else config.PARQUET_DIR
        )

    def query(
        self,
        symbols=None,
        start_date=None,
        end_date=None,
    ) -> pd.DataFrame:

        if (
            not os.path.exists(self.parquet_dir)
            or not os.listdir(self.parquet_dir)
        ):
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "symbol",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            )

        conn = duckdb.connect()

        try:
            query = f"""
                SELECT
                    timestamp,
                    symbol,
                    open,
                    high,
                    low,
                    close,
                    volume
                FROM read_parquet(
                    '{self.parquet_dir}/**/*.parquet'
                )
            """

            conditions = []

            if symbols is not None:
                if isinstance(symbols, str):
                    symbols = [symbols]

                symbols_str = ", ".join(
                    [f"'{s}'" for s in symbols]
                )

                conditions.append(
                    f"symbol IN ({symbols_str})"
                )

            if start_date is not None:
                conditions.append(
                    f"timestamp >= '{start_date}'"
                )

            if end_date is not None:
                conditions.append(
                    f"timestamp <= '{end_date}'"
                )

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                ORDER BY timestamp ASC, symbol ASC
            """

            return conn.execute(query).df()

        finally:
            conn.close()

    def detect_duplicates(self) -> pd.DataFrame:
        if (
            not os.path.exists(self.parquet_dir)
            or not os.listdir(self.parquet_dir)
        ):
            return pd.DataFrame()

        conn = duckdb.connect()

        try:
            query = f"""
                SELECT
                    timestamp,
                    symbol,
                    COUNT(*) AS cnt
                FROM read_parquet(
                    '{self.parquet_dir}/**/*.parquet'
                )
                GROUP BY timestamp, symbol
                HAVING cnt > 1
            """

            return conn.execute(query).df()

        finally:
            conn.close()