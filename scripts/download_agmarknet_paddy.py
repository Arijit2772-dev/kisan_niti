#!/usr/bin/env python3
"""Download AGMARKNET Paddy(Common) price data and flatten it to CSV."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode


BASE_URL = (
    "https://api.agmarknet.gov.in/v1/prices-and-arrivals/date-wise/"
    "specific-commodity"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download AGMARKNET Paddy(Common) market price data."
    )
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--state-id", type=int, default=28)
    parser.add_argument("--state-name", default="Punjab")
    parser.add_argument("--commodity-id", type=int, default=2)
    parser.add_argument("--commodity-name", default="Paddy(Common)")
    parser.add_argument(
        "--output",
        default="agmarknet_paddy_common_punjab.csv",
        help="CSV output path.",
    )
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument(
        "--months",
        default="1,2,3,4,5,6,7,8,9,10,11,12",
        help="Comma-separated month numbers to fetch.",
    )
    return parser.parse_args()


def build_url(year: int, month: int, state_id: int, commodity_id: int) -> str:
    query = urlencode(
        {
            "year": year,
            "month": month,
            "includeExcel": "false",
            "stateId": state_id,
            "commodityId": commodity_id,
        }
    )
    return f"{BASE_URL}?{query}"


def fetch_json(url: str, retries: int = 2) -> dict:
    curl_command = [
        "curl",
        "-fsSL",
        "--retry",
        str(retries),
        "--connect-timeout",
        "20",
        "--max-time",
        "90",
        "-H",
        "Accept: application/json",
        "-A",
        "Mozilla/5.0 AGMARKNET CSV downloader",
        url,
    ]
    completed = subprocess.run(
        curl_command,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def iso_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return value


def flatten_month(
    payload: dict,
    *,
    source_url: str,
    year: int,
    month: int,
    state_id: int,
    state_name: str,
    commodity_id: int,
    commodity_name: str,
) -> list[dict[str, str | int | float]]:
    rows: list[dict[str, str | int | float]] = []

    for market in payload.get("markets", []):
        market_name = market.get("marketName", "")
        for date_block in market.get("dates", []):
            raw_date = date_block.get("arrivalDate", "")
            total_arrivals = date_block.get("total_arrivals", "")
            for item in date_block.get("data", []):
                rows.append(
                    {
                        "state_id": state_id,
                        "state_name": state_name,
                        "commodity_id": commodity_id,
                        "commodity_name": commodity_name,
                        "year": year,
                        "month": month,
                        "market_name": market_name,
                        "arrival_date": iso_date(raw_date),
                        "arrival_date_raw": raw_date,
                        "variety": item.get("variety", ""),
                        "arrivals_metric_tonnes": item.get("arrivals", ""),
                        "total_arrivals_metric_tonnes": total_arrivals,
                        "minimum_price_rs_per_quintal": item.get("minimumPrice", ""),
                        "maximum_price_rs_per_quintal": item.get("maximumPrice", ""),
                        "modal_price_rs_per_quintal": item.get("modalPrice", ""),
                        "source_url": source_url,
                    }
                )

    return rows


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    months = [int(month.strip()) for month in args.months.split(",") if month.strip()]
    all_rows: list[dict[str, str | int | float]] = []
    successes = 0
    failures: list[str] = []

    for year in range(args.start_year, args.end_year + 1):
        for month in months:
            url = build_url(year, month, args.state_id, args.commodity_id)
            try:
                payload = fetch_json(url)
                month_rows = flatten_month(
                    payload,
                    source_url=url,
                    year=year,
                    month=month,
                    state_id=args.state_id,
                    state_name=args.state_name,
                    commodity_id=args.commodity_id,
                    commodity_name=args.commodity_name,
                )
                all_rows.extend(month_rows)
                successes += 1
                print(f"{year}-{month:02d}: {len(month_rows)} rows", flush=True)
            except (RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
                failures.append(str(exc))
                print(f"{year}-{month:02d}: failed: {exc}", flush=True)
            time.sleep(args.sleep)

    fieldnames = [
        "state_id",
        "state_name",
        "commodity_id",
        "commodity_name",
        "year",
        "month",
        "market_name",
        "arrival_date",
        "arrival_date_raw",
        "variety",
        "arrivals_metric_tonnes",
        "total_arrivals_metric_tonnes",
        "minimum_price_rs_per_quintal",
        "maximum_price_rs_per_quintal",
        "modal_price_rs_per_quintal",
        "source_url",
    ]

    all_rows.sort(
        key=lambda row: (
            str(row["arrival_date"]),
            str(row["market_name"]),
            str(row["variety"]),
        )
    )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print()
    print(f"CSV written: {output_path}")
    print(f"Rows written: {len(all_rows)}")
    print(f"Months fetched successfully: {successes}")
    if failures:
        print(f"Failed months: {len(failures)}")


if __name__ == "__main__":
    main()
