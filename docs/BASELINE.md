# Baseline: Azure/Sentinel validation branch

Captured: 2026-09-07 (America/Chicago)
Branch: `feature/azure-sentinel-validation`
Remote: private GitHub repository `oasunsec/canary-honeytoken-detection`

## Existing architecture

The FastAPI service stores token metadata and callback events in SQLite. Management routes create tokens, list tokens/events, disable tokens, and generate HTML/DOCX decoys. The public callback route validates an active token, captures request metadata, classifies scanner-like user agents, suppresses duplicate alerts inside a configurable window, persists the event, then sends a console or SMTP alert based on the triage result. The DOCX generator embeds a unique external image relationship that points to the callback URL.

## Working features

- Unique token creation and disable/revocation.
- DOCX and HTML decoy generation.
- Callback response is a transparent GIF suitable for the existing DOCX relationship.
- Event persistence before notification delivery.
- Scanner classification and duplicate suppression.
- Management API key protection when configured, loopback-only fallback otherwise.
- Console and SMTP alert rendering with triage context.
- Docker image and GitHub Actions test workflow.

## Baseline verification

- `\.venv\\Scripts\\pytest.exe -q`: **9 passed**, 2 dependency deprecation warnings.
- `\.venv\\Scripts\\python.exe -m compileall -q app tests`: **passed**.
- Existing GitHub `main` is clean and synchronized with the private remote at the baseline commit.
- Azure CLI `2.89.1` is authenticated to the enabled PAYG subscription. Subscription and tenant identifiers are intentionally not repeated in repository evidence.
- Existing Azure resource groups are training projects; none is used as the canary validation boundary.
- Preflight provider state on 2026-09-07: `Microsoft.OperationalInsights` and `Microsoft.Insights` registered; `Microsoft.App`, `Microsoft.ContainerRegistry`, and `Microsoft.SecurityInsights` not registered.

## Current limitations

- SQLite is local-only and not durable across Container App restarts.
- The callback is a public detection receiver; it must not expose management routes in Azure.
- Azure Monitor/Sentinel ingestion is not present in the baseline.
- Word/Protected View and remote endpoint behavior depend on viewer and network policy and require controlled manual testing.
- No claim is made that a callback proves a person read the document or identifies an attacker.

## Azure changes required

- Add an optional Azure Table Storage backend using `DefaultAzureCredential`.
- Add receiver-only runtime boundary and managed-identity Azure Monitor ingestion.
- Add Bicep and deployment/validation/teardown scripts for a dedicated project resource group.
- Add DCR/table/KQL/Sentinel definitions and sanitized evidence documentation.
- Keep SQLite, local management APIs, current DOCX behavior, console/SMTP alerting, and existing test flow working locally.

## Explicitly unchanged

- DOCX remains the only supported canary artifact for this release.
- No exploit delivery, credential theft, persistence, evasion, endpoint-security bypass, or document-security bypass features.
- No AKS, queueing platform, premium database, custom domain, public management API, or unnecessary service sprawl.
