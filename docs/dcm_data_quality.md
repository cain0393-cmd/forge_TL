# DCM-Trend Data & Event-Timing Feasibility Study

## Executive Summary
This document outlines the data discovery and feasibility evaluation for the DCM-Trend hypothesis (Derivative-Confirmed Momentum). The evaluation confirms that while core Futures and Open Interest data is theoretically accessible from NSE archives, the original hypothesis is definitively **BLOCKED** by the absolute unavailability of two critical components: Historical Point-in-Time Sector Classifications and Institutional Flow data.

## Research Period
2016-01-01 through 2024-12-31

## Source Discovery
- **Futures & OI**: NSE Daily F&O Bhavcopy archives (`nsearchives.nseindia.com/content/historical/DERIVATIVES/...`).
- **PIT F&O Universe**: Implicitly inferable from the daily Bhavcopy contracts.
- **Sector Data**: No historical source identified locally or publicly via NSE without survivorship bias.
- **Institutional Flow**: Previously established as blocked due to WAF restrictions (Task 13).

## Data Availability

### Futures Data
- **DATA_EXISTS**: YES
- **DATA_DISCOVERED**: YES
- **DATA_ACCESSIBLE**: YES (via NSE archives).
- **DATA_COMPLETE**: UNKNOWN (Requires downloading and parsing ~2,200 daily ZIP files).
- **DATA_USABLE**: NO (Not normalized locally; engineering acquisition pipeline required).

### Open Interest
- **DATA_EXISTS**: YES
- **DATA_DISCOVERED**: YES
- **DATA_ACCESSIBLE**: YES (Included in Bhavcopy).
- **DATA_COMPLETE**: UNKNOWN
- **PIT_SAFE**: YES (if applied correctly at T+1).

### Contract Identity
- **Status**: Contracts are deterministically identified in the Bhavcopy using `INSTRUMENT` (e.g., FUTSTK), `SYMBOL`, and `EXPIRY_DT`. 

### Expiry / Rollover
- **Status**: Safely handling rollovers requires constructing an expiry calendar and mapping Days-to-Expiry (DTE) for every contract dynamically. This is a non-trivial engineering task but mathematically feasible once data is acquired.

### PIT F&O Universe
- **Status**: FEASIBLE. It can be perfectly reconstructed by scanning the daily Bhavcopies for active `FUTSTK` symbols, thus completely avoiding survivorship bias.

### Sector Data
- **Status**: **BLOCKED**. NSE provides current index constituents but no single, comprehensive historical point-in-time ledger for sector reclassifications over the 2016-2024 period. Applying current sectors to historical equities introduces severe survivorship and look-ahead bias.

### Institutional Flow Dependency
- **Status**: **BLOCKED**. Task 13 confirmed that programmatic historical retrieval of FII/DII aggregates and Bulk/Block deals is prevented by strict WAF protections.

## Timing / Availability
Futures OI is published by the exchange post-market (EOD). Therefore, using `OI[t]` for a 15:15 `SIGNAL[t]` is a lookahead violation. The earliest safe execution is `OPEN[t+1]`. 

## Format Changes
Historical Bhavcopies are known to have structural column shifts (e.g., introduction of new fields or adjustments to column ordering over a 9-year span). An acquisition pipeline would need multiple parser versions.

## Liquidity Feasibility
- **Status**: FEASIBLE. The 20-day average traded value can be safely computed using the existing validated Parquet equity data without lookahead.

## Critical Dependencies
1. **DCM-A (Price breakout)**: AVAILABLE
2. **DCM-B (Futures OI expansion)**: ACQUISITION_REQUIRED
3. **DCM-C (Sector relative strength)**: BLOCKED
4. **DCM-D (Institutional-flow)**: BLOCKED

## Final Verdict
**DCM_BLOCKED**
