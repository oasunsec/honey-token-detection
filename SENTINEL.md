# Severity-aware honeytoken detections

Two scheduled rules preserve receiver triage in `CanaryHit_CL`. The first-access rule reuses the original rule resource ID, replacing the query that treated every callback as High.

| Event | Receiver decision | Sentinel decision |
| --- | --- | --- |
| Active non-scanner first hit, high/critical | `honeytoken_access`, investigate | High incident |
| Active scanner first hit | `automated_scanner`, medium, review | Medium incident |
| Repeat in matching window | Original classification retained; notification suppressed | Excluded from both rules, retained for investigation |
| Non-scanner low/medium token | Configured severity retained | Searchable, no incident under these rules |
| Revoked or malformed token | HTTP 404 | No event or incident |

A separate Medium scanner rule gives analysts a clear queue. Repeats add context rather than a new incident, so they have investigation queries instead of a third rule.

## Event contract

| Field | Meaning |
| --- | --- |
| `TimeGenerated`, `EventTime` | UTC observation time |
| `EventId` | UUID of the persisted event |
| `EventType` | `canary_trigger` |
| `CanaryId` | First 16 hex characters of SHA-256 of the random token |
| `ArtifactName` | Decoy filename |
| `SourceIp`, `UserAgent` | Observed connection metadata, not identity evidence |
| `Classification`, `Severity` | Receiver triage decision |
| `IsScanner`, `IsDuplicate`, `FirstHit` | Scanner heuristic and matching-window flags |
| `RepeatCount` | Earlier matching observations in the rolling suppression window |
| `ActiveCanary` | Token was active at receipt |
| `Reason`, `RecommendedAction` | Triage explanation and action |
| `AlertStatus` | Console/SMTP outcome before ingestion |
| `ReceiverVersion` | Receiver release |

`Receiver` and `NotificationStatus` remain compatibility aliases. The payload excludes raw tokens, paths, keys, and error messages. Historical rows are not reclassified and do not satisfy the new rule gates.

## Timing and correlation

Both rules run every five minutes, search one hour of event time, and select rows ingested in the last five minutes. They deduplicate `EventId` within a query and create an alert per result. Alerts from the same rule are grouped by `CanaryId` for one hour. Closed incidents are not reopened.

The ingestion slice follows [Microsoft ingestion-delay guidance](https://learn.microsoft.com/en-us/azure/sentinel/ingestion-delay). Grouping uses [selected entities and custom details](https://learn.microsoft.com/en-us/azure/templates/microsoft.securityinsights/2023-02-01/alertrules?pivots=deployment-language-bicep).

This is bounded correlation, not exactly-once delivery. Scheduling jitter, replayed uploads, incident grouping limits, closed incidents, and delays beyond the horizon can cause additional incidents or gaps. The investigation query retrieves repeats; no automation appends every repeat to an incident. Receiver suppression is best effort under concurrency and restarts after window expiry.

## Investigation

[Queries](docs/kql/README.md) cover all hits, first hits, repeats, scanners, High candidates, source/canary aggregation, and repeat timelines. [Investigate a canary](docs/kql/investigate-canary.kql) returns the decoy, classification, source, delivery outcome, and related-hit counts.

The [validation report](VALIDATION.md) distinguishes deployed results from adapter tests. Original captures remain in the [historical evidence](docs/evidence/public/README.md).
