def normalize_results(raw_results):
    findings = []

    for result in raw_results:

        finding = {
            "site_name": result.get("site_name", "Unknown"),
            "category": result.get("category", "Unknown"),
            "status": result.get("status", "Unknown"),
            "url": result.get("url", ""),
            "reason": result.get("reason", ""),
            "extra": result.get("extra", {}),
            "media": result.get("media", {}),
            "email": result.get("email", "")
        }

        findings.append(finding)

    return findings


def summarize_results(findings):
    summary = {
        "total": len(findings),
        "registered": 0,
        "not_registered": 0,
        "skipped": 0,
        "errors": 0,
        "other": 0
    }

    for finding in findings:

        status = finding["status"].lower().strip()

        if status == "registered":
            summary["registered"] += 1

        elif status == "not registered":
            summary["not_registered"] += 1

        elif status == "skipped":
            summary["skipped"] += 1

        elif status == "error":
            summary["errors"] += 1

        else:
            summary["other"] += 1

    return summary