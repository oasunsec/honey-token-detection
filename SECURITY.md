# Security controls implemented

Examples use synthetic decoy documents in controlled test systems. The published evidence removes raw tokens, account details, source IPs, tenant and subscription identifiers, and private paths.

## Azure receiver controls

The deployed receiver uses a user-assigned managed identity with only `AcrPull` on the registry, `Storage Table Data Contributor` on the storage account, and `Monitoring Metrics Publisher` on the Data Collection Rule. Storage shared-key access and ACR admin credentials are disabled.

The public Container App runs with `CANARY_RECEIVER_ONLY=true`. Health and callback routes stay available; management routes return 404. Provisioning and token lifecycle actions remain in the local operator process.

The callback writes to Azure Table Storage before Logs Ingestion. A DCR failure becomes `sentinel_status=failed` while the durable event remains available for diagnosis.

The DCR payload removes the raw callback token and request path. It carries a short SHA-256 identifier, artifact name, source metadata, triage classification, duplicate decision, alert outcome, and event ID. Raw tokens and raw evidence stay in ignored, access-controlled local storage.

The Sentinel rule creates an incident from `CanaryHit_CL` rows. Its query and severity behavior are recorded in [SENTINEL.md](SENTINEL.md).

## Deployment boundaries

The deployed receiver does not expose management routes. A local-only management fallback is safe only when the process is bound to a trusted loopback interface; remote use requires `CANARY_MANAGEMENT_API_KEY` and TLS at a trusted proxy.

Forwarded-header trust is disabled by default. Enable it only behind a proxy that replaces client-supplied forwarding headers.

The Docker build context allowlists application Python files, requirements, and the Dockerfile. Compose binds to loopback. Uvicorn access logs are disabled because callback paths contain live tokens; apply equivalent redaction at any proxy.

Report security defects privately to the repository owner.
