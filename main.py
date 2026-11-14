import csv
import os

from modules.cost_analysis import analyze_cost, analyze_region
from modules.expensive_resources import analyze_expensive
from modules.idle_detection import detect_idle_resources
from modules.anomaly_detection import detect_cost_anomaly
from modules.optimization import generate_recommendations
from modules.report_export import export_reports

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_FILE = os.path.join(BASE_DIR, "data", "cloud_usage.csv")
DAILY_COSTS_FILE = os.path.join(BASE_DIR, "data", "daily_costs.csv")


def load_records(path):
    with open(path, "r", newline="") as file:
        return list(csv.DictReader(file))
    
def validate_records(records):
    valid_records = []
    invalid_count = 0

    required_columns = [
        "resource_id",
        "service",
        "region",
        "cost",
        "utilization"
    ]

    for row in records:
        try:
            # Check required fields
            for column in required_columns:
                if not row.get(column, "").strip():
                    raise ValueError("Missing field")

            # Check cost
            cost = float(row["cost"])

            if cost < 0:
                raise ValueError("Invalid cost")

            # Check utilization
            utilization = float(
                row["utilization"].replace("%", "").strip()
            )

            if utilization < 0 or utilization > 100:
                raise ValueError("Invalid utilization")

            valid_records.append(row)

        except (ValueError, AttributeError):
            invalid_count += 1

    print("\n===== CSV DATA VALIDATION =====")
    print("Valid Records:", len(valid_records))
    print("Invalid Records:", invalid_count)

    return valid_records


def calculate_total_cost(records):
    total, skipped = 0.0, 0
    for row in records:
        try:
            total += float(row["cost"])
        except (KeyError, ValueError):
            skipped += 1
    return total, skipped


def main():
    print("================================")
    print("      CLOUD COST ANALYZER")
    print("================================")

    try:
        records = load_records(USAGE_FILE)
    except FileNotFoundError:
        print(f"Error: could not find {USAGE_FILE}")
        return
    records = validate_records(records)

    total_cost, skipped = calculate_total_cost(records)

    print("\nTotal Resources:", len(records))
    print(f"Total Cloud Cost: Rs. {total_cost:,.2f}")
    if skipped:
        print(f"(Skipped {skipped} record(s) with missing/invalid cost)")

    analyze_cost(records)
    analyze_region(records)
    analyze_expensive(records)
    detect_idle_resources(records)

    try:
        detect_cost_anomaly(DAILY_COSTS_FILE)
    except FileNotFoundError:
        print(f"\nSkipping anomaly detection: {DAILY_COSTS_FILE} not found")

    generate_recommendations(records)

    export_reports(records, total_cost)

    print("\n================================")
    print("       ANALYSIS COMPLETED")
    print("================================")


if __name__ == "__main__":
    main()