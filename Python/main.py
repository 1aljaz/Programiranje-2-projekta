"""
Google Trends Tracker
=====================
Tracks global trending searches, country traffic by time of day,
detects traffic spikes, and provides matplotlib graphs.

Usage:
    python main.py                  — fetch + save snapshot, show tables
    python main.py --graph-top      — graph top 5 most consistent countries
    python main.py --spike          — detect spikes, graph example if none found
    python main.py --spike US       — graph traffic history for a specific country
"""

import argparse
from datetime import datetime

# Settings import constants and file paths
from settings import *

# Function imports
from graphs import *
from write import *
from fetch import *
from cli import *
from parse import *
from read import *

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
    print("    python Python/main.py --graph-top       Graph top consistent countries")
    print("    python Python/main.py --spike           Detect traffic spikes")
    print("    python Python/main.py --spike US        Graph specific country traffic")
    print()


if __name__ == "__main__":
    main()
