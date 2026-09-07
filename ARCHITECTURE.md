# Architecture

```mermaid
flowchart TD
  G[Local canary generator] --> D[Canary DOCX]
  D --> W[Microsoft Word on controlled endpoint]
  W --> LOCAL[Local SQLite receiver: observed Word test]
  HTTP[Controlled HTTP requests] --> I[Azure Container Apps HTTPS ingress]
  I --> R[Receiver-only FastAPI application]
  R --> T[Azure Table Storage: CanaryHits]
  R --> O[NotificationOutbox state]
  R --> TRIAGE[Event classification and repeat decision]
  TRIAGE --> E[Console or SMTP alert]
  LOCAL --> LE[Stored local event and console alert]
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

The work added the Azure branch to the existing local receiver. Controlled HTTP requests exercised the cloud path; Word exercised the separate loopback path.

The handler stored events before attempting notification. SMTP failures retained a failed status and did not skip the Sentinel adapter. An absent adapter was recorded as disabled. Delivery remained synchronous; [operational limits](LIMITATIONS.md) covers retry and concurrency behavior.
