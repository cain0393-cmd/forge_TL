# INSTITUTIONAL FLOW DATA QUALITY & FEASIBILITY REPORT

## Source Coverage
- **Source**: National Stock Exchange of India (NSE) Official Website / Archives.
- **Years available**: Data exists structurally for 2016–2024.
- **Records**: 0 local records retrieved.
- **Missing years**: 100% missing locally.
- **Retrieval failures**: Automated retrieval of historical FII/DII and Bulk/Block deals over 9 years is blocked by NSE's aggressive WAF (Web Application Firewall, Cloudflare 403/503 errors). Attempting to scrape thousands of days without an authorized institutional feed is technically unviable. 

## Data Concepts Evaluation
- **DATA_EXISTS**: Yes, the data is generated and published by the exchange.
- **DATA_DISCOVERED**: Yes, the schemas and endpoints are known.
- **DATA_ACCESSIBLE**: No, strict bot-protection prevents programmatic historical retrieval.
- **DATA_USABLE**: No, since the data cannot be acquired in full, no robust IS/OOS backtesting can be performed.

---

## FII/FPI
- **Coverage**: 0% locally.
- **Fields**: Historically includes Date, Buy Value, Sell Value, Net Value.
- **Timestamp/Availability**: Only Date is provided. The aggregate is typically published post-market (approx. 18:00 IST). Cannot be used for same-day 15:15 signals. Earliest safe signal: T+1 Open.
- **Anomalies**: Formats and definitions have been mostly stable, but reliable retrieval is blocked.

## DII
- **Coverage**: 0% locally.
- **Fields**: Historically includes Date, Buy Value, Sell Value, Net Value.
- **Timestamp/Availability**: Published post-market alongside FII data. Earliest safe signal: T+1 Open.
- **Anomalies**: Similar to FII/FPI.

## Bulk Deals
- **Coverage**: 0% locally.
- **Fields**: Date, Symbol, Security Name, Client Name, Buy/Sell, Quantity, Trade Price.
- **Timestamp Quality**: Historical CSV archives from NSE typically provide only the `Date`, lacking exact intraday execution or publication timestamps. Thus, they must be safely assumed as post-market information for historical research purposes.

## Block Deals
- **Coverage**: 0% locally.
- **Fields**: Date, Symbol, Security Name, Client Name, Buy/Sell, Quantity, Trade Price.
- **Timestamp Quality**: Similar to Bulk Deals, historical records only provide `Date`. While the trades occur in pre-defined windows (e.g., morning and afternoon windows), the lack of precise dissemination timestamps in the daily files forces a post-market safety assumption unless painstakingly cross-referenced with tick data. 
- **Anomalies**: SEBI changed block deal regulations in 2017 (modifying the time windows and value thresholds), meaning the definition of a block deal is not perfectly consistent across the 2016-2024 research period.

## Delivery
- **Coverage**: Extensively evaluated in Task 9.
- **Quality**: Existing Task 9 dataset is pristine and usable.
- **Status**: Can be used conditionally, but primary institutional flow data is missing.

## Symbol Mapping
- **Historical/Canonical Mappings**: No institutional events data to map. If we had the data, we would use the existing `forge_TL` historical universe mapping methodology to track symbol changes over time.

## Point-in-Time (PIT) Safety
- **FAIL / BLOCKED**. Without exact publication timestamps for bulk/block deals, assuming they are available intraday introduces lookahead bias. Furthermore, since the data cannot be fetched, no PIT database can be constructed.
