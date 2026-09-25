# NSE F&O 1-Min Stock Data (April 2024 - April 2026)

Open dataset of **214 NSE F&O underlying stocks**, 1-minute OHLCV bars, ~2 years.

Sourced from **Zerodha Kite API** (intraday minute-bar feed). Provided as-is for backtesting / research.

## 📦 Download

The full dataset (compressed ~464 MB) is available as a GitHub Release:

➡️ **[Download stocks_1m_csvs.zip from Releases](../../releases/latest)**

## 📊 Data Specs

| Field | Value |
|---|---|
| Symbols | 214 NSE F&O stocks (NFO + BFO segments) |
| Timeframe | 1-minute bars |
| Date range | 2024-04-01 → 2026-04-30 (~2 years) |
| Format | CSV (gzipped, one file per symbol) |
| Total uncompressed | ~3 GB |
| Total compressed | ~464 MB |
| Total bars | ~5.5 million |

## 📁 File Format

Each file: `{SYMBOL}_1m.csv.gz`

Columns (matches TradingView export format):
```
time, open, high, low, close, CE Breakout Level, PE Breakout Level, Volume
```

- **time**: Unix timestamp in seconds (parse with `pd.to_datetime(df.time, unit='s')`)
- **open, high, low, close**: spot OHLC in INR
- **CE/PE Breakout Level**: empty (placeholder for indicator outputs)
- **Volume**: integer share count

### Python loading example

```python
import pandas as pd

df = pd.read_csv('VOLTAS_1m.csv.gz', compression='gzip')
df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert('Asia/Kolkata')
df = df.set_index('datetime').sort_index()
print(df.head())
```

## 🎯 Symbol Universe

Includes all major NSE F&O underlyings (April 2026 list). Examples:

**Indices' constituents**: RELIANCE, HDFCBANK, ICICIBANK, INFY, TCS, SBIN, AXISBANK, KOTAKBANK, ITC, LT, BHARTIARTL, MARUTI, ASIANPAINT, etc.

**Mid-caps**: VOLTAS, MUTHOOTFIN, GLENMARK, BLUESTARCO, SUPREMEIND, TITAN, LUPIN, DMART, TVSMOTOR, COCHINSHIP, KPITTECH, etc.

**PSUs**: ONGC, BPCL, GAIL, IOC, COALINDIA, NTPC, POWERGRID, etc.

**Adani group**: ADANIENT, ADANIPORTS, ADANIGREEN, ADANIPOWER, ADANIENSOL, etc.

(Full 214-symbol list visible after extraction.)

## 🚦 Use Cases

- Backtest intraday strategies on F&O underlyings
- Volume profile analysis
- Reverse-engineer institutional volume spikes
- Develop ML features (returns, volatility, microstructure)
- Sweep / breakout / mean-reversion research

## ⚖️ License

**Data provided AS-IS for research and educational use.**
- Sourced from Zerodha (which sources from NSE)
- No warranty of accuracy or completeness
- Not for redistribution as a commercial product
- Respect NSE / Zerodha terms of service

## 🙏 Credits

Compiled by **voletiramu** as part of NSE F&O algo-trading research.

Strategy backtests using this data:
- **Krishna** (Sweep Spot V6) — stock options buying
- **Atlas Imbalance** — volume spike + ladder TP
- **Various V2 strategies** — CPR, GZ Zones, Gamma Blast

## 📝 Changelog

**v1.0.0** (2026-05-03):
- Initial release: 214 stocks, 2 years (2024-04 → 2026-04)
- Zerodha 1-min spot equity bars
- Compressed CSV format matching TradingView export
