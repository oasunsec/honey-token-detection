targetScope = 'resourceGroup'

@description('Azure region for the temporary validation environment.')
param location string = resourceGroup().location
@description('Short lowercase project prefix used for globally unique names.')
param projectPrefix string = 'canarysec'
@description('Container image. The first deployment may omit the Container App, then deploy.ps1 supplies the ACR image.')
param containerImage string = ''
@description('Create the Container App after the image has been built.')
param deployContainerApp bool = false
@description('Azure Container Registry SKU. Basic is sufficient for this validation.')
param acrSku string = 'Basic'
@description('Container App minimum replicas during validation.')
param minReplicas int = 1
@description('Receiver release identifier attached to every SIEM event.')
param receiverVersion string = '0.2.2'

var tags = {
  Project: 'CanaryHoneytoken'
  Environment: 'Validation'
  ManagedBy: 'Bicep'
  Purpose: 'CloudSecurityPortfolio'
}
var suffix = uniqueString(resourceGroup().id)
var registryName = take('${projectPrefix}acr${suffix}', 50)
var storageName = take('${projectPrefix}st${suffix}', 24)
var identityName = '${projectPrefix}-receiver-mi'
var workspaceName = '${projectPrefix}-law'
var environmentName = '${projectPrefix}-cae'
var appName = '${projectPrefix}-receiver'
var dcrName = '${projectPrefix}-dcr'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  sku: {
    name: acrSku
  }
  tags: tags
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  tags: tags
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    publicNetworkAccess: 'Enabled'
  }
}

resource tableService 'Microsoft.Storage/storageAccounts/tableServices@2023-05-01' = {
  name: 'default'
  parent: storage
}

resource hitsTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  name: 'CanaryHits'
  parent: tableService
}

resource outboxTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  name: 'NotificationOutbox'
  parent: tableService
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource customTable 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = {
  name: 'CanaryHit_CL'
  parent: workspace
  properties: {
    schema: {
      name: 'CanaryHit_CL'
      columns: [
        { name: 'TimeGenerated', type: 'datetime' }
        { name: 'EventType', type: 'string' }
        { name: 'CanaryId', type: 'string' }
        { name: 'ArtifactName', type: 'string' }
        { name: 'SourceIp', type: 'string' }
        { name: 'UserAgent', type: 'string' }
        { name: 'Classification', type: 'string' }
        { name: 'EventTime', type: 'datetime' }
        { name: 'Severity', type: 'string' }
        { name: 'IsScanner', type: 'bool' }
        { name: 'IsDuplicate', type: 'bool' }
        { name: 'ActiveCanary', type: 'bool' }
        { name: 'Reason', type: 'string' }
        { name: 'RecommendedAction', type: 'string' }
        { name: 'AlertStatus', type: 'string' }
        { name: 'ReceiverVersion', type: 'string' }
        { name: 'FirstHit', type: 'bool' }
        { name: 'RepeatCount', type: 'int' }
        { name: 'Receiver', type: 'string' }
        { name: 'NotificationStatus', type: 'string' }
        { name: 'EventId', type: 'string' }
      ]
    }
    retentionInDays: 30
  }
}

resource dcr 'Microsoft.Insights/dataCollectionRules@2023-03-11' = {
  name: dcrName
  location: location
  kind: 'Direct'
  tags: tags
  dependsOn: [ customTable ]
  properties: {
    description: 'Direct ingestion for normalized canary document hit events.'
    destinations: {
      logAnalytics: [
        {
          name: 'canaryWorkspace'
          workspaceResourceId: workspace.id
        }
      ]
    }
    dataFlows: [
      {
        streams: [ 'Custom-CanaryHit_CL' ]
        destinations: [ 'canaryWorkspace' ]
      }
    ]
    streamDeclarations: {
      'Custom-CanaryHit_CL': {
        columns: [
          { name: 'TimeGenerated', type: 'datetime' }
          { name: 'EventType', type: 'string' }
          { name: 'CanaryId', type: 'string' }
          { name: 'ArtifactName', type: 'string' }
          { name: 'SourceIp', type: 'string' }
          { name: 'UserAgent', type: 'string' }
          { name: 'Classification', type: 'string' }
          { name: 'EventTime', type: 'datetime' }
          { name: 'Severity', type: 'string' }
          { name: 'IsScanner', type: 'boolean' }
          { name: 'IsDuplicate', type: 'boolean' }
          { name: 'ActiveCanary', type: 'boolean' }
          { name: 'Reason', type: 'string' }
          { name: 'RecommendedAction', type: 'string' }
          { name: 'AlertStatus', type: 'string' }
          { name: 'ReceiverVersion', type: 'string' }
          { name: 'FirstHit', type: 'boolean' }
          { name: 'RepeatCount', type: 'int' }
          { name: 'Receiver', type: 'string' }
          { name: 'NotificationStatus', type: 'string' }
          { name: 'EventId', type: 'string' }
        ]
      }
    }
  }
}

resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployContainerApp) {
  name: guid(acr.id, identity.name, 'acr-pull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployContainerApp) {
  name: guid(storage.id, identity.name, 'table-data-contributor')
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource dcrRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployContainerApp) {
  name: guid(dcr.id, identity.name, 'monitoring-metrics-publisher')
  scope: dcr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3913510d-42f4-4e42-8a64-420c390055eb')
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = if (deployContainerApp) {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  tags: tags
  properties: {
    managedEnvironmentId: containerEnv.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: acr.properties.loginServer
          identity: identity.id
        }
      ]
      secrets: []
    }
    template: {
      scale: {
        minReplicas: minReplicas
        maxReplicas: 2
      }
      containers: [
        {
          name: 'receiver'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'CANARY_BASE_URL', value: 'https://${appName}.${containerEnv.properties.defaultDomain}' }
            { name: 'CANARY_STORAGE_BACKEND', value: 'azure_table' }
            { name: 'CANARY_AZURE_STORAGE_ACCOUNT_URL', value: 'https://${storage.name}.table.${environment().suffixes.storage}' }
            { name: 'CANARY_AZURE_TABLE_HITS', value: 'CanaryHits' }
            { name: 'CANARY_AZURE_TABLE_OUTBOX', value: 'NotificationOutbox' }
            { name: 'CANARY_AZURE_DCR_ENDPOINT', value: dcr.properties.endpoints.logsIngestion }
            { name: 'CANARY_AZURE_DCR_IMMUTABLE_ID', value: dcr.properties.immutableId }
            { name: 'CANARY_AZURE_DCR_STREAM_NAME', value: 'Custom-CanaryHit_CL' }
            { name: 'CANARY_RECEIVER_ONLY', value: 'true' }
            { name: 'CANARY_RECEIVER_VERSION', value: receiverVersion }
            { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
            { name: 'CANARY_ALERT_MODE', value: 'console' }
            { name: 'CANARY_TRUST_PROXY_HEADERS', value: 'false' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000, scheme: 'HTTP' }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health', port: 8000, scheme: 'HTTP' }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
          ]
        }
      ]
    }
  }
}

resource sentinelOnboarding 'Microsoft.SecurityInsights/onboardingStates@2023-02-01' = {
  name: 'default'
  scope: workspace
  properties: {}
}

resource analyticRule 'Microsoft.SecurityInsights/alertRules@2023-02-01' = {
  name: guid(workspace.id, 'canary-document-access-detected')
  scope: workspace
  dependsOn: [ sentinelOnboarding, customTable ]
  kind: 'Scheduled'
  properties: {
    displayName: 'Honeytoken first-hit suspicious access'
    description: 'Active non-scanner first hits at receiver high or critical severity. Correlate with endpoint and identity telemetry before attribution.'
    enabled: true
    severity: 'High'
    query: loadTextContent('../docs/kql/analytics-first-access.kql')
    queryFrequency: 'PT5M'
    queryPeriod: 'PT1H'
    triggerOperator: 'GreaterThan'
    triggerThreshold: 0
    suppressionEnabled: false
    suppressionDuration: 'PT5M'
    tactics: [ 'Collection' ]
    techniques: []
    eventGroupingSettings: { aggregationKind: 'AlertPerResult' }
    incidentConfiguration: {
      createIncident: true
      groupingConfiguration: {
        enabled: true
        matchingMethod: 'Selected'
        groupByCustomDetails: [ 'CanaryId' ]
        reopenClosedIncident: false
        lookbackDuration: 'PT1H'
      }
    }
    entityMappings: [
      {
        entityType: 'IP'
        fieldMappings: [
          { identifier: 'Address', columnName: 'SourceIp' }
        ]
      }
    ]
    customDetails: {
      CanaryId: 'CanaryId'
      ArtifactName: 'ArtifactName'
      Classification: 'Classification'
      FirstHit: 'FirstHit'
      RepeatCount: 'RepeatCount'
      NotificationStatus: 'NotificationStatus'
      EventId: 'EventId'
      Severity: 'Severity'
      IsScanner: 'IsScanner'
      IsDuplicate: 'IsDuplicate'
      Reason: 'Reason'
      AlertStatus: 'AlertStatus'
    }
  }
}
resource scannerRule 'Microsoft.SecurityInsights/alertRules@2023-02-01' = {
  name: guid(workspace.id, 'honeytoken-scanner-interaction')
  scope: workspace
  dependsOn: [ sentinelOnboarding, customTable ]
  kind: 'Scheduled'
  properties: {
    displayName: 'Honeytoken automated scanner interaction'
    description: 'Scanner-classified first hits. Review automation and gateway context; User-Agent heuristics are not attribution.'
    enabled: true
    severity: 'Medium'
    query: loadTextContent('../docs/kql/analytics-scanner.kql')
    queryFrequency: 'PT5M'
    queryPeriod: 'PT1H'
    triggerOperator: 'GreaterThan'
    triggerThreshold: 0
    suppressionEnabled: false
    suppressionDuration: 'PT5M'
    tactics: [ 'Collection' ]
    techniques: []
    eventGroupingSettings: { aggregationKind: 'AlertPerResult' }
    incidentConfiguration: {
      createIncident: true
      groupingConfiguration: {
        enabled: true
        matchingMethod: 'Selected'
        groupByCustomDetails: [ 'CanaryId' ]
        reopenClosedIncident: false
        lookbackDuration: 'PT1H'
      }
    }
    entityMappings: [
      {
        entityType: 'IP'
        fieldMappings: [
          { identifier: 'Address', columnName: 'SourceIp' }
        ]
      }
    ]
    customDetails: {
      CanaryId: 'CanaryId'
      ArtifactName: 'ArtifactName'
      Classification: 'Classification'
      FirstHit: 'FirstHit'
      RepeatCount: 'RepeatCount'
      NotificationStatus: 'NotificationStatus'
      EventId: 'EventId'
      Severity: 'Severity'
      IsScanner: 'IsScanner'
      IsDuplicate: 'IsDuplicate'
      Reason: 'Reason'
      AlertStatus: 'AlertStatus'
    }
  }
}
output resourceGroupName string = resourceGroup().name
output registryName string = acr.name
output registryLoginServer string = acr.properties.loginServer
output storageAccountName string = storage.name
output storageTableEndpoint string = 'https://${storage.name}.table.${environment().suffixes.storage}'
output workspaceName string = workspace.name
output workspaceId string = workspace.id
output dcrName string = dcr.name
output dcrImmutableId string = dcr.properties.immutableId
output dcrEndpoint string = dcr.properties.endpoints.logsIngestion
output analyticRuleName string = analyticRule.name
output receiverIdentityName string = identity.name
output receiverPrincipalId string = identity.properties.principalId
output containerAppName string = deployContainerApp ? containerApp.name : ''
output containerAppFqdn string = deployContainerApp ? containerApp!.properties.configuration.ingress.fqdn : ''

output scannerRuleName string = scannerRule.name
