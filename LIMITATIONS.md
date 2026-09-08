# Operational limits

## Collection and attribution

A callback proves resource retrieval. It does not prove exfiltration or who opened a document. An observed IP may belong to NAT, VPN, proxy, scanner, or security-gateway infrastructure. Requesters supply User-Agent values and can spoof or omit them. Scanner classification is a small heuristic, not proof of a human or attacker.

The DOCX callback requires a viewer to load external content with network access. Protected View, external-content policy, proxies, DNS controls, endpoint controls, or document rewriting can block it. Offline and air-gapped opens may never fire. [Viewer coverage](COMPATIBILITY.md) records observed behavior.

Attribution requires endpoint, identity, DLP, and file-audit correlation. Honeytokens complement DLP, access controls, encryption, EDR, and SIEM monitoring; they do not replace them.

## Persistence and delivery

Observations are committed before triage and delivery. A storage failure before that commit prevents delivery. A process crash or triage failure after the initial commit can leave a pending event. SMTP and ingestion are synchronous with no retry worker. Status writes can fail after a send, leaving an ambiguous pending state while the other delivery path is still attempted.

Repeats match token and User-Agent within a rolling five-minute window by default. Counts reflect earlier matching rows in that window, not lifetime activity. Only earlier observations count toward suppression: SQLite insertion order and Azure timestamp/UUID order prevent two visible concurrent rows suppressing each other. This is not a distributed atomic claim; races and delayed visibility can still cause extra first-hit decisions. Changing UA can start another window. Source changes are retained but do not reset suppression, because ingress peer addresses can rotate. Two clients with the same canary and UA share the window. With proxy trust disabled, SourceIp can represent an ingress proxy rather than the originating endpoint.

Events remain mutable; there is no tamper-evident archive. Log Analytics retains 30 days. Azure Table needs an operator retention policy. The provisioned outbox table has no worker; outcomes are stored on event rows.

## Sentinel

First-access and scanner rules have High and Medium severity respectively. Duplicate rows are excluded from both. Each uses a five-minute ingestion slice, one-hour event horizon, and one-hour grouping by canary. Grouping does not guarantee exactly one incident forever. Replayed ingestion, scheduling jitter, closed incidents, platform grouping limits, and long ingestion delays remain concerns. Repeat enrichment requires a query.

Low/medium non-scanner tokens are retained but do not trigger the High rule. Older rows without the structured contract are excluded. Canary activation is checked at receipt, not rechecked during rule evaluation.

## Deployment

The HTTPS receiver has no project WAF or ingress rate limiter. Management routes and OpenAPI are disabled in receiver-only mode. Callback tokens remain in documents, private token storage, and transport paths; upstream services or endpoint products can observe them. [Security controls](SECURITY.md) describe these boundaries.

SMTP was exercised against a loopback sink; cloud SMTP is not configured. [Resource lifecycle](COST_AND_TEARDOWN.md) records cost and cleanup status. Entra, Defender/EDR, SharePoint audit, Purview DLP, and proxy/firewall correlation are future work, not implemented integrations.
