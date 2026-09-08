# Honeytoken investigation queries

| Question | Query |
| --- | --- |
| What arrived? | [All hits](canary-hits.kql) |
| Which interactions started a window? | [First hits](canary-first-hits.kql) |
| Which callbacks repeated? | [Repeat hits](canary-repeat-hits.kql) |
| Which matched automation heuristics? | [Scanner hits](canary-scanner-hits.kql) |
| Which qualify for High? | [High-severity access](canary-high-severity.kql) |
| What activity shares a source? | [By source](activity-by-source.kql) |
| Which decoys were retrieved? | [By canary](activity-by-canary.kql) |
| When did repeats occur? | [Repeat timeline](repeat-activity-over-time.kql) |
| What happened around one incident? | [Investigate a canary](investigate-canary.kql) |

Bicep loads [first-access analytics](analytics-first-access.kql) and [scanner analytics](analytics-scanner.kql) directly, keeping deployment and query source aligned.

`RepeatCount` counts earlier matching observations in the receiver window. Use `countif(IsDuplicate)` to count repeat rows; summing `RepeatCount` overcounts related activity. Old evidence rows may have empty new columns.

Use the public hashed `CanaryId` from an incident in the investigation query. SourceIp can reflect infrastructure, and a scanner-like User-Agent is only a heuristic. Entra, Defender/EDR, SharePoint audit, Purview DLP, and proxy/firewall joins are future work, not implemented integrations.
