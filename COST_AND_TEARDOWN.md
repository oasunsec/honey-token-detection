# Cost and teardown

The deployment creates billable Azure resources, including Basic ACR, Container Apps, Storage, and Log Analytics. Check the resource group in Azure Cost Management while the lab is running; no cost measurement was captured for this validation. Teardown has not been performed.

Before teardown, export the resource inventory, deployment outputs, KQL result, Sentinel alert/incident, email evidence, final security settings and cost view. Verify the resource group contains only this project. Then run:

```powershell
.\scripts\azure\destroy.ps1 -ResourceGroup rg-canary-cloudsec-validation -Confirm
```

The script refuses to run without `-Confirm`, deletes only the named project resource group, and verifies that the group is gone. Raw evidence remains outside Git; sanitized documentation and IaC remain redeployable.
