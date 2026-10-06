import json

from modules.parser import normalize_results, summarize_results


scan_file = "aarnovadhikari123@gmail.com_report.json"


with open(scan_file, "r", encoding="utf-8") as file:
    raw_results = json.load(file)


findings = normalize_results(raw_results)
summary = summarize_results(findings)


print("SUMMARY")
print("=" * 40)

for key, value in summary.items():
    print(f"{key}: {value}")


print()
print("REGISTERED ACCOUNTS")
print("=" * 40)

for finding in findings:

    if finding["status"].lower().strip() == "registered":

        print(
            finding["site_name"],
            "|",
            finding["status"],
            "|",
            finding["url"]
        )


print()
print("FIRST 5 FINDINGS")
print("=" * 40)

for finding in findings[:5]:
    print(finding)

    