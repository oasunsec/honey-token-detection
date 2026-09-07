param([string]$ResourceGroup = 'rg-canary-cloudsec-validation', [string]$ContainerAppName = 'canarysec-receiver')
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidence = Join-Path $repo 'evidence-private'
New-Item -ItemType Directory -Force $evidence | Out-Null
$fqdn = az containerapp show --resource-group $ResourceGroup --name $ContainerAppName --query properties.configuration.ingress.fqdn --output tsv
Invoke-WebRequest -UseBasicParsing "https://$fqdn/health" | Select-Object StatusCode,Content | ConvertTo-Json | Set-Content (Join-Path $evidence '09-container-app-health.json')
Write-Host "Receiver: https://$fqdn"
