SUGGESTIONS = {
    "ec2": "Consider rightsizing the instance.",
    "database": "Review database capacity.",
    "storage": "Review unused storage.",
}
DEFAULT_SUGGESTION = "Review resource utilization."


def generate_recommendations(records, threshold=20):
    recommendations = []
    skipped = 0

    for row in records:
        try:
            utilization = float(str(row["utilization"]).replace("%", "").strip())
        except (KeyError, ValueError):
            skipped += 1
            continue

        if utilization <= threshold:
            service = str(row.get("service", "Unknown")).strip().lower()
            recommendations.append({
                "resource_id": row.get("resource_id", "N/A"),
                "utilization": utilization,
                "recommendation": SUGGESTIONS.get(service, DEFAULT_SUGGESTION),
            })

    print("\n===== OPTIMIZATION RECOMMENDATIONS =====")

    for item in recommendations:
        print("\nResource:", item["resource_id"])
        print("Utilization:", item["utilization"], "%")
        print("Suggestion:", item["recommendation"])

    print("\nTotal Recommendations:", len(recommendations))
    if skipped:
        print(f"Skipped {skipped} record(s) with missing/invalid utilization")

    return recommendations