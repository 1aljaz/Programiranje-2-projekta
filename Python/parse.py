from collections import defaultdict
import datetime
import csv
from statistics import median
from settings import *

def build_global_top10(raw):
    merged = defaultdict(lambda: {"total": 0, "countries": {}})
    for geo, trends in raw.items():
        for t in trends:
            term = t["title"]
            merged[term]["total"] += t["traffic"]
            merged[term]["countries"][geo] = (
                merged[term]["countries"].get(geo, 0) + t["traffic"]
            )
    ranked = sorted(merged.items(), key=lambda x: x[1]["total"], reverse=True)
    return ranked[:10]

def generate_demo_spike():
    """Generate fake spike data for demo purposes when no real spikes exist."""
    import random
    random.seed(42)

    print("  No real spikes detected — generating demo data to show the feature.\n")

    demo_rows = []
    base_time = datetime(2026, 4, 1, 0, 0, 0)
    demo_geo = "US"

    # 24 hours of normal traffic, then a spike at hours 25-30
    for h in range(36):
        if h < 24:
            traffic = random.randint(8000, 15000)
        elif h < 30:
            traffic = random.randint(40000, 60000)  # spike!
        else:
            traffic = random.randint(8000, 15000)

        from datetime import timedelta
        t = base_time + timedelta(hours=h)
        demo_rows.append({
            "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
            "date": t.strftime("%Y-%m-%d"),
            "hour": str(t.hour),
            "country_code": demo_geo,
            "country_name": "United States",
            "total_traffic": str(traffic),
        })

    return demo_rows, demo_geo

def load_hourly_data():
    if not os.path.isfile(HOURLY_CSV):
        return []
    with open(HOURLY_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def detect_spikes(rows):
    """
    For each country, compute median traffic from history.
    Flag countries whose latest traffic >= SPIKE_THRESHOLD * median.
    Returns list of (geo, current, median_val, ratio).
    """
    # Group all traffic values by country
    by_geo = defaultdict(list)
    latest_ts = ""
    for r in rows:
        by_geo[r["country_code"]].append(int(r["total_traffic"]))
        if r["timestamp"] > latest_ts:
            latest_ts = r["timestamp"]

    # Get latest values
    latest = {}
    for r in rows:
        if r["timestamp"] == latest_ts:
            latest[r["country_code"]] = int(r["total_traffic"])

    spikes = []
    for geo, values in by_geo.items():
        if len(values) < 2:
            continue
        med = median(values)
        current = latest.get(geo, 0)
        if med > 0:
            ratio = current / med
            if ratio >= SPIKE_THRESHOLD:
                spikes.append((geo, current, med, ratio))

    spikes.sort(key=lambda x: x[3], reverse=True)
    return spikes