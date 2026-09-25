import duckdb
from forge_tl.historical import HistoricalData
hd = HistoricalData()
conn = duckdb.connect()
df = conn.execute(f"SELECT DISTINCT symbol FROM read_parquet('{hd.parquet_dir}/**/*.parquet') WHERE symbol LIKE '%NIFTY%' OR symbol LIKE '%VIX%'").df()
print(df)
