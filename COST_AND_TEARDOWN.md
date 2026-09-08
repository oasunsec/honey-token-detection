# Resource lifecycle

The run created billable ACR, Container Apps, Storage, and Log Analytics resources in a dedicated resource group. No cost measurement was captured, and teardown was not run during the recorded work.

A cleanup script is present for `rg-canary-cloudsec-validation`. It requires `-Confirm`, requests deletion of the named group, and checks whether the group remains. Saved event and incident records are separate from the deployed resources.

## Cleanup command

Run this only after reviewing the resource group and exporting any records to retain:

```powershell
.\scripts\azure\destroy.ps1 -ResourceGroup rg-canary-cloudsec-validation -Confirm
```

The detection upgrade reused the same resource group and added a second scheduled rule. Builds, callbacks, ingestion, and scheduled queries can incur cost. No cost measurement was taken and resources were not torn down. All nine upgrade test tokens were revoked and the temporary table-scoped operator role was removed after validation. Event records were retained. [Cleanup record](docs/evidence/public/upgrade/cleanup.json).
