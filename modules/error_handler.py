
def classify_error(reason):
    """
    Classify a scanner error into a useful category.

    This does not attempt to bypass security controls.
    It only helps us understand why a result was inconclusive.
    """

    if not reason:
        return {
            "type": "unknown",
            "retryable": False,
            "label": "Unknown error"
        }

    message = reason.lower()


    # Network / connection problems

    if (
        "connecterror" in message
        or "connection reset" in message
        or "connection was reset" in message
        or "network error" in message
        or "failed to perform" in message
        or "writeerror" in message
        or "readtimeout" in message
    ):
        return {
            "type": "connection",
            "retryable": True,
            "label": "Connection failure"
        }


    # Rate limiting

    if (
        "429" in message
        or "rate limit" in message
        or "too many requests" in message
    ):
        return {
            "type": "rate_limit",
            "retryable": True,
            "label": "Rate limited"
        }


    # Anti-bot / challenge systems

    if (
        "cloudflare" in message
        or "bot challenge" in message
        or "behind a bot challenge" in message
        or "captcha" in message
    ):
        return {
            "type": "anti_bot",
            "retryable": False,
            "label": "Anti-bot protection"
        }


    # Access denied

    if (
        "403" in message
        or "forbidden" in message
        or "blocked" in message
    ):
        return {
            "type": "access_denied",
            "retryable": False,
            "label": "Request blocked"
        }


    # Authentication / authorization

    if (
        "401" in message
        or "unauthorized" in message
        or "authentication" in message
    ):
        return {
            "type": "authentication",
            "retryable": False,
            "label": "Authentication required"
        }


    # Request format / client rejection

    if "406" in message:
        return {
            "type": "request_rejected",
            "retryable": False,
            "label": "Request rejected"
        }


    # Module / response parsing problems

    if (
        "unexpected response" in message
        or "unexpected validation" in message
        or "unexpected token" in message
        or "unknown action response" in message
        or "failed to extract" in message
        or "csrf" in message
    ):
        return {
            "type": "module",
            "retryable": False,
            "label": "Module response error"
        }


    return {
        "type": "unknown",
        "retryable": False,
        "label": "Unknown error"
    }


def enrich_errors(findings):
    """
    Add structured error information to scanner findings.
    """

    enriched = []

    for finding in findings:

        updated = finding.copy()

        status = (
            finding.get("status", "")
            .lower()
            .strip()
        )

        if status == "error":

            error_info = classify_error(
                finding.get("reason", "")
            )

            updated["error_info"] = error_info

        enriched.append(updated)

    return enriched


def summarize_errors(findings):
    """
    Count errors by their classified type.
    """

    summary = {}

    for finding in findings:

        status = (
            finding.get("status", "")
            .lower()
            .strip()
        )

        if status != "error":
            continue

        error_info = classify_error(
            finding.get("reason", "")
        )

        error_type = error_info["type"]

        if error_type not in summary:
            summary[error_type] = {
                "count": 0,
                "label": error_info["label"],
                "retryable": error_info["retryable"]
            }

        summary[error_type]["count"] += 1

    return summary

