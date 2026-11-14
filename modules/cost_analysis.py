def analyze_cost(records):
    service_cost = {}

    for row in records:
        service = row["service"]
        cost = float(row["cost"])

        if service in service_cost:
            service_cost[service] += cost
        else:
            service_cost[service] = cost

    print("\n===== SERVICE-WISE COST ANALYSIS =====")

    for service, cost in service_cost.items():
        print(service, ":", "Rs.", round(cost, 2))

    return service_cost


def analyze_region(records):
    region_cost = {}

    for row in records:
        region = row["region"]
        cost = float(row["cost"])

        if region in region_cost:
            region_cost[region] += cost
        else:
            region_cost[region] = cost

    print("\n===== REGION-WISE COST ANALYSIS =====")

    for region, cost in region_cost.items():
        print(region, ":", "Rs.", round(cost, 2))

    return region_cost