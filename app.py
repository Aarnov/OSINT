from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify

from modules.scanner import run_email_scan
from modules.parser import normalize_results, summarize_results
from modules.analysis import build_analysis

from modules.active_interaction import (
    create_investigation,
    record_interaction,
    record_location
)

from modules.simulation import (
    create_simulation,
    mark_interaction
)

from modules.email_sender import (
    send_simulation_email
)


app = Flask(__name__)


# Temporary in-memory storage.
active_investigations = {}
active_simulations = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def scan():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No request data received."
        }), 400

    email = data.get(
        "email",
        ""
    ).strip()

    if not email:
        return jsonify({
            "success": False,
            "error": "Please enter an email address."
        }), 400

    if (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):
        return jsonify({
            "success": False,
            "error": "Please enter a valid email address."
        }), 400

    print(
        f"[+] Starting scan for: {email}"
    )

    result = run_email_scan(email)

    if not result["success"]:
        return jsonify({
            "success": False,
            "error": result["error"]
        }), 500

    findings = normalize_results(
        result["data"]
    )

    summary = summarize_results(
        findings
    )

    analysis = build_analysis(
        findings
    )

    print(
        f"[+] Scan complete: "
        f"{summary['registered']} registered, "
        f"{summary['not_registered']} not registered, "
        f"{summary['errors']} errors, "
        f"{summary['skipped']} skipped"
    )

    return jsonify({
        "success": True,
        "scan_id": result["scan_id"],
        "summary": summary,
        "analysis": analysis
    })


@app.route(
    "/api/active/create",
    methods=["POST"]
)
def create_active_investigation():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No request data received."
        }), 400

    email = data.get(
        "email",
        ""
    ).strip()

    if not email:
        return jsonify({
            "success": False,
            "error": "Target email is required."
        }), 400

    if (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):
        return jsonify({
            "success": False,
            "error": "Please enter a valid email address."
        }), 400

    result = create_investigation(
        email
    )

    if not result["success"]:
        return jsonify(result), 400

    investigation = result["investigation"]

    token = investigation.get(
        "token"
    )

    if not token:
        import secrets

        token = secrets.token_urlsafe(
            16
        )

        investigation["token"] = token

    active_investigations[token] = (
        investigation
    )

    print(
        f"[+] Active investigation created: "
        f"{token}"
    )

    return jsonify({
        "success": True,
        "investigation": {
            "token": token,
            "target_email":
                investigation["target_email"],
            "created_at":
                investigation["created_at"]
        }
    })


@app.route(
    "/api/active/simulation",
    methods=["POST"]
)
def create_active_simulation():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No request data received."
        }), 400

    email = data.get(
        "email",
        ""
    ).strip()

    service_name = data.get(
        "service_name",
        ""
    ).strip()

    simulation_type = data.get(
        "simulation_type",
        "account_notification"
    )

    result = create_simulation(
        email,
        service_name,
        simulation_type
    )

    if not result["success"]:
        return jsonify(result), 400

    simulation = result["simulation"]

    token = simulation["token"]

    active_simulations[token] = (
        simulation
    )

    print(
        f"[+] Simulation created: "
        f"{service_name} / {token}"
    )

    return jsonify({
        "success": True,
        "simulation": simulation
    })


@app.route(
    "/api/active/simulation/<token>/send-email",
    methods=["POST"]
)
def send_active_simulation_email(token):

    simulation = active_simulations.get(
        token
    )

    if simulation is None:
        return jsonify({
            "success": False,
            "error": "Simulation not found or expired."
        }), 404

    data = request.get_json() or {}

    recipient_email = data.get(
        "recipient_email",
        ""
    ).strip()

    if not recipient_email:
        return jsonify({
            "success": False,
            "error": "Recipient email is required."
        }), 400

    if (
        "@" not in recipient_email
        or "." not in recipient_email.split("@")[-1]
    ):
        return jsonify({
            "success": False,
            "error": (
                "Please enter a valid recipient "
                "email address."
            )
        }), 400

    service_name = simulation.get(
        "service_name",
        "Online Service"
    )

    simulation_type = simulation.get(
        "simulation_type",
        "account_notification"
    )

    simulation_url = (
        request.url_root.rstrip("/")
        + f"/active/{token}"
    )

    result = send_simulation_email(
        recipient_email=recipient_email,
        service_name=service_name,
        simulation_url=simulation_url,
        simulation_type=simulation_type
    )

    if not result["success"]:
        return jsonify(result), 500

    simulation["email"] = {
        "sent": True,
        "recipient": recipient_email,
        "subject": result.get(
            "subject",
            ""
        ),
        "sent_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    print(
        f"[+] Simulation email sent: "
        f"{service_name} -> "
        f"{recipient_email}"
    )

    return jsonify({
        "success": True,
        "message": (
            "Simulation email sent successfully."
        ),
        "email": simulation["email"]
    })


@app.route(
    "/active/<token>",
    methods=["GET"]
)
def active_interaction(token):

    simulation = active_simulations.get(
        token
    )

    if simulation is not None:

        interaction_result = record_interaction(
            simulation,
            request.remote_addr,
            request.headers.get(
                "User-Agent",
                ""
            )
        )

        if not interaction_result["success"]:
            return (
                "Unable to record interaction.",
                500
            )

        mark_interaction(
            simulation
        )

        print(
            f"[+] Simulation interaction received: "
            f"{request.remote_addr}"
        )

        service_name = simulation.get(
            "service_name",
            "Online Service"
        )

        return f"""
        <!DOCTYPE html>
        <html>

        <head>

            <meta charset="UTF-8">

            <title>
                Security Notification Simulation
            </title>

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <style>

                * {{
                    box-sizing: border-box;
                }}

                body {{
                    margin: 0;
                    min-height: 100vh;
                    background: #0b0f14;
                    font-family:
                        Arial,
                        Helvetica,
                        sans-serif;
                    color: #e6edf3;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 24px;
                }}

                .container {{
                    width: 100%;
                    max-width: 520px;
                }}

                .simulation-label {{
                    text-align: center;
                    font-size: 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    color: #7d8996;
                    margin-bottom: 14px;
                    text-transform: uppercase;
                }}

                .card {{
                    background: #111720;
                    border: 1px solid #202a35;
                    border-radius: 12px;
                    padding: 32px;
                    box-shadow:
                        0 8px 30px
                        rgba(0, 0, 0, 0.5);
                }}

                .icon {{
                    width: 52px;
                    height: 52px;
                    border-radius: 50%;
                    background: #5d4d28;
                    color: #e8c766;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 25px;
                    margin-bottom: 22px;
                }}

                h1 {{
                    font-size: 23px;
                    margin: 0 0 12px;
                }}

                .subtitle {{
                    color: #9aa6b2;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }}

                .details {{
                    border: 1px solid #202a35;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 24px;
                }}

                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    gap: 20px;
                    padding: 8px 0;
                    font-size: 14px;
                }}

                .detail-row span:first-child {{
                    color: #7d8996;
                }}

                .detail-row strong {{
                    text-align: right;
                    word-break: break-word;
                }}

                .notice {{
                    background: #0b0f14;
                    border: 1px solid #202a35;
                    border-radius: 8px;
                    padding: 14px;
                    font-size: 13px;
                    color: #7d8996;
                    line-height: 1.55;
                    margin-bottom: 20px;
                }}

                button {{
                    width: 100%;
                    border: none;
                    border-radius: 7px;
                    padding: 13px 18px;
                    background: #39d98a;
                    color: #07110b;
                    font-size: 15px;
                    font-weight: bold;
                    cursor: pointer;
                }}

                button:hover {{
                    opacity: 0.9;
                }}

                button:disabled {{
                    opacity: 0.6;
                    cursor: not-allowed;
                }}

                .status {{
                    display: none;
                    margin-top: 18px;
                    padding: 14px;
                    border-radius: 8px;
                    background: #17261f;
                    border: 1px solid #285c45;
                    color: #39d98a;
                    font-size: 14px;
                    line-height: 1.5;
                }}

                .error {{
                    display: none;
                    margin-top: 18px;
                    padding: 14px;
                    border-radius: 8px;
                    background: #261b17;
                    border: 1px solid #5d3428;
                    color: #e8a98e;
                    font-size: 14px;
                    line-height: 1.5;
                }}

                .footer {{
                    text-align: center;
                    color: #56616d;
                    font-size: 11px;
                    margin-top: 16px;
                    line-height: 1.5;
                }}

            </style>

        </head>


        <body>

            <div class="container">

                <div class="simulation-label">

                    OSINTRecon Authorized
                    Security Simulation

                </div>


                <div class="card">


                    <div class="icon">
                        ⚠
                    </div>


                    <h1>
                        Unrecognized sign-in attempt
                    </h1>


                    <div class="subtitle">

                        A simulated sign-in attempt was
                        detected for your account on
                        <strong>{service_name}</strong>.

                    </div>


                    <div class="details">


                        <div class="detail-row">

                            <span>
                                Device
                            </span>

                            <strong>
                                Unrecognized device
                            </strong>

                        </div>


                        <div class="detail-row">

                            <span>
                                Activity
                            </span>

                            <strong>
                                Sign-in attempt
                            </strong>

                        </div>


                        <div class="detail-row">

                            <span>
                                Verification
                            </span>

                            <strong>
                                Location confirmation
                            </strong>

                        </div>


                    </div>


                    <div class="notice">

                        To participate in the
                        location-awareness portion of
                        this security exercise, you may
                        voluntarily share the location of
                        this device.

                        Your browser will display its own
                        permission prompt. Location
                        information will only be sent if
                        you explicitly allow it.

                    </div>


                    <button
                        id="locationButton"
                        onclick="shareLocation()"
                    >
                        Confirm My Location
                    </button>


                    <div
                        class="status"
                        id="status"
                    >

                        ✓ Location shared successfully.
                        You may close this page.

                    </div>


                    <div
                        class="error"
                        id="error"
                    ></div>


                </div>


                <div class="footer">

                    This is an authorized OSINTRecon
                    classroom simulation.

                    No password, authentication token,
                    or account credentials are collected.

                </div>


            </div>


            <script>

                async function shareLocation() {{

                    const button =
                        document.getElementById(
                            "locationButton"
                        );

                    const status =
                        document.getElementById(
                            "status"
                        );

                    const error =
                        document.getElementById(
                            "error"
                        );


                    status.style.display =
                        "none";

                    error.style.display =
                        "none";


                    if (!navigator.geolocation) {{

                        error.textContent =
                            "This browser does not support "
                            + "location services.";

                        error.style.display =
                            "block";

                        return;

                    }}


                    button.disabled = true;

                    button.textContent =
                        "Requesting Location Permission...";


                    navigator.geolocation.getCurrentPosition(

                        async function(position) {{

                            const location = {{

                                latitude:
                                    position.coords.latitude,

                                longitude:
                                    position.coords.longitude,

                                accuracy:
                                    position.coords.accuracy

                            }};


                            try {{

                                const response =
                                    await fetch(
                                        "/api/active/{token}/location",
                                        {{
                                            method: "POST",

                                            headers: {{
                                                "Content-Type":
                                                    "application/json"
                                            }},

                                            body:
                                                JSON.stringify(
                                                    location
                                                )
                                        }}
                                    );


                                const result =
                                    await response.json();


                                if (!result.success) {{

                                    throw new Error(
                                        result.error
                                        ||
                                        "Location could not "
                                        + "be recorded."
                                    );

                                }}


                                button.textContent =
                                    "Location Confirmed";

                                status.style.display =
                                    "block";


                            }} catch (err) {{

                                button.disabled =
                                    false;

                                button.textContent =
                                    "Confirm My Location";

                                error.textContent =
                                    err.message;

                                error.style.display =
                                    "block";

                            }}

                        }},


                        function(positionError) {{

                            button.disabled =
                                false;

                            button.textContent =
                                "Confirm My Location";


                            let message =
                                "Location permission "
                                + "was not granted.";


                            if (
                                positionError.code === 1
                            ) {{

                                message =
                                    "Location permission "
                                    + "was denied.";

                            }}


                            if (
                                positionError.code === 2
                            ) {{

                                message =
                                    "Your location could "
                                    + "not be determined.";

                            }}


                            if (
                                positionError.code === 3
                            ) {{

                                message =
                                    "Location request "
                                    + "timed out.";

                            }}


                            error.textContent =
                                message;

                            error.style.display =
                                "block";

                        }},


                        {{
                            enableHighAccuracy: true,
                            timeout: 15000,
                            maximumAge: 0
                        }}

                    );

                }}

            </script>


        </body>

        </html>
        """

    investigation = active_investigations.get(
        token
    )

    if investigation is None:
        return (
            "Investigation not found or expired.",
            404
        )

    result = record_interaction(
        investigation,
        request.remote_addr,
        request.headers.get(
            "User-Agent",
            ""
        )
    )

    if not result["success"]:
        return (
            "Unable to record interaction.",
            500
        )

    print(
        f"[+] Active interaction received: "
        f"{request.remote_addr}"
    )

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Interaction Received
        </title>

        <style>
            body {
                background: #0b0f14;
                color: #e6edf3;
                font-family: Arial, Helvetica, sans-serif;
                text-align: center;
                padding: 50px 20px;
                margin: 0;
            }
            p {
                color: #7d8996;
            }
        </style>

    </head>

    <body>

        <h1>
            Interaction received
        </h1>

        <p>
            This controlled investigation endpoint
            has recorded the test interaction.
        </p>

    </body>

    </html>
    """


@app.route(
    "/api/active/<token>/location",
    methods=["POST"]
)
def receive_location(token):

    simulation = active_simulations.get(
        token
    )

    if simulation is not None:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No location data received."
            }), 400

        result = record_location(
            simulation,
            data.get("latitude"),
            data.get("longitude"),
            data.get("accuracy")
        )

        if not result["success"]:
            return jsonify(result), 400

        print(
            "[+] Browser location received "
            f"for simulation {token}: "
            f"{result['location']['latitude']}, "
            f"{result['location']['longitude']} "
            f"(±"
            f"{result['location']['accuracy_meters']}"
            f"m)"
        )

        return jsonify(result)


    investigation = active_investigations.get(
        token
    )

    if investigation is None:
        return jsonify({
            "success": False,
            "error":
                "Investigation not found or expired."
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No location data received."
        }), 400

    result = record_location(
        investigation,
        data.get("latitude"),
        data.get("longitude"),
        data.get("accuracy")
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)


@app.route(
    "/api/active/<token>",
    methods=["GET"]
)
def get_active_investigation(token):

    simulation = active_simulations.get(
        token
    )

    if simulation is not None:

        return jsonify({
            "success": True,
            "type": "simulation",
            "simulation": simulation
        })


    investigation = active_investigations.get(
        token
    )

    if investigation is None:
        return jsonify({
            "success": False,
            "error":
                "Investigation not found or expired."
        }), 404

    return jsonify({
        "success": True,
        "type": "investigation",
        "investigation": investigation
    })


if __name__ == "__main__":

    app.run(
        debug=True
    )