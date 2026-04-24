from collections import defaultdict
from datetime import datetime, timedelta
import csv
from statistics import median
from settings import *

def build_global_top10(raw):
    """
        Prejme slovar raw in združi trende iskanja po vseh državah, za lažjo pripravo top 10.
        Vrne seznam top 10 iskanj, sortiranih po skupnem globalnem prometu.
    """
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
    """
        Zgenerira umetne podatke za špice v prometu, ko špice v podatkih ne obstajajo.
    """
    import random
    random.seed(42)

    print("  No real spikes detected — generating demo data to show the feature.\n")

    demo_rows = []
    base_time = datetime(2026, 4, 1, 0, 0, 0)
    demo_geo = "US"

    for h in range(36):
        if h < 24:
            traffic = random.randint(8000, 15000)
        elif h < 30:
            traffic = random.randint(40000, 60000)  # spike
        else:
            traffic = random.randint(8000, 15000)

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
    """
        Prebere in vrne podatke iz hourly_traffic.csv.
    """
    if not os.path.isfile(HOURLY_CSV):
        return []
    with open(HOURLY_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def detect_spikes(rows):
    """
        Za vsako državo, izračuna medijano prometa.
        Vrne seznam držav katir nazadnji promet je večji kot SPIKE_TRESHOLD * mediana.
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