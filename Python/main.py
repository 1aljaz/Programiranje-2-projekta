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
    """Glavna datoteka za Google Trends Tracker.
    Obravnava argumente ukazne vrstice, izvaja naloge in prikazuje rezultate."""
    parser = argparse.ArgumentParser(description="Google Trends Tracker")
    parser.add_argument("--graph-top", action="store_true",
                        help="Graph top 5 most consistent countries")
    parser.add_argument("--spike", nargs="?", const="auto", default=None,
                        help="Detect spikes, or pass country code (e.g. US)")
    parser.add_argument("--min-hours", type=int, default=8,
                        help="Min hours in top 5 for --graph-top (default: 8)")
    args = parser.parse_args()

    if args.graph_top:
        cmd_graph_top(args.min_hours)
        return
    if args.spike is not None:
        code = None if args.spike == "auto" else args.spike
        cmd_spike(code)
        return

    raw = fetch_all()

    top10 = build_global_top10(raw)

    save_hourly_snapshot(raw)
    print(f"  Saved hourly snapshot to {HOURLY_CSV}")

    # Shrani samo če se je top 10 držav spremenilo
    current_terms = {term for term, _ in top10}
    previous_terms = get_last_top10_terms()
    if current_terms != previous_terms:
        save_searches_csv(top10, datetime.now())
        print(f"  Top 10 changed — saved to {SEARCHES_CSV}\n")
    else:
        print(f"  Top 10 unchanged — skipped search CSV save.\n")

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
