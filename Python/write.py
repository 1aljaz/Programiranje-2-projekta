from settings import *
import sys, io
import datetime
import csv
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def save_hourly_snapshot(raw):
    """Append one row per country to hourly_traffic.csv."""
    now = datetime.now()
    ts_str = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    hour = now.hour

    file_exists = os.path.isfile(HOURLY_CSV)
    with open(HOURLY_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "date", "hour", "country_code", "country_name",
                "total_traffic",
            ])
        for geo, trends in raw.items():
            total = sum(t["traffic"] for t in trends)
            writer.writerow([
                ts_str, date_str, hour, geo, COUNTRIES[geo], total,
            ])


def save_searches_csv(top10, timestamp):
    file_exists = os.path.isfile(SEARCHES_CSV)
    date_str = timestamp.strftime("%Y-%m-%d")
    ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    with open(SEARCHES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "date", "global_rank", "search_term",
                "total_traffic", "country_code", "country_name",
                "country_traffic",
            ])
        for rank, (term, info) in enumerate(top10, 1):
            for geo, traffic in sorted(info["countries"].items(),
                                       key=lambda x: x[1], reverse=True):
                writer.writerow([
                    ts_str, date_str, rank, term,
                    info["total"], geo, COUNTRIES[geo], traffic,
                ])


