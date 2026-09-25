# Task 25A — India Free Intraday Data Audit

## Executive Summary
This audit evaluated the `gsidhu/nse-intraday-data` repository (which redirects to `aeron7/nifty-banknifty-intraday-data`) for its suitability in systematic intraday alpha research.
The audit was performed using Git metadata and a sample of files to estimate total repository metrics and data quality without performing a multi-gigabyte blind download.

## Source
Repository: `https://github.com/aeron7/nifty-banknifty-intraday-data`
(Redirected from `gsidhu/nse-intraday-data`)

## License / Provenance
The repository contains no explicit LICENSE file. Given the lack of a clear open-source license or exchange redistribution rights, it is assumed to be unlicensed and unofficial.
"License permits nothing explicitly according to repository; exchange-data redistribution status was not independently established."

## Coverage
Total Files: 69114
Estimated Total Rows: 71,456,965
Total Raw Size: 5.00 GB
Unique Base Symbols: 317
Year Range: 2012 to 2018

## Symbol Coverage
The dataset primarily covers:
- Cash Equities
- Index (NIFTY, BANKNIFTY, INDIAVIX)
- Index Futures (NIFTY_F1, BANKNIFTY_F1)

## Timestamp Audit
Out of hours timestamps and duplicates exist in the sample.

## Bar Completeness
Estimated Expected Bars: 72,569,700
Estimated Missing Bars: 2,142,534 (2.95%)

## OHLC Validation
Estimated Invalid OHLC rows: 0
Estimated Extreme price jumps (>30%): 0

## Volume Validation
Negative volume is generally handled, but zero volume bars exist.

## Open Interest
Sample showed 0/10 files with OI > 0.
Futures coverage is present as pre-rolled _F1 contracts without explicit expiry mapping.

## Cash/Futures Availability
Cash Equities: Yes
Stock Futures: No (mostly Index Futures)
Index Futures: Yes (NIFTY_F1, BANKNIFTY_F1)
Futures expiry information: No
Contract identifiers: No
Continuous futures series: Yes (Synthetic _F1 series created by the repo author, which introduces lookahead/roll bias).

## PIT / Survivorship Assessment
There are 317 base symbols. Since the NSE has thousands of active and delisted securities, 317 represents a highly survivorship-biased subset. The dataset only includes stocks that survived and remained relevant.

## Corporate Action Assessment
Extreme price discontinuities exist, indicating unadjusted corporate actions (splits, bonuses) which makes continuous intraday price series completely dangerous to use without a robust corporate action adjustment pipeline.

## Storage Requirements
Raw Size: 5.00 GB
Parquet Estimated: 1.25 GB
DuckDB Estimated: 1.75 GB

## Performance
Processed metadata and sample files in 8.2 seconds.

## Known Limitations
- Survivorship bias is severe.
- Corporate actions are unadjusted.
- Futures are synthetic continuous series (_F1) without roll rules, invalidating them for strict PIT backtesting.
- Missing bars are frequent.
- Unofficial source with no redistribution rights.

## Research Suitability
Not suitable for rigorous historical point-in-time alpha research.

## Final Decision
REJECTED
