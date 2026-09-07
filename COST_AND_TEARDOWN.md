# Resource lifecycle

The deployment created billable ACR, Container Apps, Storage, and Log Analytics resources in the dedicated project resource group. No cost measurement was captured, and teardown was not performed during the recorded work.

A cleanup script was added for `rg-canary-cloudsec-validation`. It requires `-Confirm`, requests deletion of the named group, and checks whether the group remains. Saved event and incident records were retained separately from the deployed resources.

## Cleanup command

Run only after checking the named group's contents and exporting any records that need to be retained:

```powershell
.\scripts\azure\destroy.ps1 -ResourceGroup rg-canary-cloudsec-validation -Confirm
```
