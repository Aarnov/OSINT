from collections import Counter

from modules.error_handler import (
    classify_error,
    summarize_errors
)


def get_registered_accounts(findings):
    return [
        finding
        for finding in findings
        if finding["status"].lower().strip() == "registered"
    ]


def get_not_registered_accounts(findings):
    return [
        finding
        for finding in findings
        if finding["status"].lower().strip() == "not registered"
    ]


def get_error_accounts(findings):
    return [
        finding
        for finding in findings
        if finding["status"].lower().strip() == "error"
    ]


def get_skipped_accounts(findings):
    return [
        finding
        for finding in findings
        if finding["status"].lower().strip() == "skipped"
    ]


def get_category_statistics(findings):

    registered = get_registered_accounts(findings)

    categories = Counter(
        finding["category"]
        for finding in registered
    )

    return dict(categories)


def get_inconclusive_accounts(findings):

    errors = get_error_accounts(findings)

    results = []

    for finding in errors:

        error_info = classify_error(
            finding.get("reason", "")
        )

        results.append({
            "site_name": finding["site_name"],
            "category": finding["category"],
            "reason": finding.get("reason", ""),
            "error_type": error_info["type"],
            "error_label": error_info["label"],
            "retryable": error_info["retryable"]
        })

    return results


def build_analysis(findings):

    registered = get_registered_accounts(findings)
    not_registered = get_not_registered_accounts(findings)
    errors = get_error_accounts(findings)
    skipped = get_skipped_accounts(findings)

    return {
        "total": len(findings),
        "registered": len(registered),
        "not_registered": len(not_registered),
        "errors": len(errors),
        "skipped": len(skipped),

        "category_statistics":
            get_category_statistics(findings),

        "registered_accounts":
            registered,

        "inconclusive_accounts":
            get_inconclusive_accounts(findings),

        "error_statistics":
            summarize_errors(findings)
    }