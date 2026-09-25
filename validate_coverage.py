import duckdb

c = duckdb.connect("data/forge_tl.duckdb")

print("\n=== 2016-2024 MARKET BARS ===")
print(
    c.execute("""
        SELECT
            MIN(timestamp) AS earliest,
            MAX(timestamp) AS latest,
            COUNT(DISTINCT timestamp) AS trading_dates,
            COUNT(*) AS rows
        FROM market_bars
        WHERE timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'
    """).fetchall()
)

print("\n=== VIX DATES MISSING FROM NIFTY 50 ===")
print(
    c.execute("""
        SELECT timestamp
        FROM market_bars
        WHERE symbol = 'INDIA VIX'
          AND timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'

        EXCEPT

        SELECT timestamp
        FROM market_bars
        WHERE symbol = 'NIFTY 50'
          AND timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'

        ORDER BY timestamp
    """).fetchall()
)

print("\n=== NIFTY 50 DATES MISSING FROM VIX ===")
print(
    c.execute("""
        SELECT timestamp
        FROM market_bars
        WHERE symbol = 'NIFTY 50'
          AND timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'

        EXCEPT

        SELECT timestamp
        FROM market_bars
        WHERE symbol = 'INDIA VIX'
          AND timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'

        ORDER BY timestamp
    """).fetchall()
)

print("\n=== INDEX ROW COUNTS ===")
print(
    c.execute("""
        SELECT
            timestamp,
            COUNT(*) AS rows,
            STRING_AGG(symbol, ', ' ORDER BY symbol) AS symbols
        FROM market_bars
        WHERE timestamp >= '2016-01-01'
          AND timestamp <= '2024-12-31'
          AND symbol IN ('NIFTY 50', 'INDIA VIX')
        GROUP BY timestamp
        HAVING COUNT(*) != 2
        ORDER BY timestamp
    """).fetchall()
)

c.close()
