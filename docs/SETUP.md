# Run Honey Token

Run these commands from the repository root. The local example uses synthetic documents and a loopback receiver. In Windows PowerShell, use `curl.exe` wherever the Bash examples use `curl`.

## Requirements

- Python 3.12 or 3.13 with `pip` and `venv`. CI runs on 3.12; the recorded local run used 3.13.
- Microsoft Word for the document-open test. The receiver and automated tests can run without Word.
- For Azure deployment: PowerShell, Azure CLI, and an account permitted to create the project resources and role assignments.
- Docker with Compose only for the container option.

Get the source and enter the repository before continuing:

```text
git clone https://github.com/oasunsec/canary-honeytoken-detection.git
cd canary-honeytoken-detection
```

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the API

```bash
uvicorn app.main:app --reload --no-access-log
```

Leave the API running. Open a second terminal in the repository root and activate the same virtual environment for the remaining commands.

Check:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","receiver_only":false,"receiver_version":"local","storage_backend":"sqlite"}
```

### 4. Create a financial-document decoy

```text
python -m app.cli create --name "Finance bait" --filename "Synthetic_Forecast.docx" --format docx
```

The command writes the document under `decoys/` and returns its path, token ID, and callback URL. The CLI uses the configured database directly; it does not call the management API.

### 5. Send a callback

Call the callback URL returned by the CLI:

```bash
curl -A "Lab-Validation" "http://127.0.0.1:8000/t/YOUR_TOKEN/pixel.gif" --output pixel.gif
```

You should see a console alert and an event in:

```text
GET /api/events
```

Open interactive API docs at:

```text
http://127.0.0.1:8000/docs
```

### 6. Open the document

Open the generated file on the same machine as the loopback receiver. If the viewer loads external content, its pixel request will appear in `/api/events`. Viewer coverage is recorded in [COMPATIBILITY.md](../COMPATIBILITY.md). Leave Office and endpoint security policies in place.

## Azure deployment

Install Azure CLI, sign in, and select the intended subscription before running the scripts:

```powershell
az login
az account set --subscription '<subscription name or id>'
.\scripts\azure\preflight.ps1
.\scripts\azure\deploy.ps1
.\scripts\azure\validate.ps1
```

The scripts create billable resources. [AZURE_DEPLOYMENT.md](../AZURE_DEPLOYMENT.md) records the deployed components; [COST_AND_TEARDOWN.md](../COST_AND_TEARDOWN.md) contains the cleanup command. The Azure receiver exposes health and callback routes; management operations remain local.

## Management API protection

The callback route stays public so document viewers can request it. Management routes under `/api/*` are limited to loopback clients when `CANARY_MANAGEMENT_API_KEY` is empty. Before remote use, set a strong value and send it as `X-Canary-API-Key`:

```text
CANARY_MANAGEMENT_API_KEY=use-a-secret-from-your-secret-store
```

Bash:

```bash
curl -H "X-Canary-API-Key: $CANARY_MANAGEMENT_API_KEY" http://127.0.0.1:8000/api/events
```

PowerShell:

```powershell
curl.exe -H "X-Canary-API-Key: $env:CANARY_MANAGEMENT_API_KEY" http://127.0.0.1:8000/api/events
```

Use TLS at a trusted reverse proxy for remote deployments. Never put the key in source control, a decoy, or a URL.

## Email alerts

The default alert mode is `console`. To use SMTP, set the process environment variables listed in `.env.example` before starting the API. The application reads the process environment; creating a `.env` file alone does not load these values:

```text
CANARY_ALERT_MODE=email
CANARY_ALERT_TO=security@example.com
CANARY_SMTP_HOST=smtp.example.com
CANARY_SMTP_PORT=587
CANARY_SMTP_USER=...
CANARY_SMTP_PASSWORD=...
CANARY_SMTP_FROM=canary-alerts@example.com
CANARY_SMTP_STARTTLS=true
```

Do not commit credentials to Git.

Example email subject:

```text
[CANARY] Synthetic_Forecast.docx triggered (HIGH)
```

The body includes a short hashed canary identifier, filename, timestamp, source IP, User-Agent, triage label and duplicate state. The raw callback token is not placed in the alert body. Each persisted event records `alert_status` as `sent`, `suppressed`, `disabled`, or `failed`; failed delivery includes a bounded error message for diagnosis.

## Triage logic

Each callback produces a structured event:

```json
{
  "event_type": "canary_trigger",
  "triage_label": "Honeytoken trigger - potential unauthorized access",
  "severity": "high"
}
```

A small scanner heuristic reduces obvious automated requests to `medium` severity. Correlate these events with endpoint, identity, and audit telemetry during investigation.

## API

### Create token

```http
POST /api/tokens
Content-Type: application/json

{
  "name": "Finance bait",
  "filename": "Synthetic_Forecast.docx",
  "severity": "high",
  "notes": "Placed in authorized finance deception lab"
}
```

### Generate decoy

```http
POST /api/decoys
Content-Type: application/json

{
  "token_id": "TOKEN_ID",
  "format": "docx",
  "output_dir": "decoys"
}
```

### List events

```http
GET /api/events
```

When management authentication is enabled, include `X-Canary-API-Key` on every `/api/*` request.

### Disable token

```http
POST /api/tokens/TOKEN_ID/disable
```

## Docker

```bash
docker compose up --build
```

Then use `http://localhost:8000`.

## Testing

```bash
pytest -q
```

The 16 tests cover callbacks, duplicate suppression, scanner triage, token disabling, management authentication, receiver routing, DOCX generation, filename validation, event redaction, local SMTP delivery, and delivery-failure isolation.

