# Run Honey Token

Run these commands from the repository root. The local example uses synthetic documents and a loopback receiver.

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

Check:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok","receiver_only":false,"receiver_version":"local","storage_backend":"sqlite"}
```

### 4. Create a financial-document decoy

```bash
python -m app.cli create \
  --name "Finance bait" \
  --filename "Synthetic_Forecast.docx" \
  --format docx
```

The command returns a token ID, callback URL and generated decoy path.

### 5. Send a callback

Call the callback URL returned by the CLI:

```bash
curl -A "Lab-Validation" "http://127.0.0.1:8000/t/YOUR_TOKEN/pixel.gif" -o /dev/null
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

Open the generated file on a lab endpoint that can reach the callback server. Record whether the viewer actually requests the external resource. If it does not, treat that as an observed product-control limitation rather than trying to bypass the viewer's security controls.

## Azure deployment

The checked-in Azure path provisions a dedicated resource group with a Basic ACR, user-assigned managed identity, Consumption Container App, Standard LRS Table Storage, Log Analytics, a Direct Data Collection Rule and a Microsoft Sentinel scheduled rule. The receiver image is unchanged application code packaged in the existing `Dockerfile`; Azure switches only the storage and ingestion adapters through environment variables.

```powershell
.\scripts\azure\preflight.ps1
.\scripts\azure\deploy.ps1
.\scripts\azure\validate.ps1
```

The deployed receiver exposes `/health` and `/t/<token>/pixel.gif`. It returns 404 for `/api/*` so management operations stay local to an authenticated operator process. The runtime uses its managed identity for ACR pull, Azure Table Storage and Logs Ingestion. It does not use storage keys, registry admin credentials, or callback secrets in the container configuration. `CanaryHit_CL` receives only a hashed canary identifier and normalized event fields.

## Management API protection

The callback route stays public because the token is the tripwire identifier. Management routes under `/api/*` are limited to loopback clients when `CANARY_MANAGEMENT_API_KEY` is empty. Before remote use, set a strong value and send it as `X-Canary-API-Key`:

```text
CANARY_MANAGEMENT_API_KEY=use-a-secret-from-your-secret-store
```

```bash
curl -H "X-Canary-API-Key: $CANARY_MANAGEMENT_API_KEY" http://127.0.0.1:8000/api/events
```

Use TLS at a trusted reverse proxy for remote deployments. Never put the key in source control, a decoy, or a URL.

## Email alerts

The default alert mode is `console`. To use SMTP, configure environment variables based on `.env.example`:

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

An investigation can follow this sequence:

```text
Canary fires
   -> identify token/decoy
   -> determine source context
   -> correlate user + endpoint
   -> inspect file-access/DLP events
   -> scope related activity
   -> decide benign scanner vs suspicious access
   -> contain/escalate if supported by evidence
```

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

