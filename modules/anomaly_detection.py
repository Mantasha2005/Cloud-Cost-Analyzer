import csv


def detect_cost_anomaly(path="data/daily_costs.csv", window=3, threshold=50):
    daily_costs = []

    with open(path, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                daily_costs.append({
                    "date": row["date"],
                    "cost": float(row["total_cost"]),
                })
            except (KeyError, ValueError):
                continue  # skip bad rows

    daily_costs.sort(key=lambda r: r["date"])  # works for YYYY-MM-DD dates

    anomalies = []

    print("\n===== COST ANOMALY DETECTION =====")

    for i in range(window, len(daily_costs)):
        previous = [daily_costs[j]["cost"] for j in range(i - window, i)]
        average = sum(previous) / window
        current = daily_costs[i]["cost"]

        if average == 0:
            if current > 0:
                increase = float("inf")  # any spend after zero baseline
            else:
                continue
        else:
            increase = (current - average) / average * 100

        if increase > threshold:
            anomalies.append({
                "date": daily_costs[i]["date"],
                "cost": current,
                "average": average,
                "increase": increase,
            })
            print("Anomaly Detected!")
            print("Date:", daily_costs[i]["date"])
            print("Current Cost: Rs.", current)
            print("Previous Average: Rs.", round(average, 2))
            print("Cost Increase:", "N/A (zero baseline)" if increase == float("inf") else f"{increase:.2f} %")

    if not anomalies:
        print("No anomalies found.")

    return anomalies