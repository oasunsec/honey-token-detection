# Security notes

This repository is intended for authorized defensive-security testing and deception controls.

- Use synthetic decoy content only. Do not place real payroll, customer, financial, or authentication data inside bait files.
- A callback source IP may represent a NAT gateway, VPN, proxy, DNS resolver, email-security scanner, or sandbox. Do not use it alone to identify a person.
- Callback-based tokens can fail when a host is offline, air-gapped, in Protected View, or configured to block external content.
- Set `CANARY_MANAGEMENT_API_KEY` before exposing the management API beyond a lab network. Without a key, management routes accept loopback clients only; the callback route remains public by design.
- Terminate TLS in front of the service for non-local deployments.
- Decoy filenames are restricted to plain file names so a malformed management request cannot escape the selected output directory. Keep the output directory itself controlled and writable only by the service account.
- Keep secrets out of source control.
- Alert failures are recorded on the event with a bounded error string, but the event store is not tamper-evident and should be protected and retained according to deployment policy.

Report defects privately to the repository owner before public disclosure.


## Azure receiver controls

The Azure deployment uses a user-assigned managed identity. The identity is granted only `AcrPull` on the project registry, `Storage Table Data Contributor` on the project storage account, and `Monitoring Metrics Publisher` on the project Data Collection Rule. Storage shared-key access and ACR admin credentials are disabled.

The public Container App runs with `CANARY_RECEIVER_ONLY=true`: health and callback routes remain available, while management routes return 404. Provisioning and token lifecycle actions stay in the local operator process. The callback persists the event in Azure Table Storage before attempting Logs Ingestion, and a DCR failure is recorded as `sentinel_status=failed` without discarding the durable event.

The DCR payload excludes the raw callback token and request path. It carries a short SHA-256 canary identifier, artifact name, source metadata, triage classification, duplicate decision, alert outcome, and event ID. Raw tokens and raw evidence must remain in ignored, access-controlled local storage.

The Sentinel rule is scheduled and creates an incident for `CanaryHit_CL` canary-trigger rows. This is detection plumbing; it does not establish user identity, prove a human opened the document, or replace endpoint and identity telemetry.

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
