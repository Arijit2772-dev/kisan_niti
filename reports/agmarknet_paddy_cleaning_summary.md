# AGMARKNET Paddy Cleaning Summary

- Input file: `agmarknet_paddy_common_punjab.csv`
- Raw rows: `16284`
- Exact duplicate rows removed: `81`
- Rows with repaired zero price bounds: `19`
- Rows valid after parsing and repair: `16203`
- Duplicate market-date-variety groups aggregated: `2`
- Cleaned record-level rows: `16201`
- Daily model-ready rows: `425`

## Dropped Rows

- No rows dropped after repair.

## Output Files

- `agmarknet_paddy_common_punjab_cleaned_records.csv`
- `agmarknet_paddy_common_punjab_daily_prices.csv`

## Forecasting Target

`target_modal_price_rs_per_quintal` in the daily price file is the
arrival-weighted average modal price for each date.
