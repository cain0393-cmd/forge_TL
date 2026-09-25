# Data Quality Exceptions

## 1. INDIA VIX Missing OHLC Records

### Exception Details
During the 2016-01-01 through 2024-12-31 historical backfill, the NIFTY 50 to INDIA VIX date comparison identified exactly two trading dates where NIFTY 50 was successfully recorded but INDIA VIX was quarantined:
- **2021-02-12**
- **2021-03-30**

### Source Record Nature
These records were successfully received from the official NSE index source (e.g., `ind_close_all_DDMMYYYY.csv`). While a valid close value (e.g., `23.05` for 2021-02-12) and zero volume were present, the records contained blank fields for:
- Open
- High
- Low

Example Source Record:
```csv
INDIA VIX,2021-02-12,,,,23.05,0.0,0,0.0,-,-,-,-
```

### Policy Handling
In accordance with the strict OHLC validation policy for the canonical `market_bars` schema, these records were intentionally excluded from ingestion and correctly quarantined. 
- They must **not** be reconstructed or fabricated.
- They remain permanently quarantined in `data/quarantined/`.
- The canonical `market_bars` validation remains strict and requires complete OHLC data.

### Future Resolution
A future, separately defined close-only VIX dataset may safely handle such records under an explicit close-only contract. However, the current OHLCV `market_bars` table intentionally rejects them.
