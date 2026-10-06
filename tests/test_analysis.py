import json

from modules.parser import normalize_results
from modules.analysis import build_analysis


scan_file = "data/scans/aarnovadhikari123_at_gmail.com.json"


with open(scan_file, "r", encoding="utf-8") as file:
    raw_results = json.load(file)


findings = normalize_results(raw_results)

analysis = build_analysis(findings)


print("ANALYSIS")
print("=" * 40)

print("Total:", analysis["total"])
print("Registered:", analysis["registered"])
print("Not Registered:", analysis["not_registered"])
print("Errors:", analysis["errors"])
print("Skipped:", analysis["skipped"])


print()
print("REGISTERED BY CATEGORY")
print("=" * 40)

for category, count in analysis["category_statistics"].items():
    print(f"{category}: {count}")


print()
print("REGISTERED ACCOUNTS")
print("=" * 40)

for finding in analysis["registered_accounts"]:
    print(
        f"{finding['site_name']} | "
        f"{finding['category']} | "
        f"{finding['url']}"
    )


print()
print("INCONCLUSIVE RESULTS")
print("=" * 40)

for finding in analysis["inconclusive_accounts"]:

    print(
        f"{finding['site_name']} | "
        f"{finding['error_label']} | "
        f"Retryable: {finding['retryable']}"
    )


print()
print("ERROR STATISTICS")
print("=" * 40)

for error_type, data in analysis["error_statistics"].items():

    print(
        f"{data['label']} | "
        f"{data['count']} | "
        f"Retryable: {data['retryable']}"
    )    