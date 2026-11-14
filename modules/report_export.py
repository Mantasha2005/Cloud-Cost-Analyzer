import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "reports")


def export_reports(records, total_cost):
    os.makedirs(REPORT_DIR, exist_ok=True)

    csv_file = os.path.join(REPORT_DIR, "cloud_cost_report.csv")
    txt_file = os.path.join(REPORT_DIR, "cloud_cost_report.txt")

    try:
        if records:
            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)

        with open(txt_file, "w", encoding="utf-8") as file:
            file.write("CLOUD COST ANALYZER REPORT\n")
            file.write("============================\n\n")
            file.write(f"Total Resources: {len(records)}\n")
            file.write(f"Total Cloud Cost: Rs. {total_cost:,.2f}\n\n")
            file.write("RESOURCE DETAILS\n")
            file.write("----------------------------\n")

            for row in records:
                file.write(
                    f"Resource: {row.get('resource_id', 'N/A')} | "
                    f"Service: {row.get('service', 'N/A')} | "
                    f"Region: {row.get('region', 'N/A')} | "
                    f"Cost: Rs. {row.get('cost', 'N/A')} | "
                    f"Utilization: {row.get('utilization', 'N/A')}%\n"
                )
    except PermissionError:
        print("\nError: could not write the reports. Close the files if they are open in another program.")
        return

    print("\n===== REPORT EXPORT =====")
    if records:
        print("CSV Report Saved:", csv_file)
    print("Text Report Saved:", txt_file)