# Cost and teardown

The project uses one dedicated resource group. Container Apps consumption, Table Storage, Logs Ingestion and Log Analytics usage are consumption based; the Log Analytics workspace and Container Apps environment are the likely standing-cost contributors during a live validation. Basic ACR and Standard LRS storage avoid premium SKUs.

Before teardown, export the resource inventory, deployment outputs, KQL result, Sentinel alert/incident, email evidence, final security settings and cost view. Verify the resource group contains only this project. Then run:

```powershell
.\scripts\azure\destroy.ps1 -ResourceGroup rg-canary-cloudsec-validation -Confirm
```

The script refuses to run without `-Confirm`, deletes only the named project resource group, and verifies that the group is gone. Raw evidence remains outside Git; sanitized documentation and IaC remain redeployable.
