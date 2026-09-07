# Sentinel ingestion and incident

Connected the receiver to the `Custom-CanaryHit_CL` stream through a Direct Data Collection Rule. The payload carried event time, a hashed token identifier, artifact name, source metadata, classification, repeat state, notification outcome, and event ID. Raw callback tokens and request paths stayed out of the SIEM payload.

The first ingestion attempt failed against an unresolved regional hostname. Table Storage retained the hit with `sentinel_status=failed`. After the endpoint was changed to the value returned by the deployed DCR, four records appeared in `CanaryHit_CL`.

Bicep deployed **Canary document access detected** with a five-minute frequency, ten-minute lookback, threshold greater than zero, and incident creation enabled. `SourceIp` was mapped as an IP entity. The resulting incident was recorded with severity `High` and status `New`.

The repeat event reached Log Analytics with `FirstHit=false`, `RepeatCount=1`, and a suppressed notification status. The scanner row retained `Possible automated scanner interaction` in `Classification`. Receiver severity stayed in the event record; the ingestion schema did not include a severity field.

The rule selected all `canary_trigger` rows and applied its configured high severity, including scanner and repeat rows. Receiver email or console suppression did not filter the Sentinel query.

The inspection queries are [all hits](docs/kql/canary-hits.kql), [first hits](docs/kql/canary-first-hits.kql), and [repeat hits](docs/kql/canary-repeat-hits.kql). Saved query and incident records appear in [screenshots 09–11](docs/evidence/public/README.md#09-log-analytics-ingestion).
