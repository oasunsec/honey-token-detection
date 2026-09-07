# Azure deployment record

Deployed the receiver into `rg-canary-cloudsec-validation` in `southcentralus`. Bicep created the platform resources first; the deployment script built the Docker image with `az acr build`, then deployed the receiver using a run-specific image tag.

| Component | Configuration deployed |
| --- | --- |
| ACR | Basic tier; admin credentials disabled |
| Container Apps | Consumption environment, external HTTPS ingress, receiver-only mode |
| Table Storage | Standard LRS; `CanaryHits` and `NotificationOutbox`; shared keys disabled |
| Managed identity | Scoped ACR pull, Table data, and DCR ingestion roles |
| Log Analytics | `CanaryHit_CL` custom table and Direct DCR |
| Sentinel | Scheduled rule with incident creation enabled |

The receiver's health endpoint returned 200 with `receiver_only=true` and `storage_backend=azure_table`. The public `/api/events` route returned 404. The temporary operator Table role used during provisioning was removed after inspection; the remaining count for that temporary operator assignment was zero.

The first DCR endpoint failed DNS resolution. The Bicep output was changed to use the deployed rule's `logsIngestion` endpoint, and subsequent records reached Log Analytics. The deployment used the Azure-provided HTTPS hostname. [Operational limits](LIMITATIONS.md) records the ingress scope.

[Deployment commands](docs/SETUP.md#azure-deployment) · [Sentinel outcome](SENTINEL.md) · [Teardown](COST_AND_TEARDOWN.md)
