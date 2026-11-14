def detect_idle_resources(records, threshold=20):
    idle_resources = []
    skipped = 0

    for row in records:
        try:
            utilization = float(str(row["utilization"]).replace("%", "").strip())
        except (KeyError, ValueError):
            skipped += 1
            continue

        if utilization <= threshold:
            idle_resources.append(row)

    print("\n===== IDLE RESOURCE DETECTION =====")

    for r in idle_resources:
        print(
            r.get("resource_id", "N/A"),
            "-",
            r.get("service", "N/A"),
            "- Utilization:",
            r["utilization"],
            "%"
        )

    print("\nTotal Idle Resources:", len(idle_resources))
    if skipped:
        print(f"Skipped {skipped} record(s) with missing/invalid utilization")

    return idle_resources