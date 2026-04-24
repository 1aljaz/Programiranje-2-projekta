# Tukaj imava konstante in poti do vseh datotek, ki jih uporabljava.

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCHES_CSV = os.path.join(SCRIPT_DIR, "top_searches.csv")
HOURLY_CSV = os.path.join(SCRIPT_DIR, "hourly_traffic.csv")

COUNTRIES = {
    "US": "United States",  "GB": "United Kingdom", "IN": "India",
    "BR": "Brazil",         "DE": "Germany",        "FR": "France",
    "JP": "Japan",          "CA": "Canada",         "AU": "Australia",
    "MX": "Mexico",         "RU": "Russia",         "KR": "South Korea",
    "IT": "Italy",          "ES": "Spain",          "ID": "Indonesia",
    "TR": "Turkey",         "PL": "Poland",         "AR": "Argentina",
    "NL": "Netherlands",    "SE": "Sweden",
}

NS = {"ht": "https://trends.google.com/trending/rss"}
SPIKE_THRESHOLD = 2.0