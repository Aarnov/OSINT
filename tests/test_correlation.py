import json

from modules.parser import normalize_results
from modules.correlation import build_correlation


scan_file = "aarnovadhikari123@gmail.com_report.json"


with open(scan_file, "r", encoding="utf-8") as file:
    raw_results = json.load(file)


findings = normalize_results(raw_results)

correlation = build_correlation(findings)


print("CORRELATION ANALYSIS")
print("=" * 40)


print()
print("CATEGORY PRESENCE")
print("=" * 40)

for category, data in correlation["category_presence"].items():

    print(
        f"{category}: "
        f"{data['count']} accounts "
        f"({data['percentage']}%)"
    )


print()
print("FOOTPRINT AREAS")
print("=" * 40)

for area in correlation["footprint_areas"]:

    print(
        f"{area['category']} | "
        f"{area['count']} accounts | "
        f"{area['strength']}"
    )


print()
print("GROUPED ACCOUNTS")
print("=" * 40)

for category, accounts in correlation["by_category"].items():

    print()
    print(f"[{category}]")

    for account in accounts:
        print(
            f"  {account['site_name']} | "
            f"{account['url']}"
        )