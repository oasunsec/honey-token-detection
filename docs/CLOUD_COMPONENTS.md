# Cloud components (release 0.2.2)

| Work item | What changed |
| --- | --- |
| Packaged the receiver | Built the existing Dockerfile through ACR |
| Deployed HTTPS collection | Ran the receiver in Container Apps with receiver-only mode; management and docs routes return 404 |
| Added durable cloud events | Stored callback observations and delivery outcomes in `CanaryHits`; the provisioned `NotificationOutbox` table remains unused |
| Removed runtime account keys | Used a user-assigned managed identity with scoped registry pull, Table Storage, and DCR ingestion roles |
| Added SIEM ingestion | Sent the redacted, structured event schema through a Direct DCR into `CanaryHit_CL` |
| Preserved source semantics | Forwarded headers are disabled; source IP is the direct connection peer |
| Added structured triage | Classified scanner-like User-Agents as Medium and retained configured severity for other first hits; repeat matching uses token and User-Agent |
| Added detection | Two scheduled KQL rules create High incidents for receiver high/critical first hits and Medium scanner incidents; repeat rows are excluded |
| Added cleanup tooling | Resource-group teardown script requires `-Confirm`; it was not run |

[Deployment record](../AZURE_DEPLOYMENT.md) · [Architecture](../ARCHITECTURE.md)
