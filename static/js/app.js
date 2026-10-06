let currentSimulationToken = null;
let simulationPollingTimer = null;

/*
 * RECONNAISSANCE SCAN
 */

async function startScan() {
    const emailInput = document.getElementById("emailInput");
    const scanButton = document.getElementById("scanButton");
    const email = emailInput.value.trim();

    if (!email) {
        alert("Please enter an email address.");
        emailInput.focus();
        return;
    }

    scanButton.disabled = true;
    scanButton.textContent = "Scanning...";

    try {
        const response = await fetch("/api/scan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.error);
            return;
        }

        updateDashboard(data);

    } catch (error) {
        console.error(error);
        alert("Unable to connect to the scanning server.");
    } finally {
        scanButton.disabled = false;
        scanButton.textContent = "Start Scan";
    }
}

function updateDashboard(data) {
    const summary = data.summary;
    const analysis = data.analysis;

    document.getElementById("registeredCount").textContent = summary.registered;
    document.getElementById("notRegisteredCount").textContent = summary.not_registered;
    document.getElementById("errorCount").textContent = summary.errors;
    document.getElementById("skippedCount").textContent = summary.skipped;
    document.getElementById("totalCount").textContent = summary.total;

    const percentage = summary.total > 0
        ? ((summary.registered / summary.total) * 100).toFixed(1)
        : 0;

    document.getElementById("registeredPercentage").textContent = percentage + "%";
    document.getElementById("categoryCount").textContent = Object.keys(analysis.category_statistics).length;
    document.getElementById("accountCount").textContent = analysis.registered_accounts.length + " accounts";

    renderFootprint(analysis.category_statistics);
    renderAccounts(analysis.registered_accounts);
    renderInconclusive(analysis.inconclusive_accounts, analysis.error_statistics);
    setupSimulationServices(analysis.registered_accounts);
}

function renderFootprint(categories) {
    const container = document.getElementById("footprintContainer");
    container.innerHTML = "";
    const entries = Object.entries(categories).sort((a, b) => b[1] - a[1]);

    if (entries.length === 0) {
        container.innerHTML = "<p>No registered accounts found.</p>";
        return;
    }

    const max = Math.max(...entries.map(entry => entry[1]));

    for (const [category, count] of entries) {
        const percentage = (count / max) * 100;
        const row = document.createElement("div");
        row.className = "footprint-row";
        row.innerHTML = `
            <div class="footprint-info">
                <span>${escapeHtml(category)}</span>
                <span>${count}</span>
            </div>
            <div class="progress">
                <div class="progress-bar" style="width: ${percentage}%"></div>
            </div>
        `;
        container.appendChild(row);
    }
}

function renderAccounts(accounts) {
    const table = document.getElementById("accountsTable");
    table.innerHTML = "";

    for (const account of accounts) {
        const row = document.createElement("tr");
        const url = account.url || "";
        const safeUrl = isSafeUrl(url) ? url : "";

        row.innerHTML = `
            <td>${escapeHtml(account.site_name)}</td>
            <td>${escapeHtml(account.category)}</td>
            <td><span class="status-badge">Registered</span></td>
            <td>
                ${safeUrl
                    ? `<a href="${escapeHtml(safeUrl)}" target="_blank" rel="noopener noreferrer">Open</a>`
                    : "—"}
            </td>
        `;
        table.appendChild(row);
    }
}

function renderInconclusive(accounts, statistics) {
    const count = document.getElementById("inconclusiveCount");
    const statsContainer = document.getElementById("errorStatistics");
    const table = document.getElementById("inconclusiveTable");

    count.textContent = accounts.length + " results";
    statsContainer.innerHTML = "";
    const entries = Object.entries(statistics).sort((a, b) => b[1].count - a[1].count);

    for (const [type, data] of entries) {
        const item = document.createElement("div");
        item.className = "error-stat";
        item.innerHTML = `
            <span>${escapeHtml(data.label)}</span>
            <strong>${data.count}</strong>
        `;
        statsContainer.appendChild(item);
    }

    table.innerHTML = "";

    for (const account of accounts) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${escapeHtml(account.site_name)}</td>
            <td>${escapeHtml(account.category)}</td>
            <td>${escapeHtml(account.error_label)}</td>
            <td>
                ${account.retryable
                    ? '<span class="retry-yes">YES</span>'
                    : '<span class="retry-no">NO</span>'}
            </td>
        `;
        table.appendChild(row);
    }
}


/*
 * ACTIVE INTERACTION SIMULATION
 */

function setupSimulationServices(accounts) {
    const panel = document.getElementById("activeSimulationPanel");
    const select = document.getElementById("simulationService");
    select.innerHTML = "";

    if (!accounts || accounts.length === 0) {
        panel.style.display = "none";
        return;
    }

    const services = [];
    const seen = new Set();

    for (const account of accounts) {
        const name = String(account.site_name || "").trim();
        if (!name) continue;

        const key = name.toLowerCase();
        if (seen.has(key)) continue;

        seen.add(key);
        services.push(name);
    }

    for (const service of services) {
        const option = document.createElement("option");
        option.value = service;
        option.textContent = service;
        select.appendChild(option);
    }

    panel.style.display = "block";
}

async function createActiveSimulation() {
    const email = document.getElementById("emailInput").value.trim();
    const serviceName = document.getElementById("simulationService").value;
    const simulationType = document.getElementById("simulationType").value;
    const button = document.getElementById("createSimulationButton");

    if (!email) {
        alert("Run a reconnaissance scan first.");
        return;
    }
    if (!serviceName) {
        alert("Select a confirmed service.");
        return;
    }

    button.disabled = true;
    button.textContent = "Creating...";

    stopSimulationPolling();

    try {
        const response = await fetch("/api/active/simulation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: email,
                service_name: serviceName,
                simulation_type: simulationType
            })
        });

        const data = await response.json();

        if (!data.success) {
            alert(data.error);
            return;
        }

        const simulation = data.simulation;
        currentSimulationToken = simulation.token;

        const simulationUrl = window.location.origin + "/active/" + simulation.token;

        document.getElementById("simulationUrl").textContent = simulationUrl;
        document.getElementById("simulationResult").style.display = "flex";
        document.getElementById("simulationInteractionStatus").textContent = "Waiting for interaction";
        document.getElementById("simulationStatusBadge").textContent = "WAITING";
        document.getElementById("simulationEvidence").style.display = "none";

        setupSimulationEmail(simulation);
        startSimulationPolling();

    } catch (error) {
        console.error(error);
        alert("Unable to create the simulation.");
    } finally {
        button.disabled = false;
        button.textContent = "Create Simulation";
    }
}

/*
 * SIMULATION EMAIL
 */

function setupSimulationEmail(simulation) {
    const resultContainer = document.getElementById("simulationResult");
    let emailSection = document.getElementById("simulationEmailSection");

    if (!emailSection) {
        emailSection = document.createElement("div");
        emailSection.id = "simulationEmailSection";
        emailSection.className = "simulation-card";

        emailSection.innerHTML = `
            <div class="simulation-card-header">
                <div>
                    <div class="simulation-card-title">SEND EMAIL</div>
                    <div class="simulation-email-notice">
                        Send the authorized security-awareness
                        simulation to the participant's email address.
                        No credentials are requested or collected.
                    </div>
                </div>
            </div>

            <div class="simulation-email-row">
                <input
                    id="simulationRecipientEmail"
                    type="email"
                    placeholder="Recipient email"
                    class="simulation-input"
                >
                <button
                    id="sendSimulationEmailButton"
                    type="button"
                    class="simulation-email-button"
                >
                    Send Simulation Email
                </button>
            </div>

            <div id="simulationEmailStatus"></div>
        `;

        resultContainer.appendChild(emailSection);

        document
            .getElementById("sendSimulationEmailButton")
            .addEventListener("click", sendSimulationEmail);
    }

    const recipientInput = document.getElementById("simulationRecipientEmail");
    const status = document.getElementById("simulationEmailStatus");
    const button = document.getElementById("sendSimulationEmailButton");

    recipientInput.value = simulation.target_email || "";
    status.textContent = "";
    status.className = "";
    button.disabled = false;
    button.textContent = "Send Simulation Email";
}

async function sendSimulationEmail() {
    if (!currentSimulationToken) {
        alert("Create a simulation first.");
        return;
    }

    const recipientInput = document.getElementById("simulationRecipientEmail");
    const button = document.getElementById("sendSimulationEmailButton");
    const status = document.getElementById("simulationEmailStatus");
    const recipientEmail = recipientInput.value.trim();

    if (!recipientEmail || !recipientEmail.includes("@") || !recipientEmail.split("@").at(-1).includes(".")) {
        alert("Please enter a valid recipient email address.");
        recipientInput.focus();
        return;
    }

    button.disabled = true;
    button.textContent = "Sending...";
    status.textContent = "Sending simulation email...";
    status.className = ""; 

    try {
        const response = await fetch(
            "/api/active/simulation/" + encodeURIComponent(currentSimulationToken) + "/send-email",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ recipient_email: recipientEmail })
            }
        );

        const data = await response.json();

        if (!data.success) {
            status.textContent = data.error || "Unable to send the simulation email.";
            status.className = "simulation-email-error";
            button.disabled = false;
            button.textContent = "Send Simulation Email";
            return;
        }

        status.textContent = "Simulation email sent to " + recipientEmail + ".";
        status.className = "simulation-email-success";
        button.textContent = "Email Sent";
        button.disabled = true;

        displaySimulationEmailEvidence(data.email);

    } catch (error) {
        console.error(error);
        status.textContent = "Unable to connect to the scanning server.";
        status.className = "simulation-email-error";
        button.disabled = false;
        button.textContent = "Send Simulation Email";
    }
}

function displaySimulationEmailEvidence(emailData) {
    const emailSection = document.getElementById("simulationEmailSection");
    let evidence = document.getElementById("simulationEmailEvidence");

    if (!evidence) {
        evidence = document.createElement("div");
        evidence.id = "simulationEmailEvidence";
        evidence.className = "simulation-email-details";

        evidence.innerHTML = `
            <div class="simulation-email-detail">
                <span>Email Status</span>
                <strong>Sent</strong>
            </div>
            <div class="simulation-email-detail">
                <span>Recipient</span>
                <strong id="simulationEmailRecipient">—</strong>
            </div>
            <div class="simulation-email-detail">
                <span>Subject</span>
                <strong id="simulationEmailSubject">—</strong>
            </div>
            <div class="simulation-email-detail">
                <span>Sent At</span>
                <strong id="simulationEmailSentAt">—</strong>
            </div>
        `;
        emailSection.appendChild(evidence);
    }

    document.getElementById("simulationEmailRecipient").textContent = emailData.recipient || "Unavailable";
    document.getElementById("simulationEmailSubject").textContent = emailData.subject || "Unavailable";
    document.getElementById("simulationEmailSentAt").textContent = formatTimestamp(emailData.sent_at);
}


/*
 * SIMULATION POLLING
 */

function startSimulationPolling() {
    stopSimulationPolling();
    if (!currentSimulationToken) return;
    
    checkSimulationStatus();
    simulationPollingTimer = setInterval(checkSimulationStatus, 3000);
}

function stopSimulationPolling() {
    if (simulationPollingTimer) {
        clearInterval(simulationPollingTimer);
        simulationPollingTimer = null;
    }
}

async function checkSimulationStatus() {
    if (!currentSimulationToken) return;

    try {
        const response = await fetch("/api/active/" + encodeURIComponent(currentSimulationToken));
        const data = await response.json();

        if (!data.success) return;
        if (data.type !== "simulation") return;

        const simulation = data.simulation;

        if (simulation.status === "interacted") {
            displaySimulationInteraction(simulation);
        }

    } catch (error) {
        console.error("Simulation status check failed:", error);
    }
}

function displaySimulationInteraction(simulation) {
    const interaction = simulation.interactions && simulation.interactions.length > 0
        ? simulation.interactions[simulation.interactions.length - 1]
        : null;

    if (!interaction) return;

    document.getElementById("simulationInteractionStatus").textContent = "Interaction received";
    document.getElementById("simulationStatusBadge").textContent = "INTERACTED";
    document.getElementById("simulationIp").textContent = interaction.ip_address || "Unavailable";
    document.getElementById("simulationTimestamp").textContent = formatTimestamp(interaction.timestamp);
    document.getElementById("simulationUserAgent").textContent = interaction.user_agent || "Unavailable";
    document.getElementById("simulationEvidence").style.display = "block";

    updateLocationEvidence(interaction);
}

/*
 * LOCATION EVIDENCE
 */

function updateLocationEvidence(interaction) {
    const evidenceContainer = document.getElementById("simulationEvidence");
    let locationSection = document.getElementById("simulationLocationEvidence");

    if (!locationSection) {
        locationSection = document.createElement("div");
        locationSection.id = "simulationLocationEvidence";
        locationSection.style.marginTop = "15px";
        locationSection.style.paddingTop = "15px";
        locationSection.style.borderTop = "1px solid #202a35";

        locationSection.innerHTML = `
            <div class="simulation-location-state">
                <span class="simulation-location-state-label">Location Permission</span>
                <span class="simulation-location-state-value" id="simulationLocationPermission">Not requested</span>
            </div>

            <div id="simulationLocationDetails" style="display:none;">
                <div class="simulation-evidence-grid" style="margin-bottom: 15px;">
                    <div class="simulation-evidence-item">
                        <div class="simulation-evidence-label">LATITUDE</div>
                        <div class="simulation-evidence-value monospace" id="simulationLatitude">—</div>
                    </div>
                    <div class="simulation-evidence-item">
                        <div class="simulation-evidence-label">LONGITUDE</div>
                        <div class="simulation-evidence-value monospace" id="simulationLongitude">—</div>
                    </div>
                    <div class="simulation-evidence-item">
                        <div class="simulation-evidence-label">ACCURACY</div>
                        <div class="simulation-evidence-value" id="simulationLocationAccuracy">—</div>
                    </div>
                    <div class="simulation-evidence-item">
                        <div class="simulation-evidence-label">SOURCE</div>
                        <div class="simulation-evidence-value" id="simulationLocationSource">—</div>
                    </div>
                </div>

                <div class="simulation-email-details" style="border-top: none; padding-top: 0;">
                    <div class="simulation-email-detail">
                        <span>Consent</span>
                        <strong id="simulationLocationConsent">—</strong>
                    </div>
                    <div class="simulation-email-detail">
                        <span>Location Timestamp</span>
                        <strong id="simulationLocationTimestamp">—</strong>
                    </div>
                </div>
            </div>
        `;
        evidenceContainer.appendChild(locationSection);
    }

    const permissionElement = document.getElementById("simulationLocationPermission");
    const details = document.getElementById("simulationLocationDetails");
    const location = interaction.location;

    if (!location) {
        permissionElement.textContent = "Not provided";
        permissionElement.classList.remove("granted");
        details.style.display = "none";
        return;
    }

    permissionElement.textContent = "Granted";
    permissionElement.classList.add("granted");
    details.style.display = "block";

    document.getElementById("simulationLatitude").textContent = formatCoordinate(location.latitude);
    document.getElementById("simulationLongitude").textContent = formatCoordinate(location.longitude);
    document.getElementById("simulationLocationAccuracy").textContent = location.accuracy_meters !== undefined ? "±" + location.accuracy_meters + " m" : "Unavailable";
    document.getElementById("simulationLocationSource").textContent = location.source || "Browser Geolocation";
    document.getElementById("simulationLocationConsent").textContent = location.consent || "Granted";
    document.getElementById("simulationLocationTimestamp").textContent = formatTimestamp(location.timestamp);
}

/*
 * UTILITY FUNCTIONS
 */

function formatCoordinate(value) {
    if (value === null || value === undefined || value === "") return "Unavailable";
    const number = Number(value);
    if (Number.isNaN(number)) return "Unavailable";
    return number.toFixed(6);
}

function formatTimestamp(timestamp) {
    if (!timestamp) return "Unavailable";
    try {
        return new Date(timestamp).toLocaleString();
    } catch {
        return timestamp;
    }
}

async function copySimulationUrl() {
    const url = document.getElementById("simulationUrl").textContent;
    if (!url) return;

    try {
        await navigator.clipboard.writeText(url);
        const button = document.getElementById("copySimulationButton");
        const originalText = button.textContent;
        button.textContent = "Copied";
        setTimeout(() => { button.textContent = originalText; }, 1500);
    } catch (error) {
        console.error(error);
        alert("Unable to copy the simulation URL.");
    }
}

function isSafeUrl(url) {
    try {
        const parsed = new URL(url);
        return (parsed.protocol === "http:" || parsed.protocol === "https:");
    } catch {
        return false;
    }
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/*
 * EVENT LISTENERS
 */

document.getElementById("scanButton").addEventListener("click", startScan);

document.getElementById("emailInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        startScan();
    }
});

document.getElementById("createSimulationButton").addEventListener("click", createActiveSimulation);
document.getElementById("copySimulationButton").addEventListener("click", copySimulationUrl);