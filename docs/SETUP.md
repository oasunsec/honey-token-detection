# Run locally (release 0.2.2)

Run these commands from the repository root. The local walkthrough uses synthetic documents and a loopback receiver. In Windows PowerShell, use `curl.exe` where the Bash examples use `curl`.

## Requirements

- Python 3.12 or 3.13 with `pip` and `venv`. CI uses 3.12; the documented local verification used 3.13.
- Microsoft Word for the document-open test. The receiver and automated tests can run without Word.
- For Azure deployment: PowerShell, Azure CLI, and an account permitted to create the project resources and role assignments.
- Docker with Compose only for the container option.

Get the source and enter the repository before continuing:

```text
git clone https://github.com/oasunsec/honey-token-detection.git
cd honey-token-detection
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
uvicorn app.main:app --reload --no-access-log --no-proxy-headers
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

### 4. Create a synthetic DOCX decoy

```text
python -m app.cli create --name "Synthetic forecast" --filename "Synthetic_Forecast.docx" --format docx
```

The command writes the document under `decoys/` and returns its path, token ID, and callback URL. The CLI uses the configured database directly; it does not call the management API.

### 5. Send a callback

Call the callback URL returned by the CLI:

```bash
curl -A "HoneyToken-Demo" "http://127.0.0.1:8000/t/YOUR_TOKEN/pixel.gif" --output pixel.gif
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

Open the generated file on the machine running the receiver. If the viewer loads external content, its pixel request will appear in `/api/events`. Viewer behavior varies with Office and endpoint policies; see [COMPATIBILITY.md](../COMPATIBILITY.md) for the tested paths.

## Azure deployment

Install Azure CLI, sign in, and select the intended subscription before running the scripts:

```powershell
az login
az account set --subscription '<subscription name or id>'
.\scripts\azure\preflight.ps1
.\scripts\azure\deploy.ps1
.\scripts\azure\validate.ps1
```

The scripts create billable resources. [AZURE_DEPLOYMENT.md](../AZURE_DEPLOYMENT.md) records the deployed components; [COST_AND_TEARDOWN.md](../COST_AND_TEARDOWN.md) contains the cleanup command. The Azure receiver runs in receiver-only mode: `/health` and callback routes are exposed, while management and interactive documentation routes return `404`. Create tokens and decoys through the local management API or CLI before deployment.

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

The body includes a short hashed canary identifier, filename, timestamp, source IP, User-Agent, triage label and duplicate state. The raw callback token is not placed in the alert body. Each persisted event records `alert_status` as `sent`, `suppressed`, `disabled`, or `failed`; failed delivery records an exception category and numeric status where available.

## Triage logic

Each callback produces a structured event:

```json
{
  "event_type": "canary_trigger",
  "classification": "honeytoken_access",
  "is_scanner": false,
  "first_hit": true,
  "repeat_count": 0,
  "severity": "high",
  "recommended_action": "investigate"
}
```

Requests whose User-Agent matches the scanner or command-line markers are classified as `automated_scanner` with `medium` severity; other requests retain the token's configured severity. Repeat suppression matches the token and User-Agent within the configured deduplication window (five minutes by default), and records `first_hit` and `repeat_count`. Source forwarding headers are ignored by default (`CANARY_TRUST_PROXY_HEADERS=false`), so the recorded source is the direct connection peer. Correlate events with endpoint, identity, and audit telemetry during investigation.

The cloud deployment carries release identifier `0.2.2` into the normalized event schema. Sentinel has two scheduled rules: High or Critical non-scanner first hits, and Medium scanner first hits. Repeat rows remain searchable but do not create notification or analytic-rule alerts.

## API

### Create token

```http
POST /api/tokens
Content-Type: application/json

{
  "name": "Synthetic forecast",
  "filename": "Synthetic_Forecast.docx",
  "severity": "high",
  "notes": "Synthetic forecast document"
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

The tests cover callbacks, duplicate suppression, scanner triage, token disabling, management authentication, receiver routing, DOCX generation, filename validation, event redaction, local SMTP delivery, and delivery-failure isolation.

