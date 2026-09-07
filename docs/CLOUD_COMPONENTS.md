# Cloud components added

| Work item | What changed |
| --- | --- |
| Packaged the receiver | Built the existing Dockerfile through ACR |
| Deployed HTTPS collection | Ran the receiver in Container Apps with management routes disabled |
| Added durable cloud events | Stored hits and notification outcomes in Azure Table Storage |
| Removed runtime account keys | Used a managed identity with registry, table, and DCR roles |
| Added SIEM ingestion | Sent normalized events through a Direct DCR into `CanaryHit_CL` |
| Added detection | Scheduled KQL rule created a Sentinel incident |
| Added cleanup tooling | Resource-group teardown script requires `-Confirm`; it was not run |

[Deployment record](../AZURE_DEPLOYMENT.md) · [Architecture](../ARCHITECTURE.md)
