from settings import *
import requests
import xml.etree.ElementTree as ET

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