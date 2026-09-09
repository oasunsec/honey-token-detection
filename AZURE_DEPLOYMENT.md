# Azure deployment

I deployed the receiver to `rg-canary-cloudsec-validation` in `southcentralus`.

| Resource | Use |
| --- | --- |
| Azure Container Registry | Builds and stores the image. Admin access is disabled. |
| Container Apps | Runs the receiver with public HTTPS ingress. |
| Table Storage | Stores `CanaryHits` and `NotificationOutbox`. |
| Managed identity | Pulls the image and writes to Table Storage and the DCR. |
| Log Analytics | Stores the `CanaryHit_CL` table. |
| Microsoft Sentinel | Runs the scheduled detection rules. |

## What worked

The deployed `/health` endpoint returned 200 with `receiver_only=true` and Azure Table Storage enabled. The public `/api/events` route returned 404. A controlled callback returned the GIF, saved a Table Storage event, reached Log Analytics, and produced a Sentinel incident.

## Problem found

The first DCR hostname did not resolve. I changed the receiver to use the `logsIngestion` endpoint from the deployed DCR. Later events reached `CanaryHit_CL`.

The app uses the Azure-provided HTTPS hostname. Forwarded headers and proxy rewriting are disabled, so the recorded source is the connection peer. Repeat matching uses the canary and User-Agent.

[Deployment commands](docs/SETUP.md#azure-deployment) - [Sentinel rules](SENTINEL.md) - [Validation](VALIDATION.md) - [Teardown](COST_AND_TEARDOWN.md)
