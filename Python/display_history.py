import os, csv

from settings import *

def display_history():
    if not os.path.isfile(SEARCHES_CSV):
        return

    timestamps = set()
    with open(SEARCHES_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            timestamps.add(row["timestamp"])

    dates = sorted(set(ts[:10] for ts in timestamps))

    hourly_count = 0
    if os.path.isfile(HOURLY_CSV):
        with open(HOURLY_CSV, "r", encoding="utf-8") as f:
            hourly_count = sum(1 for _ in csv.DictReader(f))

    print("=" * 90)
    print("  ACCUMULATED DATA")
    print("=" * 90)
    print(f"  Searches CSV:     {SEARCHES_CSV}")
    print(f"  Hourly CSV:       {HOURLY_CSV}")
    print(f"  Search snapshots: {len(timestamps)}")
    print(f"  Hourly records:   {hourly_count:,}")
    print(f"  Date range:       {dates[0]}  ->  {dates[-1]}  ({len(dates)} day(s))")
    print()