import subprocess
import sys
import json
import re
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SCAN_DIR = BASE_DIR / "data" / "scans"

SCAN_DIR.mkdir(parents=True, exist_ok=True)


def email_to_filename(email):
    """
    Convert an email address into a safe filename.

    Example:
    aarnovadhikari123@gmail.com
    ->
    aarnovadhikari123_at_gmail.com.json
    """

    safe_email = email.strip().lower()

    safe_email = safe_email.replace("@", "_at_")

    safe_email = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        safe_email
    )

    return f"{safe_email}.json"


def run_email_scan(email):

    output_filename = email_to_filename(email)
    output_file = SCAN_DIR / output_filename

    # Delete the previous report before starting a new scan.
    # This ensures one email always has one current report.
    if output_file.exists():

        try:
            output_file.unlink()

        except OSError as e:

            return {
                "success": False,
                "scan_id": output_filename,
                "error": (
                    f"Could not replace the previous "
                    f"scan report: {e}"
                ),
                "data": None
            }

    # Run user-scanner through the active Python interpreter
    # with UTF-8 mode explicitly enabled.
    command = [
        str(sys.executable),
        "-X",
        "utf8",
        "-m",
        "user_scanner",
        "-e",
        email,
        "-f",
        "json",
        "-o",
        str(output_file)
    ]

    process_env = os.environ.copy()

    process_env["PYTHONIOENCODING"] = "utf-8"
    process_env["PYTHONUTF8"] = "1"
    process_env["LC_ALL"] = "C.UTF-8"
    process_env["LANG"] = "C.UTF-8"

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=process_env,
            timeout=300
        )

        if result.returncode != 0:

            return {
                "success": False,
                "scan_id": output_filename,
                "error": (
                    result.stderr
                    or "User Scanner failed."
                ),
                "data": None
            }

        if not output_file.exists():

            return {
                "success": False,
                "scan_id": output_filename,
                "error": (
                    "User Scanner did not create "
                    "the JSON output file."
                ),
                "data": None
            }

        with open(
            output_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            "success": True,
            "scan_id": output_filename,
            "error": None,
            "data": data
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "scan_id": output_filename,
            "error": "Scan timed out after 5 minutes.",
            "data": None
        }

    except json.JSONDecodeError:

        return {
            "success": False,
            "scan_id": output_filename,
            "error": (
                "The generated JSON file "
                "could not be parsed."
            ),
            "data": None
        }

    except Exception as e:

        return {
            "success": False,
            "scan_id": output_filename,
            "error": str(e),
            "data": None
        }