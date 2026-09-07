# Microsoft Sentinel validation

The Direct DCR declares the `Custom-CanaryHit_CL` stream and routes it to the project Log Analytics workspace. The receiver sends normalized records without raw callback secrets:

`TimeGenerated`, `EventType`, `CanaryId`, `ArtifactName`, `SourceIp`, `UserAgent`, `Classification`, `FirstHit`, `RepeatCount`, `Receiver`, `NotificationStatus`, and `EventId`.

Queries are stored in `docs/kql/`. Validate ingestion with `canary-hits.kql`, then create a scheduled Sentinel rule named **Canary document access detected** with a five-minute frequency, ten-minute lookback, threshold greater than zero, incident creation enabled, an IP entity mapping from `SourceIp`, and custom details for `CanaryId`, `ArtifactName`, `Classification`, `FirstHit`, `RepeatCount`, `NotificationStatus`, and `EventId`. The checked-in Bicep creates this rule with the same settings.

The receiver remains functional if Sentinel ingestion is unavailable. The durable hit remains in Table Storage and records `sentinel_status=failed` with a bounded diagnostic error for later retry or investigation.


The rule is intentionally scheduled rather than inline on the callback path. A callback must persist durable evidence and remain useful when Sentinel is temporarily unavailable; the receiver records the ingestion outcome so a failed DCR call is distinguishable from a missing event. In the validation environment, the first event recorded the expected failure from the pre-fix regional endpoint, and later events ingested successfully through the resource-specific DCR endpoint and produced a new Sentinel incident.
