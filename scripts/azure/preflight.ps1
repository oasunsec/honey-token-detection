param(
  [string]$ResourceGroup = 'rg-canary-cloudsec-validation',
  [string]$Location = 'southcentralus'
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidence = Join-Path $repo 'evidence-private'
New-Item -ItemType Directory -Force $evidence | Out-Null

az account show --output json | Set-Content (Join-Path $evidence '00-azure-start-state.json')
$groups = az group list --query '[].{name:name,location:location,tags:tags}' --output json
$groups | Set-Content (Join-Path $evidence '00-resource-groups.json')

foreach ($provider in @('Microsoft.App','Microsoft.ContainerRegistry','Microsoft.OperationalInsights','Microsoft.Insights','Microsoft.SecurityInsights','Microsoft.OperationsManagement')) {
  $state = az provider show --namespace $provider --query registrationState --output tsv
  Write-Host "${provider}: $state"
}

$existing = az group exists --name $ResourceGroup
Write-Host "Dedicated resource group exists: $existing"
Write-Host "Preflight evidence written under evidence-private (ignored by Git)."
