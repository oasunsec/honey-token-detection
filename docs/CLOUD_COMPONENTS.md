# Cloud components added

| Work item | Implementation |
| --- | --- |
| Packaged the receiver | Existing Dockerfile built through ACR |
| Deployed HTTPS collection | Container Apps with management routes disabled |
| Added durable cloud events | Azure Table backend for hits and notification outcomes |
| Removed runtime account keys | Managed identity with registry, table, and DCR roles |
| Added SIEM ingestion | Direct DCR and `CanaryHit_CL` schema |
| Added detection | Scheduled KQL rule that produced a Sentinel incident |
| Added cleanup tooling | Resource-group teardown script requiring `-Confirm`; not executed |

[Deployment record](../AZURE_DEPLOYMENT.md) · [Architecture](../ARCHITECTURE.md)
