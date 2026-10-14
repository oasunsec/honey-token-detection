# Cost and teardown

The Azure run used billable ACR, Container Apps, Table Storage, and Log Analytics resources in `rg-canary-cloudsec-validation`. I did not measure the cost, and I did not tear down the resource group during the run.

## Cleanup command

Review the resource group and export anything you need before running this:

```powershell
.\scripts\azure\destroy.ps1 -ResourceGroup rg-canary-cloudsec-validation -Confirm
```

The script requires `-Confirm` and checks whether the group remains. It removes the deployed resources but does not remove separately saved evidence. Test tokens were revoked, and the temporary operator role was removed after validation.
