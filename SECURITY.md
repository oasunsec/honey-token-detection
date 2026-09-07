# Security controls implemented

The work used synthetic decoy documents. Callback telemetry was collected in the authorized lab; raw tokens and identifying account details were excluded from the screenshot package.

## Azure receiver controls

The Azure deployment uses a user-assigned managed identity. The identity is granted only `AcrPull` on the project registry, `Storage Table Data Contributor` on the project storage account, and `Monitoring Metrics Publisher` on the project Data Collection Rule. Storage shared-key access and ACR admin credentials are disabled.

The public Container App runs with `CANARY_RECEIVER_ONLY=true`: health and callback routes remain available, while management routes return 404. Provisioning and token lifecycle actions stay in the local operator process. The callback persists the event in Azure Table Storage before attempting Logs Ingestion, and a DCR failure is recorded as `sentinel_status=failed` without discarding the durable event.

The DCR payload excludes the raw callback token and request path. It carries a short SHA-256 canary identifier, artifact name, source metadata, triage classification, duplicate decision, alert outcome, and event ID. Raw tokens and raw evidence must remain in ignored, access-controlled local storage.

The Sentinel rule is scheduled and creates an incident for `CanaryHit_CL` canary-trigger rows. The recorded incident did not establish user identity or document exfiltration.

## Deployment requirements

Production operations require deployment-specific ingress rate limits, retention, monitoring
of failed delivery, and identity correlation. Do not expose local management
through a loopback reverse proxy without an API key: the local-only fallback
identifies the immediate peer. Only enable forwarded-header trust behind an
explicitly trusted proxy that replaces client-supplied forwarding headers.

Docker build context is allowlisted to application Python files, requirements,
and the Dockerfile. Compose binds to loopback. The container disables Uvicorn
access logs because callback paths carry live tokens; apply equivalent redaction
at any proxy. Live tokens in ignored private evidence must never be published.

Report security defects privately to the repository owner.
