# AGMARKNET Paddy Cleaning Rules

## Goal

Prepare the raw AGMARKNET Paddy(Common) Punjab data for forecasting without
changing the original raw CSV.

## Raw Input

- File: `agmarknet_paddy_common_punjab.csv`
- Target column for forecasting: `modal_price_rs_per_quintal`
- Unit: rupees per quintal

## Cleaning Rules

1. Keep the raw CSV unchanged.
2. Trim whitespace from text columns.
3. Parse `arrival_date` as an ISO date.
4. Convert arrival and price columns to numeric values.
5. Remove exact duplicate rows.
6. Repair obvious missing price bounds:
   - If `minimum_price_rs_per_quintal` is `0` but modal price is valid, set
     minimum price equal to modal price.
   - If `maximum_price_rs_per_quintal` is `0` but modal price is valid, set
     maximum price equal to modal price.
7. Drop only rows that still fail core validity checks after repair:
   - invalid date
   - non-positive arrivals
   - non-positive modal price
   - invalid price order after repair
8. If more than one row remains for the same market, date, and variety:
   - sum arrivals
   - keep the lowest minimum price
   - keep the highest maximum price
   - compute modal price as an arrival-weighted average
9. Create two cleaned outputs:
   - row-level cleaned records
   - daily model-ready price series aggregated across Punjab markets

## Daily Aggregation Rule

For each date, compute the main forecasting target as:

`target_modal_price_rs_per_quintal = arrival-weighted average modal price`

This gives larger mandi arrivals more influence than very small arrivals.
