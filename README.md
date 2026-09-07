# Canary Honeytoken MVP

A small self-hosted deception project for detecting interaction with sensitive-looking decoy files in an **authorized environment**.

The project creates a unique callback token, associates it with a decoy such as `Synthetic_Forecast.docx`, records callback telemetry, performs lightweight triage, suppresses duplicate notifications, and sends an alert to the console or email.

## What it is

```text
Decoy file
   |
   | external callback
   v
FastAPI token endpoint
   |
   +--> SQLite or Azure Table evidence
   |
   +--> Triage rule
   |
   +--> Console / email alert
```

This is a **detective deception control**. It does not replace encryption, access control, DLP, EDR, removable-media policy, or audit logging.

## Current MVP

- Unique cryptographically random token per decoy
- Public callback endpoint returning a transparent 1x1 GIF
- Token metadata stored in SQLite locally or Azure Table Storage in the receiver deployment
- HTML decoy generator
- DOCX decoy generator using an external image relationship
- Source IP, User-Agent, timestamp, token and filename logging
- Simple scanner-aware triage
- Five-minute duplicate notification suppression by default
- Console alerts by default
- SMTP email alerts as an option
- Token disable endpoint
- Event API for investigation
- Optional API-key protection for management endpoints, with loopback-only fallback
- Persisted alert outcome and delivery error evidence
- Automated tests
- Docker support

## Important limitation

A callback-based document token **does not guarantee detection of every file open**.

The callback may not fire when:

- the endpoint is offline or air-gapped;
- Microsoft Office or another viewer blocks external content;
- Protected View prevents the resource from loading;
- a proxy/firewall blocks the callback;
- the file is copied without being opened;
- the viewer does not support the external resource behavior.

Also, a source IP is not identity. It can belong to a proxy, VPN, NAT gateway, mail-security scanner, sandbox, or resolver. Correlate the event with identity, endpoint, file-audit, DLP and network telemetry before attribution.

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
uvicorn app.main:app --reload
```

Check:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

### 4. Create a financial-document decoy

```bash
python -m app.cli create \
  --name "Finance bait" \
  --filename "Synthetic_Forecast.docx" \
  --format docx
```

The command returns a token ID, callback URL and generated decoy path.

### 5. Validate the detector before opening the document

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

### Azure receiver validation

The checked-in Azure path provisions a dedicated resource group with a Basic ACR, user-assigned managed identity, Consumption Container App, Standard LRS Table Storage, Log Analytics, a Direct Data Collection Rule and a Microsoft Sentinel scheduled rule. The receiver image is unchanged application code packaged in the existing `Dockerfile`; Azure switches only the storage and ingestion adapters through environment variables.

```powershell
.\scripts\azure\preflight.ps1
.\scripts\azure\deploy.ps1
.\scripts\azure\validate.ps1
```

The deployed receiver exposes `/health` and `/t/<token>/pixel.gif`. It returns 404 for `/api/*` so management operations stay local to an authenticated operator process. The runtime uses its managed identity for ACR pull, Azure Table Storage and Logs Ingestion. It does not use storage keys, registry admin credentials, or callback secrets in the container configuration. `CanaryHit_CL` receives only a hashed canary identifier and normalized event fields.

### Management API protection

The callback route stays public because the token is the tripwire identifier. Management routes under `/api/*` are limited to loopback clients when `CANARY_MANAGEMENT_API_KEY` is empty. Before remote use, set a strong value and send it as `X-Canary-API-Key`:

```text
CANARY_MANAGEMENT_API_KEY=use-a-secret-from-your-secret-store
```

```bash
curl -H "X-Canary-API-Key: $CANARY_MANAGEMENT_API_KEY" http://127.0.0.1:8000/api/events
```

Use TLS at a trusted reverse proxy for remote deployments. Never put the key in source control, a decoy, or a URL.

### 6. Test the DOCX in a controlled lab

Open the generated file on a lab endpoint that can reach the callback server. Record whether the viewer actually requests the external resource. If it does not, treat that as an observed product-control limitation rather than trying to bypass the viewer's security controls.

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

The body includes the token, filename, timestamp, source IP, User-Agent, triage label and duplicate state. Each persisted event records `alert_status` as `sent`, `suppressed`, `disabled`, or `failed`; failed delivery includes a bounded error message for diagnosis.

## Triage logic

The MVP produces a structured event:

```json
{
  "event_type": "canary_trigger",
  "triage_label": "Honeytoken trigger - potential unauthorized access",
  "severity": "high"
}
```

A small scanner heuristic reduces obvious automated requests to `medium` severity. This is deliberately simple. A real environment should enrich the event with endpoint, identity and audit telemetry.

A useful production workflow is:

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

The test suite covers token triggering, duplicate suppression, scanner triage, token disabling, triage-derived console alerts, DOCX relationship generation and filename path validation.

## Suggested GitHub roadmap

### v0.1 — MVP
Current repository.

### v0.2 — Secure management plane
- SSO or a managed secret store for management credentials
- TLS deployment guidance
- role separation
- audit trail for token creation/disable actions

### v0.3 — Better triage
- trusted scanner allowlist
- source-network context
- token criticality
- enrichment adapters
- confidence score

### v0.4 — SOC integration
- Splunk HEC output
- Microsoft Sentinel/Log Analytics output
- generic webhook adapter
- normalized JSON schema

### v0.5 — Deception management
- multiple token types
- ownership/expiry
- bulk token generation
- token health testing
- dashboard

## What this project demonstrates

For a security-engineering portfolio, this repo shows:

- deception/honeytoken concepts;
- FastAPI service development;
- event normalization;
- basic detection/triage engineering;
- false-positive handling;
- alerting;
- security limitations and threat-model thinking;
- a path to SIEM integration.

## Authorized use only

Deploy decoys only in systems and networks you own or are authorized to monitor. Use synthetic bait data. Do not include real financial records, credentials or personal data in decoy documents.

## License

MIT
