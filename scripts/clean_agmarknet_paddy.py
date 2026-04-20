#!/usr/bin/env python3
"""Clean AGMARKNET Paddy(Common) CSV data for forecasting experiments."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean


NUMERIC_COLUMNS = [
    "arrivals_metric_tonnes",
    "minimum_price_rs_per_quintal",
    "maximum_price_rs_per_quintal",
    "modal_price_rs_per_quintal",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean AGMARKNET Paddy data.")
    parser.add_argument("--input", default="agmarknet_paddy_common_punjab.csv")
    parser.add_argument(
        "--cleaned-records",
        default="agmarknet_paddy_common_punjab_cleaned_records.csv",
    )
    parser.add_argument(
        "--daily-series",
        default="agmarknet_paddy_common_punjab_daily_prices.csv",
    )
    parser.add_argument(
        "--summary",
        default="reports/agmarknet_paddy_cleaning_summary.md",
    )
    return parser.parse_args()


def parse_float(value: str) -> float | None:
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def rounded(value: float) -> float:
    return round(value, 4)


def weighted_average(rows: list[dict], value_key: str, weight_key: str) -> float:
    total_weight = sum(row[weight_key] for row in rows)
    if total_weight <= 0:
        return mean(row[value_key] for row in rows)
    return sum(row[value_key] * row[weight_key] for row in rows) / total_weight


def read_raw_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        rows = [
            {column: row.get(column, "").strip() for column in fieldnames}
            for row in reader
        ]
    return fieldnames, rows


def remove_exact_duplicates(
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> tuple[list[dict[str, str]], int]:
    seen = set()
    deduped = []
    duplicate_count = 0

    for row in rows:
        key = tuple(row.get(column, "") for column in fieldnames)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        deduped.append(row)

    return deduped, duplicate_count


def normalize_records(rows: list[dict[str, str]]) -> tuple[list[dict], Counter, int]:
    cleaned = []
    dropped: Counter[str] = Counter()
    repaired_price_rows = 0

    for row in rows:
        parsed_date = parse_date(row.get("arrival_date", ""))
        if parsed_date is None:
            dropped["invalid_date"] += 1
            continue

        numeric = {column: parse_float(row.get(column, "")) for column in NUMERIC_COLUMNS}
        if any(value is None for value in numeric.values()):
            dropped["invalid_numeric_value"] += 1
            continue

        arrivals = numeric["arrivals_metric_tonnes"]
        min_price = numeric["minimum_price_rs_per_quintal"]
        max_price = numeric["maximum_price_rs_per_quintal"]
        modal_price = numeric["modal_price_rs_per_quintal"]

        repaired_this_row = False
        if modal_price and modal_price > 0:
            if min_price is None or min_price <= 0:
                min_price = modal_price
                repaired_this_row = True
            if max_price is None or max_price <= 0:
                max_price = modal_price
                repaired_this_row = True

        if repaired_this_row:
            repaired_price_rows += 1

        if arrivals is None or arrivals <= 0:
            dropped["non_positive_arrivals"] += 1
            continue
        if modal_price is None or modal_price <= 0:
            dropped["non_positive_modal_price"] += 1
            continue
        if min_price is None or max_price is None or min_price <= 0 or max_price <= 0:
            dropped["non_positive_price_bound"] += 1
            continue
        if not (min_price <= modal_price <= max_price):
            dropped["invalid_price_order"] += 1
            continue

        cleaned.append(
            {
                "state_id": int(float(row["state_id"])),
                "state_name": row["state_name"],
                "commodity_id": int(float(row["commodity_id"])),
                "commodity_name": row["commodity_name"],
                "market_name": row["market_name"],
                "arrival_date": parsed_date.date().isoformat(),
                "year": parsed_date.year,
                "month": parsed_date.month,
                "variety": row["variety"],
                "arrivals_metric_tonnes": arrivals,
                "minimum_price_rs_per_quintal": min_price,
                "maximum_price_rs_per_quintal": max_price,
                "modal_price_rs_per_quintal": modal_price,
                "source_url": row["source_url"],
            }
        )

    return cleaned, dropped, repaired_price_rows


def aggregate_market_date_variety(records: list[dict]) -> tuple[list[dict], int]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for record in records:
        key = (
            record["state_id"],
            record["state_name"],
            record["commodity_id"],
            record["commodity_name"],
            record["market_name"],
            record["arrival_date"],
            record["variety"],
        )
        grouped[key].append(record)

    aggregated = []
    duplicate_groups = 0

    for key, group_rows in grouped.items():
        if len(group_rows) > 1:
            duplicate_groups += 1

        sample = group_rows[0]
        total_arrivals = sum(row["arrivals_metric_tonnes"] for row in group_rows)
        source_urls = sorted({row["source_url"] for row in group_rows})

        aggregated.append(
            {
                "state_id": sample["state_id"],
                "state_name": sample["state_name"],
                "commodity_id": sample["commodity_id"],
                "commodity_name": sample["commodity_name"],
                "market_name": sample["market_name"],
                "arrival_date": sample["arrival_date"],
                "year": sample["year"],
                "month": sample["month"],
                "variety": sample["variety"],
                "arrivals_metric_tonnes": rounded(total_arrivals),
                "minimum_price_rs_per_quintal": rounded(
                    min(row["minimum_price_rs_per_quintal"] for row in group_rows)
                ),
                "maximum_price_rs_per_quintal": rounded(
                    max(row["maximum_price_rs_per_quintal"] for row in group_rows)
                ),
                "modal_price_rs_per_quintal": rounded(
                    weighted_average(
                        group_rows,
                        "modal_price_rs_per_quintal",
                        "arrivals_metric_tonnes",
                    )
                ),
                "source_rows": len(group_rows),
                "source_urls": ";".join(source_urls),
            }
        )

    aggregated.sort(
        key=lambda row: (
            row["arrival_date"],
            row["market_name"],
            row["variety"],
        )
    )
    return aggregated, duplicate_groups


def aggregate_daily_series(records: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[record["arrival_date"]].append(record)

    daily_rows = []
    for date, group_rows in grouped.items():
        parsed_date = parse_date(date)
        if parsed_date is None:
            continue

        total_arrivals = sum(row["arrivals_metric_tonnes"] for row in group_rows)
        weighted_modal = weighted_average(
            group_rows,
            "modal_price_rs_per_quintal",
            "arrivals_metric_tonnes",
        )
        simple_modal = mean(row["modal_price_rs_per_quintal"] for row in group_rows)

        daily_rows.append(
            {
                "arrival_date": date,
                "year": parsed_date.year,
                "month": parsed_date.month,
                "record_count": len(group_rows),
                "market_count": len({row["market_name"] for row in group_rows}),
                "variety_count": len({row["variety"] for row in group_rows}),
                "total_arrivals_metric_tonnes": rounded(total_arrivals),
                "minimum_price_rs_per_quintal": rounded(
                    min(row["minimum_price_rs_per_quintal"] for row in group_rows)
                ),
                "maximum_price_rs_per_quintal": rounded(
                    max(row["maximum_price_rs_per_quintal"] for row in group_rows)
                ),
                "modal_price_simple_avg_rs_per_quintal": rounded(simple_modal),
                "modal_price_weighted_avg_rs_per_quintal": rounded(weighted_modal),
                "target_modal_price_rs_per_quintal": rounded(weighted_modal),
            }
        )

    daily_rows.sort(key=lambda row: row["arrival_date"])
    return daily_rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    path: Path,
    *,
    input_path: Path,
    raw_rows: int,
    exact_duplicates_removed: int,
    repaired_price_rows: int,
    dropped: Counter,
    normalized_rows: int,
    duplicate_groups_aggregated: int,
    cleaned_records: int,
    daily_rows: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# AGMARKNET Paddy Cleaning Summary",
        "",
        f"- Input file: `{input_path}`",
        f"- Raw rows: `{raw_rows}`",
        f"- Exact duplicate rows removed: `{exact_duplicates_removed}`",
        f"- Rows with repaired zero price bounds: `{repaired_price_rows}`",
        f"- Rows valid after parsing and repair: `{normalized_rows}`",
        f"- Duplicate market-date-variety groups aggregated: `{duplicate_groups_aggregated}`",
        f"- Cleaned record-level rows: `{cleaned_records}`",
        f"- Daily model-ready rows: `{daily_rows}`",
        "",
        "## Dropped Rows",
        "",
    ]

    if dropped:
        for reason, count in dropped.items():
            lines.append(f"- `{reason}`: `{count}`")
    else:
        lines.append("- No rows dropped after repair.")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `agmarknet_paddy_common_punjab_cleaned_records.csv`",
            "- `agmarknet_paddy_common_punjab_daily_prices.csv`",
            "",
            "## Forecasting Target",
            "",
            "`target_modal_price_rs_per_quintal` in the daily price file is the",
            "arrival-weighted average modal price for each date.",
        ]
    )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    cleaned_records_path = Path(args.cleaned_records)
    daily_series_path = Path(args.daily_series)
    summary_path = Path(args.summary)

    fieldnames, raw_rows = read_raw_rows(input_path)
    deduped_rows, exact_duplicates_removed = remove_exact_duplicates(
        raw_rows,
        fieldnames,
    )
    normalized_records, dropped, repaired_price_rows = normalize_records(deduped_rows)
    cleaned_records, duplicate_groups_aggregated = aggregate_market_date_variety(
        normalized_records
    )
    daily_rows = aggregate_daily_series(cleaned_records)

    cleaned_record_fields = [
        "state_id",
        "state_name",
        "commodity_id",
        "commodity_name",
        "market_name",
        "arrival_date",
        "year",
        "month",
        "variety",
        "arrivals_metric_tonnes",
        "minimum_price_rs_per_quintal",
        "maximum_price_rs_per_quintal",
        "modal_price_rs_per_quintal",
        "source_rows",
        "source_urls",
    ]
    daily_series_fields = [
        "arrival_date",
        "year",
        "month",
        "record_count",
        "market_count",
        "variety_count",
        "total_arrivals_metric_tonnes",
        "minimum_price_rs_per_quintal",
        "maximum_price_rs_per_quintal",
        "modal_price_simple_avg_rs_per_quintal",
        "modal_price_weighted_avg_rs_per_quintal",
        "target_modal_price_rs_per_quintal",
    ]

    write_csv(cleaned_records_path, cleaned_records, cleaned_record_fields)
    write_csv(daily_series_path, daily_rows, daily_series_fields)
    write_summary(
        summary_path,
        input_path=input_path,
        raw_rows=len(raw_rows),
        exact_duplicates_removed=exact_duplicates_removed,
        repaired_price_rows=repaired_price_rows,
        dropped=dropped,
        normalized_rows=len(normalized_records),
        duplicate_groups_aggregated=duplicate_groups_aggregated,
        cleaned_records=len(cleaned_records),
        daily_rows=len(daily_rows),
    )

    print(f"Raw rows: {len(raw_rows)}")
    print(f"Exact duplicate rows removed: {exact_duplicates_removed}")
    print(f"Rows with repaired zero price bounds: {repaired_price_rows}")
    print(f"Rows dropped after repair: {sum(dropped.values())}")
    print(f"Duplicate market-date-variety groups aggregated: {duplicate_groups_aggregated}")
    print(f"Cleaned record rows: {len(cleaned_records)}")
    print(f"Daily model-ready rows: {len(daily_rows)}")
    print(f"Cleaned records written: {cleaned_records_path}")
    print(f"Daily series written: {daily_series_path}")
    print(f"Summary written: {summary_path}")


if __name__ == "__main__":
    main()
