# TASK 22: F&O Alpha Study (Stage B)

## Methodology
Using the 6-day feasibility sample, a limited cross-sectional study of single-stock futures was performed.
Signals tested:
- Basis (Top vs Bottom Quintile)
- Daily OI Change (Top vs Bottom Quintile)

## Results Summary
```csv
Signal,N,ret_1_mean,ret_5_mean
High Basis (Top 20%),226,0.012502926558269784,-0.0057266743941144435
Low Basis (Bottom 20%),228,-0.011618313640880463,-0.012007468052669843
High OI Increase (Top 20%),226,0.002417014828879546,-0.014186701897068334
High OI Decrease (Bottom 20%),227,0.01308186467491827,-0.01016851614204396

```

Due to the limited sample size (6 days, ~900 cross-sectional observations), the results provide an indication of signal direction but lack the statistical power and continuous time-series properties required to establish a tradable alpha. 

A deeper continuous historical study is blocked by the inability to efficiently download 2,250 daily F&O Bhavcopy zip files without a dedicated automated bulk downloader, which the prompt specifically advised against ("deliberately designed to avoid another multi-hour blind download").
