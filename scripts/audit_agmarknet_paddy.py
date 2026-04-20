#!/usr/bin/env python3
"""Audit raw AGMARKNET Paddy(Common) CSV data before cleaning."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean


PRICE_COLUMNS = [
    "minimum_price_rs_per_quintal",
    "maximum_price_rs_per_quintal",
    "modal_price_rs_per_quintal",
]

NUMERIC_COLUMNS = [
    "arrivals_metric_tonnes",
    "total_arrivals_metric_tonnes",
    *PRICE_COLUMNS,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit raw AGMARKNET CSV data.")
    parser.add_argument(
        "--input",
        default="agmarknet_paddy_common_punjab.csv",
        help="Raw AGMARKNET CSV file.",
    )
    parser.add_argument(
        "--report",
        default="reports/agmarknet_paddy_raw_audit.md",
        help="Markdown report output path.",
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


def metric_summary(values: list[float]) -> str:
    if not values:
        return "count=0"
    return (
        f"count={len(values)}, min={min(values):.2f}, "
        f"mean={mean(values):.2f}, max={max(values):.2f}"
    )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    missing = {
        column: sum(1 for row in rows if not row.get(column, "").strip())
        for column in fieldnames
    }

    numeric_values: dict[str, list[float]] = {column: [] for column in NUMERIC_COLUMNS}
    numeric_invalid: Counter[str] = Counter()
    numeric_non_positive: Counter[str] = Counter()

    invalid_dates = 0
    parsed_dates = []
    bad_price_order = 0
    duplicate_full_rows = 0
    duplicate_market_date_variety = 0

    full_row_counter = Counter(tuple(row.get(column, "") for column in fieldnames) for row in rows)
    duplicate_full_rows = sum(count - 1 for count in full_row_counter.values() if count > 1)

    key_counter = Counter(
        (row.get("market_name", ""), row.get("arrival_date", ""), row.get("variety", ""))
        for row in rows
    )
    duplicate_market_date_variety = sum(
        count - 1 for count in key_counter.values() if count > 1
    )

    for row in rows:
        parsed = parse_date(row.get("arrival_date", ""))
        if parsed is None:
            invalid_dates += 1
        else:
            parsed_dates.append(parsed)

        numeric_row: dict[str, float | None] = {}
        for column in NUMERIC_COLUMNS:
            value = parse_float(row.get(column, ""))
            numeric_row[column] = value
            if value is None:
                numeric_invalid[column] += 1
            else:
                numeric_values[column].append(value)
                if value <= 0:
                    numeric_non_positive[column] += 1

        min_price = numeric_row["minimum_price_rs_per_quintal"]
        max_price = numeric_row["maximum_price_rs_per_quintal"]
        modal_price = numeric_row["modal_price_rs_per_quintal"]
        if (
            min_price is not None
            and max_price is not None
            and modal_price is not None
            and not (min_price <= modal_price <= max_price)
        ):
            bad_price_order += 1

    markets = Counter(row.get("market_name", "") for row in rows)
    varieties = Counter(row.get("variety", "") for row in rows)
    states = Counter(row.get("state_name", "") for row in rows)
    commodities = Counter(row.get("commodity_name", "") for row in rows)

    report_lines = [
        "# AGMARKNET Paddy Raw Data Audit",
        "",
        "## File",
        "",
        f"- Input file: `{input_path}`",
        f"- Total rows: `{len(rows)}`",
        f"- Total columns: `{len(fieldnames)}`",
        "",
        "## Identity Checks",
        "",
        f"- States found: `{dict(states)}`",
        f"- Commodities found: `{dict(commodities)}`",
        f"- Unique markets: `{len(markets)}`",
        f"- Unique varieties: `{len(varieties)}`",
        "",
        "## Date Checks",
        "",
        f"- Invalid dates: `{invalid_dates}`",
        f"- Earliest date: `{min(parsed_dates).date() if parsed_dates else 'NA'}`",
        f"- Latest date: `{max(parsed_dates).date() if parsed_dates else 'NA'}`",
        "",
        "## Duplicate Checks",
        "",
        f"- Exact duplicate rows: `{duplicate_full_rows}`",
        f"- Duplicate market-date-variety keys: `{duplicate_market_date_variety}`",
        "",
        "## Price Consistency Checks",
        "",
        f"- Rows where min <= modal <= max is false: `{bad_price_order}`",
        "",
        "## Missing Values",
        "",
    ]

    for column, count in missing.items():
        report_lines.append(f"- `{column}`: `{count}`")

    report_lines.extend(["", "## Numeric Column Summary", ""])
    for column in NUMERIC_COLUMNS:
        report_lines.append(
            f"- `{column}`: {metric_summary(numeric_values[column])}; "
            f"invalid=`{numeric_invalid[column]}`; "
            f"non_positive=`{numeric_non_positive[column]}`"
        )

    report_lines.extend(["", "## Top Markets By Row Count", ""])
    for market, count in markets.most_common(10):
        report_lines.append(f"- `{market}`: `{count}`")

    report_lines.extend(["", "## Varieties By Row Count", ""])
    for variety, count in varieties.most_common():
        report_lines.append(f"- `{variety}`: `{count}`")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(fieldnames)}")
    print(f"Date range: {min(parsed_dates).date()} to {max(parsed_dates).date()}")
    print(f"Markets: {len(markets)}")
    print(f"Varieties: {len(varieties)}")
    print(f"Exact duplicate rows: {duplicate_full_rows}")
    print(f"Duplicate market-date-variety keys: {duplicate_market_date_variety}")
    print(f"Bad price order rows: {bad_price_order}")
    print(f"Report written: {report_path}")


if __name__ == "__main__":
    main()
