param([string]$ResourceGroup = 'rg-canary-cloudsec-validation', [switch]$Confirm)
$ErrorActionPreference = 'Stop'
if (-not $Confirm) { throw 'Refusing teardown without -Confirm. Verify evidence and unrelated-resource boundary first.' }
$exists = az group exists --name $ResourceGroup
if ($exists -ne 'true') { Write-Host "Resource group $ResourceGroup is already absent."; exit 0 }
$resources = az resource list --resource-group $ResourceGroup --query '[].{name:name,type:type}' --output json
Write-Host 'Resources scheduled for deletion:'
$resources
az group delete --name $ResourceGroup --yes --no-wait false
if ((az group exists --name $ResourceGroup) -eq 'true') { throw 'Resource group still exists after teardown.' }
Write-Host "Deleted dedicated resource group $ResourceGroup."
