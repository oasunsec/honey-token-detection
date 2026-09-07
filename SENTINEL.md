# Microsoft Sentinel validation

The Direct DCR declares the `Custom-CanaryHit_CL` stream and routes it to the project Log Analytics workspace. The receiver sends normalized records without raw callback secrets:

`TimeGenerated`, `EventType`, `CanaryId`, `ArtifactName`, `SourceIp`, `UserAgent`, `Classification`, `FirstHit`, `RepeatCount`, `Receiver`, `NotificationStatus`, and `EventId`.

Queries are stored in `docs/kql/`. Validate ingestion with `canary-hits.kql`, then create a scheduled Sentinel rule named **Canary document access detected** with a five-minute frequency, ten-minute lookback, threshold greater than zero, incident creation enabled, and custom details for `CanaryId`, `ArtifactName`, `UserAgent`, `Classification`, `FirstHit`, and `RepeatCount`.

The receiver remains functional if Sentinel ingestion is unavailable. The durable hit remains in Table Storage and records `sentinel_status=failed` with a bounded diagnostic error for later retry or investigation.
