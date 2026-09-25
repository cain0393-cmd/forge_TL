# PEAD Data Architecture & Feasibility Gate

## A. Executive Verdict
**BLOCKED**

## B. Sources
1. **National Stock Exchange (NSE)**
   - **Provider**: NSE India (Official Exchange)
   - **URL**: `https://www.nseindia.com/companies-listing/corporate-filings-financial-results`
   - **Data type**: Raw Financial Results (Actual EPS, Revenue, Announcement Timestamps)
   - **Period**: Theoretically available historically.
   - **Fields**: Symbol, Period End, Actual EPS, Actual Revenue, Announcement Date, Announcement Timestamp.
   - **Access method**: API / Web Scraping
   - **Reliability**: Officially reliable, but automated extraction of 9 years of data is currently blocked by strict Web Application Firewalls (Cloudflare 403/503 errors).
2. **Consensus Estimates (IBES / FactSet / Bloomberg / Refinitiv)**
   - **Provider**: Commercial Institutional Vendors
   - **URL**: N/A
   - **Data type**: Expected EPS, Expected Revenue
   - **Period**: 2016-2024
   - **Fields**: Expected EPS, Expected Revenue, Number of Estimates.
   - **Access method**: Licensed Institutional Feed.
   - **Reliability**: High, but absolutely unavailable locally in `forge_TL` or via free public scraping.

## C. Coverage
- **2016 - 2024**: 0% local coverage. No historical earnings records exist in the repository.

## D. Field Completeness
Because no data can be acquired:
- **Exact Timestamps**: 0%
- **Actual EPS**: 0%
- **Actual Revenue**: 0%
- **Expected EPS (Consensus)**: 0%
- **Expected Revenue (Consensus)**: 0%

## E. Timing Quality
- **Exact Timestamp vs Date-only**: NSE officially maintains exact broadcast timestamps for corporate announcements, meaning Pre-Market, Intraday, and Post-Market classifications are theoretically possible. However, the data cannot be acquired.

## F. Consensus Availability
**NO**. Historical consensus (Expected EPS / Expected Revenue) is not provided by the exchange and cannot be obtained without an expensive commercial institutional data feed. Consequently, "Classic PEAD" (which relies on standardizing the surprise relative to analyst expectations) is fundamentally impossible to test.

## G. PIT Universe
**NO**. A point-in-time historical Nifty 200 universe cannot be constructed currently. The repository only contains historical Nifty 50 ledgers (`nifty50_event_ledger.csv`). Constructing the Nifty 200 historically without survivorship bias requires tracking hundreds of index changes over 9 years, which we do not have data for.

## H. Known Limitations
1. Without Consensus Estimates, the strategy would have to rely on Year-over-Year (YoY) or Quarter-over-Quarter (QoQ) actual growth, which is a fundamentally different hypothesis than Classic PEAD.
2. Even if we redefined PEAD to use YoY actual growth, we still cannot scrape the raw Actual EPS/Revenue and their exact dissemination timestamps due to WAF blocking.
3. Survivorship bias would severely compromise the test if the current Nifty 200 were used as a historical substitute.

## I. Recommended Next Step
**BLOCKED_NEEDS_EXTERNAL_DATA**
