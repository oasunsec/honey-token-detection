# Microsoft Sentinel rules

The receiver sends events to the `CanaryHit_CL` table. Two scheduled rules decide which events should create incidents.

| Event | Receiver label | Sentinel result |
| --- | --- | --- |
| Non-scanner first hit with High or Critical severity | `honeytoken_access` | High incident |
| Scanner-like first hit | `automated_scanner` | Medium incident |
| Repeat within the matching window | Same label as the first hit | Stored for investigation; no new incident |
| Non-scanner first hit with Low or Medium severity | `honeytoken_access` | Stored; no incident under these rules |
| Revoked or bad token | No event | HTTP 404 |

## Event fields

| Field | Meaning |
| --- | --- |
| `TimeGenerated`, `EventTime` | Time of the request in UTC. |
| `EventId` | UUID for the saved event. |
| `EventType` | `canary_trigger`. |
| `CanaryId` | First 16 characters of the SHA-256 token hash. |
| `ArtifactName` | Decoy filename. |
| `SourceIp`, `UserAgent` | Connection details. They are not proof of identity. |
| `Classification`, `Severity` | Receiver decision. |
| `IsScanner`, `IsDuplicate`, `FirstHit` | Request and matching flags. |
| `RepeatCount` | Number of earlier matching requests. |
| `ActiveCanary` | Whether the token was active when received. |
| `Reason`, `RecommendedAction` | Explanation and suggested next step. |
| `AlertStatus` | Console or SMTP result before SIEM ingestion. |
| `ReceiverVersion` | Receiver release. |

## Timing

Both rules run every five minutes. They search one hour of event time and the last five minutes of ingestion. Incidents are grouped by `CanaryId` for one hour. Repeats remain in the table for investigation.

## Queries

[Investigation queries](docs/kql/README.md) cover all hits, first hits, repeats, scanners, High candidates, and activity by canary or source. [Investigate a canary](docs/kql/investigate-canary.kql) joins the event details and related hits.

The [validation results](VALIDATION.md) show the observed cloud incidents. The [evidence walkthrough](docs/evidence/public/README.md) contains the saved records and screenshots.
