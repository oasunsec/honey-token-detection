param(
  [string]$ResourceGroup = 'rg-canary-cloudsec-validation',
  [string]$Location = 'southcentralus',
  [string]$ProjectPrefix = 'canarysec',
  [string]$ImageTag = '',
  [string]$ReceiverVersion = '0.2.2',
  [switch]$SkipWhatIf
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidence = Join-Path $repo 'evidence-private'
New-Item -ItemType Directory -Force $evidence | Out-Null
$runId = Get-Date -AsUTC -Format 'yyyyMMddTHHmmssfffZ'
$projectTagValue = 'CanaryHoneytoken'
if ([string]::IsNullOrWhiteSpace($ImageTag)) {
  $ImageTag = "validation-$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))"
}

function Invoke-AzPrivate {
  param(
    [Parameter(Mandatory)] [string]$EvidenceName,
    [Parameter(Mandatory)] [string[]]$Arguments
  )
  $path = Join-Path $evidence "$runId-$EvidenceName"
  $errorPath = Join-Path $evidence "$runId-$EvidenceName.stderr.txt"
  $result = @(& az @Arguments 2> $errorPath)
  $exitCode = $LASTEXITCODE
  $result | Out-File -LiteralPath $path -Encoding utf8
  if ($exitCode -ne 0) {
    throw "Azure CLI command failed (exit code $exitCode). See private evidence: $path and $errorPath"
  }
  return ($result -join [Environment]::NewLine)
}

$null = Invoke-AzPrivate '01-account-show.json' @('account', 'show', '--output', 'json')
$groupExists = (Invoke-AzPrivate '02-group-exists.txt' @('group', 'exists', '--name', $ResourceGroup, '--output', 'tsv')).Trim()
if ($groupExists -ne 'true') {
  $null = Invoke-AzPrivate '03-group-create.json' @('group', 'create', '--name', $ResourceGroup, '--location', $Location, '--tags', "Project=$projectTagValue", 'Environment=Validation', 'ManagedBy=Bicep', 'Purpose=CloudSecurityPortfolio', '--output', 'json')
}

$baseArgs = @('--resource-group', $ResourceGroup, '--template-file', (Join-Path $repo 'infra/main.bicep'), '--parameters', "location=$Location", "projectPrefix=$ProjectPrefix", "receiverVersion=$ReceiverVersion", 'deployContainerApp=false')
if (-not $SkipWhatIf) {
  $null = Invoke-AzPrivate '04-bicep-what-if.txt' (@('deployment', 'group', 'what-if') + $baseArgs + @('--result-format', 'ResourceIdOnly'))
}
$null = Invoke-AzPrivate '05-bicep-base-deployment.json' (@('deployment', 'group', 'create') + $baseArgs + @('--name', 'canary-base', '--output', 'json'))

$outputsJson = Invoke-AzPrivate '06-bicep-base-outputs.json' @('deployment', 'group', 'show', '--resource-group', $ResourceGroup, '--name', 'canary-base', '--query', 'properties.outputs', '--output', 'json')
$outputs = $outputsJson | ConvertFrom-Json
$acrName = $outputs.registryName.value
$acrLoginServer = $outputs.registryLoginServer.value
$null = Invoke-AzPrivate '07-acr-build.json' @('acr', 'build', '--registry', $acrName, '--image', "receiver:$ImageTag", '--file', (Join-Path $repo 'Dockerfile'), $repo, '--no-logs', '--output', 'json')

$image = "$acrLoginServer/receiver:$ImageTag"
$finalArgs = @('--resource-group', $ResourceGroup, '--template-file', (Join-Path $repo 'infra/main.bicep'), '--parameters', "location=$Location", "projectPrefix=$ProjectPrefix", "receiverVersion=$ReceiverVersion", "containerImage=$image", 'deployContainerApp=true')
$null = Invoke-AzPrivate '08-bicep-final-deployment.json' (@('deployment', 'group', 'create') + $finalArgs + @('--name', 'canary-final', '--output', 'json'))
$appName = "$ProjectPrefix-receiver"
$null = Invoke-AzPrivate '09-container-app-overview.json' @('containerapp', 'show', '--resource-group', $ResourceGroup, '--name', $appName, '--output', 'json')
$null = Invoke-AzPrivate '10-container-image.json' @('acr', 'repository', 'show', '--name', $acrName, '--image', "receiver:$ImageTag", '--output', 'json')

Write-Host "Azure deployment completed. Private evidence was saved under evidence-private."
