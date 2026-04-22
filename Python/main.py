"""
Google Trends Tracker
=====================
Tracks global trending searches, country traffic by time of day,
detects traffic spikes, and provides matplotlib graphs.

Usage:
    python trial.py                  — fetch + save snapshot, show tables
    python trial.py --graph-top      — graph top 5 most consistent countries
    python trial.py --spike          — detect spikes, graph example if none found
    python trial.py --spike US       — graph traffic history for a specific country
"""

import sys
import io
import os
import csv
import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from statistics import median

import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


from settings import *

# Function imports
from display_history import *



sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_traffic(s):
    try:
        return int(s.replace(",", "").replace("+", "").strip())
    except ValueError:
        return 0


def get_trending(geo):
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    trends = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "")
        traffic = item.findtext("ht:approx_traffic", "N/A", NS)
        trends.append({"title": title.lower().strip(),
                        "traffic": parse_traffic(traffic)})
    return trends


def fetch_all():
    raw = {}
    print("Fetching trends from 20 countries", end="", flush=True)
    for geo in COUNTRIES:
        try:
            raw[geo] = get_trending(geo)
            print(".", end="", flush=True)
        except Exception:
            raw[geo] = []
            print("x", end="", flush=True)
    print(" done!\n")
    return raw


# ── Task 1: Global top 10 ───────────────────────────────────────────────────



# ── Task 2: Save hourly traffic by country ──────────────────────────────────

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


def get_last_top10_terms():
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


# ── Task 2 display: traffic by country ───────────────────────────────────────

def display_traffic_table(raw):
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


# ── Task 3: Graph top 5 most consistent countries ───────────────────────────

def cmd_graph_top(min_hours=8):
    """
    Graph countries that appear in the top 5 traffic for at least
    `min_hours` distinct hours in the data.
    """
    if not os.path.isfile(HOURLY_CSV):
        print("  No hourly data yet. Run the script a few times first.\n")
        return

    rows = []
    with open(HOURLY_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("  No hourly data yet.\n")
        return

    # For each timestamp, find top 5 countries
    by_ts = defaultdict(dict)
    for r in rows:
        by_ts[r["timestamp"]][r["country_code"]] = int(r["total_traffic"])

    # Count how many distinct hours each country was in top 5
    hours_in_top5 = defaultdict(set)
    for ts, countries in by_ts.items():
        top5 = sorted(countries, key=countries.get, reverse=True)[:5]
        hour = ts[11:13]  # extract HH
        for geo in top5:
            hours_in_top5[geo].add(hour)

    # Filter to countries with >= min_hours
    qualified = {geo for geo, hrs in hours_in_top5.items()
                 if len(hrs) >= min_hours}

    if not qualified:
        # Relax threshold to show something
        max_hours = max(len(h) for h in hours_in_top5.values())
        print(f"  No country hit {min_hours}h threshold yet "
              f"(max seen: {max_hours}h).")
        print(f"  Showing all countries that appeared in top 5.\n")
        qualified = {geo for geo, hrs in hours_in_top5.items() if len(hrs) >= 1}

    # Build time series for qualified countries
    series = defaultdict(lambda: {"times": [], "values": []})
    for r in rows:
        geo = r["country_code"]
        if geo in qualified:
            t = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S")
            series[geo]["times"].append(t)
            series[geo]["values"].append(int(r["total_traffic"]))

    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))
    for geo in sorted(qualified):
        ax.plot(series[geo]["times"], series[geo]["values"],
                marker="o", markersize=3, label=COUNTRIES.get(geo, geo))

    ax.set_title("Top Countries — Trending Traffic Over Time", fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Approximate Trending Traffic")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


# ── Task 4: Spike detection ─────────────────────────────────────────────────

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


def cmd_spike(country_code=None):
    """Detect spikes or graph a specific country's traffic."""
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


def plot_country_traffic(rows, geo, demo=False):
    """Plot traffic over time for a single country with median line."""
    times = []
    values = []
    for r in rows:
        if r["country_code"] == geo:
            t = datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S")
            times.append(t)
            values.append(int(r["total_traffic"]))

    if not values:
        print(f"  No data to plot for {geo}.\n")
        return

    med = median(values)
    spike_line = med * SPIKE_THRESHOLD

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(times, values, marker="o", markersize=4, color="steelblue",
            linewidth=2, label="Traffic")
    ax.axhline(y=med, color="green", linestyle="--", alpha=0.7,
               label=f"Median ({med:,.0f})")
    ax.axhline(y=spike_line, color="red", linestyle="--", alpha=0.7,
               label=f"Spike threshold ({spike_line:,.0f})")

    # Highlight spike points
    for t, v in zip(times, values):
        if v >= spike_line:
            ax.plot(t, v, "ro", markersize=10, zorder=5)

    title = f"{COUNTRIES.get(geo, geo)} — Trending Traffic Over Time"
    if demo:
        title += " (DEMO DATA)"
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Time")
    ax.set_ylabel("Approximate Trending Traffic")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


# ── Display history ──────────────────────────────────────────────────────────

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


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Google Trends Tracker")
    parser.add_argument("--graph-top", action="store_true",
                        help="Graph top 5 most consistent countries")
    parser.add_argument("--spike", nargs="?", const="auto", default=None,
                        help="Detect spikes, or pass country code (e.g. US)")
    parser.add_argument("--min-hours", type=int, default=8,
                        help="Min hours in top 5 for --graph-top (default: 8)")
    args = parser.parse_args()

    # Handle graph/spike commands (no fetching needed)
    if args.graph_top:
        cmd_graph_top(args.min_hours)
        return
    if args.spike is not None:
        code = None if args.spike == "auto" else args.spike
        cmd_spike(code)
        return

    # Default: fetch, save, display
    raw = fetch_all()

    # Task 1: Global top 10
    top10 = build_global_top10(raw)

    # Task 2: Save hourly snapshot (always — tracks time of day)
    save_hourly_snapshot(raw)
    print(f"  Saved hourly snapshot to {HOURLY_CSV}")

    # Save search snapshot only if top 10 changed
    current_terms = {term for term, _ in top10}
    previous_terms = get_last_top10_terms()
    if current_terms != previous_terms:
        save_searches_csv(top10, datetime.now())
        print(f"  Top 10 changed — saved to {SEARCHES_CSV}\n")
    else:
        print(f"  Top 10 unchanged — skipped search CSV save.\n")

    # Display
    display_top10(top10)
    display_traffic_table(raw)
    display_history()

    print("  Commands:")
    print("    python main.py --graph-top       Graph top consistent countries")
    print("    python main.py --spike           Detect traffic spikes")
    print("    python main.py --spike US        Graph specific country traffic")
    print()


if __name__ == "__main__":
    main()
