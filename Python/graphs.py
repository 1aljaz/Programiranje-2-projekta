from settings import *
from collections import defaultdict
import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statistics import median

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