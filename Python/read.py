from settings import *
import csv, os

def display_history():
    """
        Funkcija izpiše zgodovino podatkov.
        In sicer: pot do obeh csv datotek, kolikokrat smo podatke zajeli, koliko je podatkov v hourly_traffic.csv in
        koliko dni smo podatke zajemali.
    """
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

def get_last_top10_terms():
    """
        Vrne množico zadnjih 10 najbolj popularnih iskanj.
    """
    if not os.path.isfile(SEARCHES_CSV):
        return set()
    last_ts = None
    terms = set()
    with open(SEARCHES_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = row["timestamp"]
            if last_ts is None or ts > last_ts:
                last_ts = ts
                terms = set()
            if ts == last_ts:
                terms.add(row["search_term"])
    return terms