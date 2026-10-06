from datetime import datetime, timezone


def create_investigation(target_email):
    """
    Create a controlled active-interaction investigation.

    No personal information is collected at creation time.
    """

    target_email = str(
        target_email or ""
    ).strip().lower()

    if not target_email:
        return {
            "success": False,
            "error": "Target email is required."
        }

    return {
        "success": True,
        "investigation": {
            "target_email": target_email,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "interactions": []
        }
    }


def record_interaction(
    investigation,
    ip_address,
    user_agent
):
    """
    Record technical metadata from an authorized
    interaction with the simulation.
    """

    if not investigation:
        return {
            "success": False,
            "error": "Investigation not found."
        }

    interaction = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "ip_address": str(
            ip_address or ""
        ),
        "user_agent": str(
            user_agent or ""
        ),
        "location": None
    }

    investigation.setdefault(
        "interactions",
        []
    ).append(interaction)

    return {
        "success": True,
        "interaction": interaction
    }


def record_location(
    investigation,
    latitude,
    longitude,
    accuracy
):
    """
    Record browser-provided location only after
    the participant explicitly grants permission.
    """

    if not investigation:
        return {
            "success": False,
            "error": "Investigation not found."
        }

    interactions = investigation.get(
        "interactions",
        []
    )

    if not interactions:
        return {
            "success": False,
            "error": "No interaction has been recorded yet."
        }

    try:
        latitude = float(latitude)
        longitude = float(longitude)
        accuracy = float(accuracy)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Invalid location data."
        }

    if not -90 <= latitude <= 90:
        return {
            "success": False,
            "error": "Invalid latitude."
        }

    if not -180 <= longitude <= 180:
        return {
            "success": False,
            "error": "Invalid longitude."
        }

    if accuracy < 0:
        return {
            "success": False,
            "error": "Invalid location accuracy."
        }

    location = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy_meters": round(
            accuracy,
            2
        ),
        "source": "Browser Geolocation",
        "consent": "Granted",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    interactions[-1]["location"] = location

    return {
        "success": True,
        "location": location
    }


def get_latest_interaction(
    investigation
):
    """
    Return the most recent interaction.
    """

    interactions = investigation.get(
        "interactions",
        []
    )

    if not interactions:
        return None

    return interactions[-1]