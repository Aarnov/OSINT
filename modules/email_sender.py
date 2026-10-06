import os
import smtplib
from email.message import EmailMessage
from html import escape

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def get_simulation_content(simulation_type):
    """
    Return generic content based only on the simulation type.

    The selected service is inserted dynamically later.
    """

    if simulation_type == "security_alert":
        return {
            "subject": "Security Alert — Unrecognized Activity",
            "title": "Unrecognized Activity",
            "description": (
                "A simulated security event was detected "
                "associated with your account."
            ),
            "activity": "Unrecognized account activity",
            "verification": "Security activity review",
        }

    if simulation_type == "profile_update":
        return {
            "subject": "Profile Update Notification",
            "title": "Profile Update",
            "description": (
                "A simulated notification has been generated "
                "regarding a change to your account profile."
            ),
            "activity": "Profile update",
            "verification": "Profile activity review",
        }

    return {
        "subject": "Account Activity Notification",
        "title": "Account Activity",
        "description": (
            "A simulated account activity notification "
            "has been generated for this security exercise."
        ),
        "activity": "Account activity",
        "verification": "Activity review",
    }


def send_simulation_email(
    recipient_email,
    service_name,
    simulation_url,
    simulation_type="security_alert"
):
    """
    Send an authorized OSINTRecon security-awareness
    simulation email.

    The service name is completely dynamic and can be
    any service selected by the investigator.

    No passwords, authentication tokens, recovery codes,
    or account credentials are requested.
    """

    sender_email = os.getenv("SMTP_EMAIL")
    app_password = os.getenv("SMTP_APP_PASSWORD")

    if not sender_email:
        return {
            "success": False,
            "error": "SMTP_EMAIL is not configured."
        }

    if not app_password:
        return {
            "success": False,
            "error": "SMTP_APP_PASSWORD is not configured."
        }

    if not recipient_email:
        return {
            "success": False,
            "error": "Recipient email is required."
        }

    if not service_name:
        return {
            "success": False,
            "error": "Service name is required."
        }

    if not simulation_url:
        return {
            "success": False,
            "error": "Simulation URL is required."
        }

    content = get_simulation_content(
        simulation_type
    )

    # Escape user-controlled values before placing them
    # inside the HTML email.
    safe_service = escape(
        str(service_name).strip()
    )

    safe_title = escape(
        content["title"]
    )

    safe_description = escape(
        content["description"]
    )

    safe_activity = escape(
        content["activity"]
    )

    safe_verification = escape(
        content["verification"]
    )

    safe_url = escape(
        str(simulation_url),
        quote=True
    )

    subject = (
        f"{safe_service} — "
        f"{content['subject']}"
    )

    # --------------------------------------------------
    # Plain-text version
    # --------------------------------------------------

    text_body = f"""
OSINTRecon Authorized Security Simulation

{service_name}

{content["title"]}

{content["description"]}

SERVICE
{service_name}

ACTIVITY
{content["activity"]}

VERIFICATION
{content["verification"]}

Review the simulated activity:
{simulation_url}

IMPORTANT

This message is part of an authorized OSINTRecon
security-awareness exercise.

It is not an official message from {service_name}.

No password, authentication token, recovery code,
or account credentials are requested or collected.
""".strip()

    # --------------------------------------------------
    # HTML version
    # --------------------------------------------------

    html_body = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        {safe_service} Security Simulation
    </title>

</head>


<body style="
    margin:0;
    padding:0;
    background:#f4f6f8;
    font-family:Arial, Helvetica, sans-serif;
    color:#202124;
">


    <div style="
        max-width:600px;
        margin:40px auto;
        background:#ffffff;
        border:1px solid #dadce0;
        border-radius:10px;
        overflow:hidden;
    ">


        <!--
            Simulation identification
        -->

        <div style="
            padding:15px 24px;
            background:#f8f9fa;
            border-bottom:1px solid #e5e7eb;
            font-size:11px;
            font-weight:bold;
            letter-spacing:0.8px;
            color:#667085;
        ">

            OSINTRecon AUTHORIZED SECURITY SIMULATION

        </div>


        <!--
            Dynamic service section
        -->

        <div style="
            padding:28px;
            border-bottom:1px solid #eaecf0;
        ">

            <div style="
                font-size:12px;
                font-weight:bold;
                letter-spacing:0.6px;
                color:#667085;
                margin-bottom:8px;
                text-transform:uppercase;
            ">

                Service

            </div>


            <div style="
                font-size:24px;
                font-weight:700;
                color:#202124;
                word-break:break-word;
            ">

                {safe_service}

            </div>

        </div>


        <!--
            Main notification
        -->

        <div style="
            padding:28px;
        ">


            <h1 style="
                margin:0 0 12px;
                font-size:23px;
                line-height:1.35;
                color:#202124;
            ">

                {safe_title}

            </h1>


            <p style="
                margin:0 0 24px;
                font-size:15px;
                line-height:1.6;
                color:#475467;
            ">

                {safe_description}

            </p>


            <!--
                Activity details
            -->

            <div style="
                border:1px solid #eaecf0;
                border-radius:8px;
                overflow:hidden;
                margin-bottom:26px;
            ">


                <div style="
                    padding:15px 17px;
                    border-bottom:1px solid #eaecf0;
                ">

                    <div style="
                        font-size:11px;
                        font-weight:bold;
                        letter-spacing:0.5px;
                        color:#667085;
                        margin-bottom:6px;
                    ">

                        SERVICE

                    </div>


                    <div style="
                        font-size:14px;
                        font-weight:600;
                        color:#202124;
                        word-break:break-word;
                    ">

                        {safe_service}

                    </div>

                </div>


                <div style="
                    padding:15px 17px;
                    border-bottom:1px solid #eaecf0;
                ">

                    <div style="
                        font-size:11px;
                        font-weight:bold;
                        letter-spacing:0.5px;
                        color:#667085;
                        margin-bottom:6px;
                    ">

                        ACTIVITY

                    </div>


                    <div style="
                        font-size:14px;
                        font-weight:600;
                        color:#202124;
                    ">

                        {safe_activity}

                    </div>

                </div>


                <div style="
                    padding:15px 17px;
                ">

                    <div style="
                        font-size:11px;
                        font-weight:bold;
                        letter-spacing:0.5px;
                        color:#667085;
                        margin-bottom:6px;
                    ">

                        VERIFICATION

                    </div>


                    <div style="
                        font-size:14px;
                        font-weight:600;
                        color:#202124;
                    ">

                        {safe_verification}

                    </div>

                </div>


            </div>


            <!--
                Simulation action
            -->

            <div style="
                text-align:center;
                margin:30px 0;
            ">


                <a
                    href="{safe_url}"
                    style="
                        display:inline-block;
                        padding:13px 25px;
                        background:#1d2939;
                        color:#ffffff;
                        text-decoration:none;
                        border-radius:6px;
                        font-size:14px;
                        font-weight:bold;
                    "
                >

                    Review Simulated Activity

                </a>


            </div>


            <!--
                Authorization notice
            -->

            <div style="
                padding:16px;
                background:#fff8e1;
                border:1px solid #f1df9a;
                border-radius:7px;
            ">


                <div style="
                    font-size:13px;
                    font-weight:bold;
                    color:#344054;
                    margin-bottom:7px;
                ">

                    Authorized Security Exercise

                </div>


                <div style="
                    font-size:13px;
                    line-height:1.6;
                    color:#667085;
                ">

                    This message is part of an authorized
                    OSINTRecon security-awareness simulation.

                    It is not an official message from
                    <strong>{safe_service}</strong>.

                    No password, authentication token,
                    recovery code, or account credentials
                    are requested or collected.

                </div>


            </div>


        </div>


        <!--
            Footer
        -->

        <div style="
            padding:18px 28px;
            background:#f8f9fa;
            border-top:1px solid #eaecf0;
            text-align:center;
            font-size:11px;
            line-height:1.5;
            color:#98a2b3;
        ">

            OSINTRecon Authorized Security Simulation

        </div>


    </div>


</body>

</html>
"""

    # --------------------------------------------------
    # Build email
    # --------------------------------------------------

    email = EmailMessage()

    email["From"] = sender_email
    email["To"] = recipient_email
    email["Subject"] = subject

    email.set_content(
        text_body
    )

    email.add_alternative(
        html_body,
        subtype="html"
    )

    # --------------------------------------------------
    # Send through Gmail SMTP
    # --------------------------------------------------

    try:

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                sender_email,
                app_password
            )

            server.send_message(
                email
            )

        return {
            "success": True,
            "recipient": recipient_email,
            "service": service_name,
            "subject": subject
        }

    except smtplib.SMTPAuthenticationError:

        return {
            "success": False,
            "error": (
                "Gmail authentication failed. "
                "Check the Gmail App Password and "
                "2-Step Verification."
            )
        }

    except smtplib.SMTPException as e:

        return {
            "success": False,
            "error": f"SMTP error: {e}"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }