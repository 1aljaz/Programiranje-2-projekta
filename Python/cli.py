from settings import *
from datetime import datetime
import csv
import os
from parse import *
from graphs import *

def display_history():
    """
    Prikaže pridobljene podatke o iskanjih in prometu, ter datumski razpon zajetih podatkov.
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

def display_top10(top10):
    """Prikaže top 10 globalnih trendov iskanja z razčlenitvijo po državah in deležem prometa."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 90)
    print(f"  TOP 10 GLOBAL TRENDING SEARCHES — {now}")
    print("=" * 90)
    for rank, (term, info) in enumerate(top10, 1):
        print(f"\n  #{rank}  {term}   (total traffic: {info['total']:,})")
        print(f"  {'Country':<20} {'Traffic':>10} {'Share':>8}")
        print(f"  {'-'*20} {'-'*10} {'-'*8}")
        for geo, traffic in sorted(info["countries"].items(),
                                   key=lambda x: x[1], reverse=True):
            pct = traffic / info["total"] * 100 if info["total"] else 0
            print(f"  {COUNTRIES[geo]:<20} {traffic:>10,} {pct:>7.1f}%")
    print()


def display_traffic_table(raw):
    """Prikaže tabelo prometa po državah, vključno s skupnim prometom"""
    rows = []
    for geo, trends in raw.items():
        total = sum(t["traffic"] for t in trends)
        top = trends[0]["title"] if trends else "N/A"
        rows.append((COUNTRIES[geo], geo, total, top))
    rows.sort(key=lambda r: r[2], reverse=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 90)
    print(f"  TRAFFIC BY COUNTRY — {now}")
    print("=" * 90)
    print(f"  {'Country':<20} {'Code':<6} {'Traffic':>12}   {'#1 Topic'}")
    print(f"  {'-'*20} {'-'*6} {'-'*12}   {'-'*40}")
    for name, geo, total, top in rows:
        print(f"  {name:<20} {geo:<6} {total:>12,}   {top}")
    print()

def cmd_spike(country_code=None):
    """Prikazuje promet po državah in samodejno zazna nenavadne skoke v prometu, ki bi lahko nakazovali na trend"""
    rows = load_hourly_data()
    use_demo = False

    if country_code:
        # Graph specific country
        geo = country_code.upper()
        geo_rows = [r for r in rows if r["country_code"] == geo]
        if not geo_rows:
            print(f"  No data for {geo}.\n")
            return
        plot_country_traffic(geo_rows, geo)
        return

    # Auto-detect spikes
    if len(rows) < 2:
        rows, demo_geo = generate_demo_spike()
        use_demo = True

    spikes = detect_spikes(rows)

    if not spikes and not use_demo:
        # No spikes in real data — show demo
        demo_rows, demo_geo = generate_demo_spike()
        spikes_demo = detect_spikes(demo_rows)
        print("=" * 90)
        print("  SPIKE DETECTION (DEMO — no real spikes found)")
        print("=" * 90)
        for geo, current, med, ratio in spikes_demo:
            print(f"  {COUNTRIES.get(geo, geo):<20} Current: {current:>10,}   "
                  f"Median: {med:>10,.0f}   Ratio: {ratio:.1f}x  *** SPIKE ***")
        print()
        plot_country_traffic(demo_rows, demo_geo, demo=True)
        return

    # Real spikes
    print("=" * 90)
    print("  SPIKE DETECTION")
    print(f"  Threshold: {SPIKE_THRESHOLD}x median traffic")
    print("=" * 90)

    if spikes:
        for geo, current, med, ratio in spikes:
            print(f"  *** {COUNTRIES.get(geo, geo):<20} Current: {current:>10,}   "
                  f"Median: {med:>10,.0f}   Ratio: {ratio:.1f}x  *** SPIKE ***")
        print()
        # Graph the biggest spike
        biggest_geo = spikes[0][0]
        geo_rows = [r for r in rows if r["country_code"] == biggest_geo]
        plot_country_traffic(geo_rows, biggest_geo)
    else:
        print("  No spikes detected. All countries within normal range.\n")
        if use_demo:
            plot_country_traffic(rows, demo_geo, demo=True)