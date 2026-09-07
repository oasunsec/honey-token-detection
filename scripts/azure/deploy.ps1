param(
  [string]$ResourceGroup = 'rg-canary-cloudsec-validation',
  [string]$Location = 'southcentralus',
  [string]$ProjectPrefix = 'canarysec',
  [string]$ImageTag = 'validation-20260907',
  [switch]$SkipWhatIf
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidence = Join-Path $repo 'evidence-private'
New-Item -ItemType Directory -Force $evidence | Out-Null

az account show --output json | Out-Null
if ((az group exists --name $ResourceGroup) -ne 'true') {
  az group create --name $ResourceGroup --location $Location --tags Project=CanaryHoneytoken Environment=Validation ManagedBy=Bicep Purpose=CloudSecurityPortfolio --output none
}

$baseArgs = @('--resource-group', $ResourceGroup, '--template-file', (Join-Path $repo 'infra/main.bicep'), '--parameters', "location=$Location", "projectPrefix=$ProjectPrefix", 'deployContainerApp=false')
if (-not $SkipWhatIf) {
  az deployment group what-if @baseArgs --result-format ResourceIdOnly | Tee-Object (Join-Path $evidence '02-bicep-what-if.txt')
}
az deployment group create @baseArgs --name canary-base --output json | Tee-Object (Join-Path $evidence '03-bicep-base-deployment.json')

$outputs = az deployment group show --resource-group $ResourceGroup --name canary-base --query properties.outputs --output json | ConvertFrom-Json
$acrName = $outputs.registryName.value
$acrLoginServer = $outputs.registryLoginServer.value
az acr build --registry $acrName --image "receiver:$ImageTag" --file (Join-Path $repo 'Dockerfile') $repo --output none

$image = "$acrLoginServer/receiver:$ImageTag"
$finalArgs = @('--resource-group', $ResourceGroup, '--template-file', (Join-Path $repo 'infra/main.bicep'), '--parameters', "location=$Location", "projectPrefix=$ProjectPrefix", "containerImage=$image", 'deployContainerApp=true')
az deployment group create @finalArgs --name canary-final --output json | Tee-Object (Join-Path $evidence '03-bicep-final-deployment.json')
az containerapp show --resource-group $ResourceGroup --name $outputs.containerAppName.value --output json | Tee-Object (Join-Path $evidence '07-container-app-overview.json')
az acr repository show --name $acrName --image "receiver:$ImageTag" --output json | Tee-Object (Join-Path $evidence '04-container-image.json')

Write-Host "Deployed image: $image"
Write-Host "Resource group: $ResourceGroup"
