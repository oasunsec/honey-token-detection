# Architecture

The system has two exercised paths: a local Word callback into SQLite, and a controlled cloud callback through Azure storage, Logs Ingestion, and Sentinel.

[![Honey Token: separate local Word and Azure-to-Sentinel event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

## Components and connections

| Component | What it did in the run |
| --- | --- |
| Local generator and Word | Created a DOCX with an external pixel; Word requested the loopback receiver |
| Local receiver | Stored the callback in SQLite and recorded triage and console-alert outcomes |
| Azure receiver | Accepted controlled HTTPS callbacks in Container Apps; management routes returned 404 |
| Azure Table Storage | Stored token events in `CanaryHits` and delivery state in `NotificationOutbox` |
| Notification handler | Recorded console or SMTP delivery independently of Sentinel ingestion |
| Logs Ingestion adapter | Sent normalized events through the Direct DCR into `CanaryHit_CL` |
| Sentinel rule | Evaluated callback rows every five minutes and created a high-severity incident |
| Managed identity | Supplied scoped registry, storage, and DCR permissions |

## Source files

- [Receiver and routing](app/main.py)
- [Azure Table backend](app/azure_storage.py) and [SQLite backend](app/db.py)
- [Logs Ingestion adapter](app/azure_ingestion.py)
- [Infrastructure and Sentinel rule](infra/main.bicep)

Events are written before delivery. A failed SMTP or DCR operation remains visible in the event record; an absent adapter is recorded as disabled.

[Receiver boundaries and event fields](docs/architecture.md) · [Azure deployment](AZURE_DEPLOYMENT.md) · [Operational limits](LIMITATIONS.md)
