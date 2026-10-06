from collections import defaultdict


def group_by_category(findings):
    grouped = defaultdict(list)

    for finding in findings:

        if finding["status"].lower().strip() == "registered":
            category = finding["category"]

            grouped[category].append({
                "site_name": finding["site_name"],
                "url": finding["url"],
                "extra": finding["extra"]
            })

    return dict(grouped)


def calculate_category_presence(findings):
    registered = [
        finding
        for finding in findings
        if finding["status"].lower().strip() == "registered"
    ]

    total_registered = len(registered)

    if total_registered == 0:
        return {}

    category_counts = defaultdict(int)

    for finding in registered:
        category_counts[finding["category"]] += 1

    result = {}

    for category, count in category_counts.items():
        percentage = (count / total_registered) * 100

        result[category] = {
            "count": count,
            "percentage": round(percentage, 2)
        }

    return dict(result)


def identify_footprint_areas(findings):
    category_presence = calculate_category_presence(findings)

    areas = []

    for category, data in category_presence.items():

        if data["count"] >= 3:
            strength = "strong"

        elif data["count"] >= 2:
            strength = "moderate"

        else:
            strength = "limited"

        areas.append({
            "category": category,
            "count": data["count"],
            "percentage": data["percentage"],
            "strength": strength
        })

    areas.sort(
        key=lambda item: item["count"],
        reverse=True
    )

    return areas


def build_correlation(findings):
    return {
        "by_category": group_by_category(findings),
        "category_presence": calculate_category_presence(findings),
        "footprint_areas": identify_footprint_areas(findings)
    }