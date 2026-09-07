# Azure deployment

The temporary validation environment is scoped to `rg-canary-cloudsec-validation` in `southcentralus`. The deployment uses a Basic Azure Container Registry, a user-assigned managed identity, a Consumption Container Apps environment and one small external HTTPS Container App, a Standard LRS StorageV2 account with `CanaryHits` and `NotificationOutbox` tables, a Log Analytics workspace, a custom `CanaryHit_CL` table, a Direct DCR, and Microsoft Sentinel onboarding.

The first deployment creates the registry and platform resources. `scripts/azure/deploy.ps1` then builds the existing Docker image with `az acr build` and performs a second deployment with an immutable validation tag. The Container App pulls from ACR using the managed identity; no registry admin credential is enabled.

```powershell
az login
az account set --subscription '<subscription name or id>'
.\scripts\azure\preflight.ps1
.\scripts\azure\deploy.ps1
.\scripts\azure\validate.ps1
```

The app is receiver-only in Azure: `/health` and `/t/<secret>/pixel.gif` are needed for detection; `/api/*` returns 404. The generated Azure HTTPS FQDN is the only callback host. No custom domain, WAF, gateway, VM or private endpoint is required.

The app uses `DefaultAzureCredential`. The runtime identity receives `AcrPull` on the project registry, `Storage Table Data Contributor` on the project storage account, and `Monitoring Metrics Publisher` on the project DCR. These role assignments are deployment-time permissions and are not application credentials.
