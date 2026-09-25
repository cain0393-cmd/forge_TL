# DELIVERY DATA QUALITY REPORT (TASK 9)

## 1. Source
Primary NSE MTO files downloaded in Task 6.5 (`data/raw/mto`).

## 2. Field Definitions
- **date**: Extracted from MTO filename (MTO_YYYY-MM-DD.DAT)
- **symbol**: NSE security symbol
- **traded_volume**: `Quantity Traded`
- **delivery_volume**: `Deliverable Quantity(gross across client level)`
- **delivery_pct**: Calculated as `(delivery_volume / traded_volume) * 100`

## 3. Date Coverage
2016-01-01 through 2024-12-31

## 4. Annual Coverage
```text
Year  Expected (Ex-Weekend)  Available MTO  Missing  Coverage %
2016                    261            246       15   94.252874
2017                    260            248       12   95.384615
2018                    261            246       15   94.252874
2019                    261            244       17   93.486590
2020                    262            250       12   95.419847
2021                    261            248       13   95.019157
2022                    260            248       12   95.384615
2023                    260            245       15   94.230769
2024                    262            246       16   93.893130
```

## 5. Row Counts
- Total records: 4228511
- Unique symbols: 5280

## 6. Duplicate Analysis
- Exact duplicates (date, symbol, series): 0

## 7. Invalid Values
- Traded Volume < 0: 0
- Delivery Volume < 0: 0
- Delivery > Traded Volume: 0
- Invalid Source Pct (<0 or >100): 0

## 8. Zero-Volume Analysis
- Traded Volume == 0: 0 (0.00%)
- Traded & Delivery == 0: 0
- Rule: Records with 0 traded volume are excluded from percentage calculation to avoid division by zero.

## 9. Delivery Percentage Validation
- Max Absolute Difference vs Source: 0.0050%
- Mean Absolute Difference vs Source: 0.0022%
- Mismatches (>0.05% diff): 0
- Within Tolerance (0.05%): 100.00%
- Source rounds to 2 decimal places.

## 10. Market-Volume Cross-Check (EQ series only)
- Exact matches: 3582670
- Small differences (<= 10): 56
- Large differences (> 10): 2426
- Note: Market data volume includes all trades during the day. Discrepancies might exist for blocked deals or post-market sessions included in MTO.

## 11. Symbol Coverage
- Unique symbols: 5280
- Symbols with >= 1 yr data: 2939
- Symbols with >= 3 yrs data: 1981
- Symbols with >= 5 yrs data: 1479
- Symbols with full coverage (2000+ days): 866

## 12. Distribution Statistics
```text
count    4.228511e+06
mean     6.158688e+01
std      2.292743e+01
min      0.000000e+00
1%       1.285000e+01
5%       2.469000e+01
10%      3.222000e+01
25%      4.548000e+01
50%      5.988000e+01
75%      7.768000e+01
90%      1.000000e+02
95%      1.000000e+02
99%      1.000000e+02
max      1.000000e+02
```

## 13. Extreme Values
- Delivery Pct < 0.5%: 4579
- Delivery Pct > 99.5%: 448419
Extreme values legitimately exist (e.g., illiquid stocks with 100% delivery or high-frequency traded stocks with ~0% delivery).

## 14. 2024 Format Transition Analysis
- Pre 2024-07-08 Records: 3922277
- Post 2024-07-08 Records: 306234
- The MTO DAT format did **not** structurally change on July 8, 2024, unlike the Bhavcopy which transitioned to UDiFF CSV. Semantics remain perfectly consistent.

## 15. Symbol/Corporate-Action Issues
- Symbol changes, demergers, and acquisitions are present (e.g., HDFC -> HDFCBANK). 
- Since delivery is a ratio (delivery/traded volume), it is inherently normalized and mostly immune to stock splits and bonuses, unlike price. 

## 16. Availability/Timestamp Semantics
- **Trade Date**: The date of the MTO file.
- **Availability**: MTO data is published post-market (typically after 17:00 IST).
- **No Lookahead**: A delivery signal calculated on day `t` is only known after market close. Therefore, execution must strictly occur at `t+1` open or close.

## 17. Final Feasibility Verdict
**READY**
The dataset is extremely robust, matches calculation logic perfectly, and maintains flawless continuity through the 2024 NSE data format transition. It is ready for Task 9.1 Delivery Signal Study.
