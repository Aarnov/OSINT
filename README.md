```markdown
# OSINT Recon

An Email Digital Footprint Analysis platform designed for mapping publicly observable accounts and conducting
authorized security awareness exercises. 

 **Disclaimer:** This tool is designed strictly for authorized public-source analysis and educational security
   awareness exercises. Users must ensure they have explicit permission before scanning targets or sending active
   interaction simulations.

## Features

* **Email Reconnaissance:** Analyzes publicly observable accounts associated with an authorized email identity.
* **Digital Footprint Mapping:** Categorizes confirmed accounts and visualizes the distribution of the target's
    digital footprint across platforms.
* **Inconclusive Result Handling:** Tracks services where account status could not be reliably determined and
    indicates whether the check is retryable
    (e.g., due to rate limits or connection errors).
* **Active Interaction Simulation:** Generates a controlled interaction endpoint toconduct authorized security
    exercises. Includes built-in templates such as Account Notification, Security Alert, and Profile Update.
* **Evidence Collection:** Automatically captures the interaction IP address, timestamp, and User-Agent when a
     target interacts with a simulation endpoint.
* **Location Tracking:** Optionally requests and records the target's latitude, longitude, accuracy, and source
     using the browser Geolocation API, strictly subject to explicit user consent.
* **Integrated Email Delivery:** Sends the authorized security-awareness simulation directly to the participant's
     email address without requesting or collecting actual credentials.

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Custom Dark Theme)
* **Testing:** Python `unittest` / `pytest` (located in the `tests/` directory)

## Project Structure

```text
├── app.py                      # Main Flask application and API routing
├── modules/
│   ├── scanner.py              # OSINT email scanning logic execution
│   ├── parser.py               # Data normalization and summarization
│   ├── analysis.py             # Analytics and digital footprint categorization
│   ├── active_interaction.py   # Investigation and interaction evidence logging
│   ├── simulation.py           # Simulation state management
│   ├── email_sender.py         # Outbound simulation email delivery via SMTP
│   ├── error_handler.py        # Classification of inconclusive/failed scan attempts
│   └── correlation.py          # Footprint area identification and categorization
├── static/
│   ├── css/
│   │   └── style.css           # UI styling and responsive dark theme grid layout
│   └── js/
│       └── app.js              # Client-side logic, API fetching, and simulation polling
├── templates/
│   └── index.html              # Main dashboard interface
└── tests/                      # Automated test suite for CI/CD integration

```

## Prerequisites

* Python 3.8+
* A valid Gmail account with an App Password (for simulation email delivery)
* The underlying `user_scanner` module available in your Python environment

## Installation & Setup

1. **Clone the repository:**
```bash
git clone [https://github.com/Aarnov/OSINT.git](https://github.com/Aarnov/OSINT.git)
cd OSINT
```


2. **Create and activate a virtual environment:**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate  

# On Windows:
venv\Scripts\activate
```


3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables:**
Create a `.env` file in the root directory of the project to configure the SMTP sender for the active simulation emails:
```env
SMTP_EMAIL=your_authorized_sender@gmail.com
SMTP_APP_PASSWORD=your_16_character_app_password
```



## Usage

1. **Start the server:**
```bash
python app.py
```

  *The application will start in debug mode on http://127.0.0.1:5000/.*

2. **Run a Scan:**
Navigate to the web interface, enter a valid target email address in the "New Reconnaissance" panel, and click "Start Scan".

3. **Review Findings:**
Analyze the confirmed accounts, inconclusive results, and overall footprint statistics on the dashboard.

5. **Deploy a Simulation:**
Select a confirmed service from the active simulation dropdown, choose a simulation type, and click "Create Simulation". Use the dynamic simulation panel to send the email directly to the target.

6. **Monitor Interactions:**
The system will automatically poll for interactions every 3 seconds. When the target clicks the link, the dashboard will automatically update with the interaction timestamp, User-Agent, IP, and location data (if consent is granted by the target).

## Testing

This project includes a test suite located in the `tests/` directory to ensure module reliability and safeguard against regressions during future development.

To run the tests:

```bash
# If using pytest
pytest tests/

# If using standard unittest
python -m unittest discover -s tests

```

## License

This project is intended strictly for educational and authorized public-source analysis. Ensure you explicitly disclaim liability for misuse of the scanning and active interaction simulation features before deploying.
