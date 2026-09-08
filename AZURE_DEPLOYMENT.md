# Azure deployment record

Deployed the receiver into `rg-canary-cloudsec-validation` in `southcentralus`. Bicep created the platform resources; `az acr build` built the image and the deployment script released a run-specific tag.

| Component | Deployed configuration |
| --- | --- |
| ACR | Basic tier; admin credentials disabled |
| Container Apps | Consumption environment, external HTTPS ingress, receiver-only mode |
| Table Storage | Standard LRS; `CanaryHits` and `NotificationOutbox`; shared keys disabled |
| Managed identity | Scoped ACR pull, Table data, and DCR ingestion roles |
| Log Analytics | `CanaryHit_CL` custom table and Direct DCR |
| Sentinel | Scheduled rule with incident creation enabled |

The deployed `/health` endpoint returned 200 with `receiver_only=true` and `storage_backend=azure_table`. The public `/api/events` route returned 404. The temporary operator Table role used during provisioning was removed after inspection.

The first DCR hostname failed DNS resolution. The deployment was changed to use the `logsIngestion` endpoint returned by the deployed rule; subsequent records reached Log Analytics. The receiver used the Azure-provided HTTPS hostname.

[Deployment commands](docs/SETUP.md#azure-deployment) · [Sentinel outcome](SENTINEL.md) · [Teardown](COST_AND_TEARDOWN.md)

## Detection engineering upgrade

Release 0.2.2 extends the existing table and DCR schema, updates the original analytic resource to the High first-access rule, and adds the Medium scanner rule. No account-key authentication or broader runtime role was introduced. The receiver uses the DCR-provided Logs Ingestion endpoint and publishes its release identifier.

Source forwarding and Uvicorn proxy rewriting are disabled. SourceIp therefore records the connection peer and can represent ingress infrastructure. Repeat matching uses canary and UA, while incident grouping uses canary ID.

The [validation report](VALIDATION.md) records health checks, cloud callbacks, query execution, incidents, and the Word attempt. Baseline screenshots remain historical records of the original configuration.
