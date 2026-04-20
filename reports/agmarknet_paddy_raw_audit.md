# AGMARKNET Paddy Raw Data Audit

## File

- Input file: `agmarknet_paddy_common_punjab.csv`
- Total rows: `16284`
- Total columns: `16`

## Identity Checks

- States found: `{'Punjab': 16284}`
- Commodities found: `{'Paddy(Common)': 16284}`
- Unique markets: `176`
- Unique varieties: `13`

## Date Checks

- Invalid dates: `0`
- Earliest date: `2020-09-21`
- Latest date: `2025-11-27`

## Duplicate Checks

- Exact duplicate rows: `81`
- Duplicate market-date-variety keys: `83`

## Price Consistency Checks

- Rows where min <= modal <= max is false: `18`

## Missing Values

- `state_id`: `0`
- `state_name`: `0`
- `commodity_id`: `0`
- `commodity_name`: `0`
- `year`: `0`
- `month`: `0`
- `market_name`: `0`
- `arrival_date`: `0`
- `arrival_date_raw`: `0`
- `variety`: `0`
- `arrivals_metric_tonnes`: `0`
- `total_arrivals_metric_tonnes`: `0`
- `minimum_price_rs_per_quintal`: `0`
- `maximum_price_rs_per_quintal`: `0`
- `modal_price_rs_per_quintal`: `0`
- `source_url`: `0`

## Numeric Column Summary

- `arrivals_metric_tonnes`: count=16284, min=0.10, mean=2551.17, max=157737.00; invalid=`0`; non_positive=`0`
- `total_arrivals_metric_tonnes`: count=16284, min=0.10, mean=2566.61, max=157737.00; invalid=`0`; non_positive=`0`
- `minimum_price_rs_per_quintal`: count=16284, min=0.00, mean=2143.82, max=4275.00; invalid=`0`; non_positive=`2`
- `maximum_price_rs_per_quintal`: count=16284, min=0.00, mean=2149.43, max=4950.00; invalid=`0`; non_positive=`18`
- `modal_price_rs_per_quintal`: count=16284, min=900.00, mean=2147.33, max=4300.00; invalid=`0`; non_positive=`0`

## Top Markets By Row Count

- `Bhikhi APMC`: `288`
- `Boha APMC`: `272`
- `Amargarh APMC`: `258`
- `Abohar APMC`: `253`
- `Sangat APMC`: `252`
- `Sahnewal APMC`: `245`
- `Jalalabad APMC`: `237`
- `Jalandhar City APMC`: `235`
- `Rayya APMC`: `233`
- `Jalandhar Cantt. APMC`: `233`

## Varieties By Row Count

- `Paddy`: `7453`
- `Other`: `6626`
- `Paddy fine`: `901`
- `Common`: `492`
- `1001`: `312`
- `Fine`: `274`
- `Paddy Coarse`: `170`
- `A. Ponni`: `28`
- `5001`: `10`
- `1121`: `9`
- `Sarvati`: `4`
- `Paddy Medium`: `4`
- `Basmati`: `1`
