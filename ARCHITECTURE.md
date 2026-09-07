# Architecture

```mermaid
flowchart TD
  G[Local canary generator] --> D[Canary DOCX]
  D --> W[Microsoft Word on controlled endpoint]
  W --> I[Azure Container Apps HTTPS ingress]
  I --> R[Receiver-only FastAPI application]
  R --> T[Azure Table Storage: CanaryHits]
  R --> O[NotificationOutbox state]
  R --> E[Existing console or SMTP alert]
  R --> L[Azure Monitor Logs Ingestion API]
  L --> DCR[Direct Data Collection Rule]
  DCR --> C[CanaryHit_CL]
  C --> S[Microsoft Sentinel]
  S --> A[Scheduled analytic rule]
  A --> N[Sentinel alert and incident]
  MI[User-assigned managed identity] --> R
  MI -->|AcrPull| ACR[Azure Container Registry]
  MI -->|Storage Table Data Contributor| T
  MI -->|Monitoring Metrics Publisher| DCR
```

The callback persists a hit before attempting email or Azure Monitor delivery. The Azure receiver does not expose management routes; token and decoy provisioning can happen locally with the same Azure Table backend using the operator's `DefaultAzureCredential`.
