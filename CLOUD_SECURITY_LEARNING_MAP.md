# Cloud security learning map

| Resource/control | What it does | Why this project needs it | Security concept | Misconfiguration risk | How to validate |
|---|---|---|---|---|---|
| Resource Group | Resource boundary | Keeps temporary lab resources together | Scope and teardown | Unrelated resources could be deleted | Inventory before teardown |
| Bicep | Declarative deployment | Rebuilds the lab consistently | IaC and drift reduction | Portal-only drift | `az bicep build` and what-if |
| ACR | Stores receiver image | Reproducible container source | Supply-chain boundary | Admin keys or mutable tags | Admin disabled, digest/tag recorded |
| Managed Identity | Entra workload identity | Removes app credentials | Secretless auth | Broad role assignment | Inspect role assignments |
| RBAC | Limits Azure access | Grants only ACR/Table/DCR rights | Least privilege | Owner/Contributor overreach | Scope and role evidence |
| Container Apps | Runs receiver | Public HTTPS callback | Minimal serverless ingress | Public management routes | `/health` and `/api` checks |
| HTTPS ingress | Terminates TLS | Word needs a reachable callback | Transport security | HTTP or custom gateway drift | FQDN and `allowInsecure=false` |
| Table Storage | Persists hits/outbox | Survives container restarts | Durable evidence | Shared keys or broad access | Table entities and RBAC |
| Log Analytics | Receives normalized records | Sentinel query source | Centralized telemetry | Secrets in logs | KQL result review |
| DCR | Defines ingestion schema | Stable `CanaryHit_CL` records | Data contract | Wrong stream/table mapping | Independent ingestion test |
| Logs Ingestion API | Sends normalized events | Receiver-to-SIEM path | Managed identity ingestion | Client secret leakage | DCR status and KQL |
| KQL | Investigates hits | Analyst-friendly evidence | Detection query design | Overbroad/opaque query | Query files and result |
| Microsoft Sentinel | Correlates and cases | Alert/incident proof | SIEM workflow | Rule disabled or noisy | Rule, alert, incident |
| Analytic Rule | Turns hits into alerts | Demonstrates detection engineering | Scheduled detection | Wrong lookback/threshold | Test hit creates alert |
| Incident | Groups an alert for response | Case-management evidence | Response workflow | No incident creation | Sentinel incident |
| Cost Management | Tracks temporary use | PAYG safety | Cost awareness | Resources left running | Cost view and inventory |
| Teardown | Removes project resources | Prevents ongoing charges | Reversible lab lifecycle | Deleting unrelated assets | Dedicated RG verification |
