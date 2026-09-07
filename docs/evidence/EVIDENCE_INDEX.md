# Evidence index

Raw screenshots and command output belong under `evidence-private/`, which is ignored by Git. Only sanitized, portfolio-safe evidence may be placed under `docs/evidence/public/`.

| Filename | Phase | Demonstrates | Security concept | Redactions | Validation |
|---|---|---|---|---|---|
| `00-azure-start-state` | Preflight | Subscription/provider starting state | Scoped change boundary | Yes | `preflight.ps1` |
| `02-bicep-what-if` | IaC | Planned project resources | Reproducible deployment | No secrets | `deploy.ps1` |
| `03-bicep-final-deployment` | IaC | Deployment result | Declarative infrastructure | Yes | `deploy.ps1` |
| `07-container-app-overview` | Runtime | Receiver configuration | HTTPS receiver-only boundary | Yes | `deploy.ps1` |
| `09-container-app-health` | Runtime | Health response | Safe health endpoint | No secrets | `validate.ps1` |
| `16-real-callback-received` | Detection | Callback observed | Detection signal | Token redacted | Manual Word or controlled HTTP test |
| `17-persisted-canary-hit` | Storage | Durable Azure Table event | Evidence before delivery | Token redacted | Table query |
| `18-email-alert` | Alerting | Safe mailbox delivery | Triage-derived notification | No credentials | SMTP sink |
| `19-log-analytics-kql-result` | SIEM | `CanaryHit_CL` query result | Analyst investigation | Token redacted | KQL |
| `20-sentinel-analytic-rule` | Sentinel | Scheduled rule | Detection engineering | No secrets | Sentinel |
| `21-sentinel-alert` | Sentinel | Alert created | Signal-to-alert path | Token redacted | Sentinel |
| `22-sentinel-incident` | Sentinel | Incident created | Case management | Token redacted | Sentinel |
| `26-final-resource-inventory` | Teardown | Project-only inventory | Safe cleanup boundary | Yes | `az resource list` |
| `29-post-teardown` | Teardown | Resource group absent | Cost control | Yes | `destroy.ps1` |
