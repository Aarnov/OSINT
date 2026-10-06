import secrets
from datetime import datetime, timezone


SIMULATION_TYPES = {
    "account_notification": {
        "name": "Account Notification",
        "description": (
            "A simulated notification about activity "
            "on an online account."
        )
    },
    "security_alert": {
        "name": "Security Alert",
        "description": (
            "A simulated security notification "
            "requiring the participant to review activity."
        )
    },
    "profile_update": {
        "name": "Profile Update",
        "description": (
            "A simulated notification about a "
            "profile or account update."
        )
    }
}


def create_simulation(
    target_email,
    service_name,
    simulation_type="account_notification"
):
    """
    Create an authorized interaction simulation.

    The simulation does not collect credentials and does not
    attempt to authenticate against the real service.
    """

    target_email = str(
        target_email or ""
    ).strip().lower()

    service_name = str(
        service_name or ""
    ).strip()

    if not target_email:
        return {
            "success": False,
            "error": "Target email is required."
        }

    if not service_name:
        return {
            "success": False,
            "error": "Service name is required."
        }

    if simulation_type not in SIMULATION_TYPES:
        return {
            "success": False,
            "error": "Unknown simulation type."
        }

    token = secrets.token_urlsafe(16)

    simulation_info = SIMULATION_TYPES[
        simulation_type
    ]

    return {
        "success": True,
        "simulation": {
            "token": token,
            "target_email": target_email,
            "service_name": service_name,
            "simulation_type": simulation_type,
            "simulation_name":
                simulation_info["name"],
            "description":
                simulation_info["description"],
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "waiting",
            "interactions": []
        }
    }


def mark_interaction(simulation):
    """
    Mark a simulation as having received an interaction.
    """

    if not simulation:
        return {
            "success": False,
            "error": "Simulation not found."
        }

    simulation["status"] = "interacted"

    return {
        "success": True,
        "status": simulation["status"]
    }