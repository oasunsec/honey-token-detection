# Security controls

The receiver uses synthetic documents and publishes redacted evidence. Callback tokens, account identifiers, real email addresses, and private paths remain outside the public package.

## Receiver and identity

Receiver-only mode returns 404 for management, docs, and OpenAPI. Local management requires a key when configured; the no-key fallback accepts loopback connections only. Provisioning uses an operator process rather than a public endpoint.

The managed identity has `AcrPull` on its registry, `Storage Table Data Contributor` on the storage account, and `Monitoring Metrics Publisher` on the DCR. The Table role is account-scoped because the backend initializes two tables at startup. Narrowing it requires removing table creation from runtime and migrating the assignments; no role was broadened for this release. The outbox is provisioned but unused. Registry admin access and storage shared-key access are disabled. Ingress requires HTTPS.

Observations persist before triage and delivery. SMTP and ingestion failures have independent statuses. SMTP STARTTLS verifies server certificates and hostnames. Loopback sink tests disable TLS only for the local test connection.

Diagnostics retain exception categories and numeric HTTP/SMTP status codes when available, excluding arbitrary SDK messages that can contain secrets or response bodies. Event API responses replace all nonempty error text with a redacted marker, including historical error messages. The private database retains operator diagnostics. A failed status write can remain pending; the other delivery path is still attempted.

## Callback privacy

Tokens are random, secret-like callback identifiers. Anyone holding one can trigger it. They remain in the decoy relationship and private token store, so protect both and revoke tokens after use.

Uvicorn access logging is disabled in Docker and documented local commands. Stored event paths are redacted. Event API output and SIEM payloads exclude raw tokens, including an exact token echoed through User-Agent. Alerts include a hashed identifier and triage context. No request headers or SDK diagnostic bodies are sent wholesale to Log Analytics.

Ingress, TLS inspection, endpoint telemetry, document caches, backups, and third-party scanners may observe callback URLs. This project cannot guarantee redaction in those external systems. Review their logging/retention controls and keep raw evidence private. Management token provisioning intentionally returns the callback secret to the authenticated operator; the event API does not.

## Source IP trust

Forwarded-header trust is disabled by default in the application and Bicep. Docker also passes `--no-proxy-headers` to Uvicorn so server middleware cannot silently rewrite `request.client`. The safe default records the socket peer, which can be the Container Apps proxy.

Enable application forwarding only behind an ingress that overwrites client-supplied headers and prevents bypass. Trusting the first arbitrary `X-Forwarded-For` value lets a requester invent SourceIp and mislead investigation. This release does not assume that overwrite contract.

An IP never identifies a person by itself. NAT, VPNs, proxies, scanners, and gateways require endpoint, identity, DLP, and file-audit correlation. A callback alone proves neither attribution nor exfiltration.

## Repository controls

The Docker build context allowlists application files. Compose binds to loopback. Environment files, databases, logs, generated decoys, deployment responses, and private evidence are ignored. The full reachable history is scanned with Gitleaks before release. [Validation](VALIDATION.md) records the result and remaining limits.

Report security defects privately to the repository owner.
