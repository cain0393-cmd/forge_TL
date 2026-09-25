# Task 25B — Free Indian Intraday Data Source Discovery

## Objective
To find and screen alternative freely accessible historical Indian/NSE intraday market-data sources that satisfy rigorous quantitative point-in-time (PIT) research standards.

## Hard Constraint
Research-data budget = ₹0. 
No purchases, subscriptions, or commercial feeds.

## Sources Investigated
1. **GitHub Repositories** (voletiramu, rbhatia46)
2. **Kaggle Datasets**
3. **Broker APIs** (Zerodha, Upstox, Angel One, Dhan, Fyers)
4. **NSE Public Sources**

## Candidate 1
**ID:** C1
**Source:** voletiramu/nse-fno-1min-data
**Provider:** GitHub (voletiramu)
**Data Type:** 1-minute OHLCV (Spot Equity, Not F&O)
**Date Range:** 2024-04-01 to 2026-04-30
**Evaluation:** This dataset claims to provide F&O data, but actually provides underlying spot cash equity prices. It includes only 214 symbols active as of April 2026, meaning it is fundamentally contaminated with survivorship bias. It is also unclear if corporate actions are handled correctly.
**Classification:** REJECTED

## Candidate 2
**ID:** C2
**Source:** rbhatia46/Intraday-1-Minute-data-Nifty-BankNifty
**Provider:** GitHub (rbhatia46)
**Data Type:** 1-minute OHLCV (Index only)
**Date Range:** 2012 to 2023
**Evaluation:** Because this contains only NIFTY and BANKNIFTY spot index data, it completely sidesteps the corporate-action and survivorship bias issues that plague equity datasets. However, it is fundamentally limited in breadth and lacks futures/options derivatives data.
**Classification:** PARTIAL_CANDIDATE (Usable ONLY for pure index trend research).

## Candidate 3
**ID:** C3
**Source:** Upstox Historical API
**Provider:** Upstox
**Data Type:** 1-minute OHLCV
**Date Range:** Jan 2022 to Present
**Evaluation:** Upstox provides an entirely free API for fetching historical data for stocks, futures, and options. While rate limits apply (approx. 25 req/sec), it supports expired derivatives contracts natively and allows explicit extraction without synthetic roll leakage. 
**Classification:** PARTIAL_CANDIDATE (Requires writing a pipeline to slowly hydrate a local database; history is relatively short, starting 2022).

## Candidate 4
**ID:** C4
**Source:** Angel One SmartAPI
**Provider:** Angel One
**Data Type:** 1-minute OHLCV
**Date Range:** T-30 Days
**Evaluation:** Angel One offers a free API, but strictly caps 1-minute historical data to the last 30 days. This makes it useless for long-term quantitative backtesting.
**Classification:** REJECTED

## Candidate 5
**ID:** C5
**Source:** Kaggle Nifty-50 1-Min Data (Generic)
**Provider:** Various Kaggle Users
**Data Type:** 1-minute OHLCV
**Date Range:** ~2015 to ~2023
**Evaluation:** Kaggle datasets for Indian markets are routinely uploaded by students/hobbyists. They invariably extract the *current* Nifty 50 constituents and pull historical data for them, hardcoding lookahead survivorship bias into the file structure. Provenance and CA adjustments are entirely unknown.
**Classification:** REJECTED

## Broker/API Investigation
- **Zerodha Kite:** Requires paid subscription (₹2000/mo API + ₹2000/mo Historical).
- **DhanHQ:** Free for trading, but requires ₹499/mo for Historical Data API.
- **Fyers:** Free API, provides historical data similar to Upstox.
- **Upstox:** Best free API candidate, offering data back to 2022 with expired F&O contract support.

## NSE Public-Source Investigation
The NSE does **not** provide free intraday data. Its free historical data is strictly End-of-Day (EOD) Bhavcopies and indices. Any intraday order/trade data requires thousands of dollars in annual licensing fees via their paid data products. We will not scrape or bypass their commercial walls.

## Candidate Comparison
| ID | Source | Breadth | PIT Safe | Classification |
|---|---|---|---|---|
| C1 | voletiramu GitHub | High (214 EQ) | No | REJECTED |
| C2 | rbhatia46 GitHub | Low (2 Index) | Yes | PARTIAL_CANDIDATE |
| C3 | Upstox API | Very High | Yes | PARTIAL_CANDIDATE |
| C4 | Angel One API | Very High | Yes (but short) | REJECTED |
| C5 | Kaggle | Low (50 EQ) | No | REJECTED |

## PIT Assessment
Almost all free community GitHub/Kaggle datasets fail PIT checks. They lack mapping of delisted companies, fail to record index constituent changes, and smooth over corporate actions without retaining unadjusted prices. Broker APIs (like Upstox) solve this by providing accurate historical ticks, provided you can resolve the expired instrument tokens.

## Licensing / Provenance Assessment
Community datasets are uploaded as-is, often violating broker TOS. Broker APIs are explicitly licensed for personal use and API development, which fits our research budget perfectly, provided we accept the rate limits.

## Storage / Access Assessment
Scraping from an API (C3) will require minimal initial storage but significant execution time due to rate limits. Downloading GitHub repos requires minimal time but yields dirty data.

## Rejected Sources
- `gsidhu/nse-intraday-data` (Task 25A - Severe Bias)
- `voletiramu/nse-fno-1min-data` (Severe Bias)
- Kaggle Nifty-50 compilations (Severe Bias)
- Angel One (Limited History)
- Dhan/Zerodha (Not Free)

## Research Candidates
We have identified two partial candidates:
1. **rbhatia46/Intraday-1-Minute-data-Nifty-BankNifty**: Excellent for simple, index-only intraday studies without CA contamination.
2. **Upstox Free API**: The only viable path to a comprehensive, PIT-safe universe (Cash + F&O), requiring a bespoke slow-hydration pipeline.

## Final Decision
**FINAL_DECISION = NO_FREE_PIT_INTRADAY_SOURCE**
(We do not have a single, monolithic, pre-packaged, fully research-ready free source).

## Recommended Next Audit
If the project requires broad cross-sectional equity/F&O intraday data, I recommend pivoting to build a slow-hydration historical ingestion pipeline using the **Upstox API**. 
If the project only requires index trend research, **Candidate C2** can be used immediately.
