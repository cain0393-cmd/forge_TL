from forge_tl.historical import HistoricalData
import duckdb

hd = HistoricalData()
conn = duckdb.connect()
query = f"""
    SELECT DISTINCT symbol
    FROM read_parquet('{hd.parquet_dir}/**/*.parquet')
    WHERE symbol LIKE '%FMCG%' OR symbol LIKE '%BEES%'
"""
print(conn.execute(query).df())
