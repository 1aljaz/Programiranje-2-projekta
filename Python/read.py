from settings import *
import csv, os

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

