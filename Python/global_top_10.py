from collections import defaultdict

def build_global_top10(raw):
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


def display_top10(top10):
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
