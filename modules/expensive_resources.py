import heapq

def parse_cost(record):
    """Return cost as float, or None if missing/invalid."""
    try:
        return float(str(record["cost"]).replace(",", "").strip())
    except (KeyError, ValueError):
        return None


def analyze_expensive(records, n=5):
    valid = [(cost, r) for r in records if (cost := parse_cost(r)) is not None]

    top = heapq.nlargest(n, valid, key=lambda pair: pair[0])

    print(f"\n===== TOP {n} EXPENSIVE RESOURCES =====")
    for cost, r in top:
        print(f"{r.get('resource_id', 'N/A')} - {r.get('service', 'N/A')} - Rs.{cost:,.2f}")

    skipped = len(records) - len(valid)
    if skipped:
        print(f"\n(Skipped {skipped} record(s) with missing/invalid cost)")

    return [r for _, r in top]