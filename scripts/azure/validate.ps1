param([string]$ResourceGroup = 'rg-canary-cloudsec-validation', [string]$ContainerAppName = 'canarysec-receiver')
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$evidence = Join-Path $repo 'evidence-private'
New-Item -ItemType Directory -Force $evidence | Out-Null
$runId = Get-Date -AsUTC -Format 'yyyyMMddTHHmmssfffZ'

function Invoke-AzPrivate {
  param([Parameter(Mandatory)] [string]$EvidenceName, [Parameter(Mandatory)] [string[]]$Arguments)
  $path = Join-Path $evidence "$runId-$EvidenceName"
  $errorPath = Join-Path $evidence "$runId-$EvidenceName.stderr.txt"
  $result = @(& az @Arguments 2> $errorPath)
  $exitCode = $LASTEXITCODE
  $result | Out-File -LiteralPath $path -Encoding utf8
  if ($exitCode -ne 0) { throw "Azure CLI command failed (exit code $exitCode). See private evidence: $path and $errorPath" }
  return ($result -join [Environment]::NewLine)
}

$fqdn = (Invoke-AzPrivate '01-container-app-fqdn.txt' @('containerapp', 'show', '--resource-group', $ResourceGroup, '--name', $ContainerAppName, '--query', 'properties.configuration.ingress.fqdn', '--output', 'tsv')).Trim()
if ([string]::IsNullOrWhiteSpace($fqdn)) { throw 'Container App ingress FQDN was empty.' }

function Get-PrivateHttpResult {
  param([Parameter(Mandatory)] [string]$Path)
  $uri = "https://$fqdn$Path"
  try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $uri -ErrorAction Stop
    return [ordered]@{ StatusCode = [int]$response.StatusCode; Content = $response.Content }
  } catch {
    $statusCode = $null
    if ($_.Exception.Response) { $statusCode = [int]$_.Exception.Response.StatusCode }
    return [ordered]@{ StatusCode = $statusCode; Content = '' }
  }
}

$health = Get-PrivateHttpResult '/health'
$management = Get-PrivateHttpResult '/api/events'
$docs = Get-PrivateHttpResult '/docs'
[ordered]@{ health = $health; management = $management; docs = $docs } |
  ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidence "$runId-http-validation.json")

if ($health.StatusCode -ne 200) { throw "Health endpoint returned HTTP $($health.StatusCode); expected 200." }
$healthBody = $health.Content | ConvertFrom-Json
if ($healthBody.receiver_only -ne $true) { throw 'Health response did not report receiver_only=true.' }
if ($management.StatusCode -ne 404) { throw "Management endpoint returned HTTP $($management.StatusCode); expected 404." }
if ($docs.StatusCode -ne 404) { throw "Documentation endpoint returned HTTP $($docs.StatusCode); expected 404." }

Write-Host 'Validation passed: health 200 receiver-only; management and docs 404. Private evidence was saved under evidence-private.'
