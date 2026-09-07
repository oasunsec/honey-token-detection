# Architecture

The Azure deployment extended the local document-token receiver with Table Storage and Sentinel ingestion. The diagram shows the two paths exercised during the work.

[![Honey Token: separate local Word and Azure-to-Sentinel event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

## Components and connections

| Component | Connection implemented |
| --- | --- |
| Local generator and Word | Generated a DOCX with an external pixel; Word requested the loopback receiver |
| Local receiver | Stored the callback in SQLite and recorded its classification and console alert outcome |
| Azure receiver | Accepted controlled HTTPS callbacks in Container Apps; management routes returned 404 |
| Azure Table Storage | Stored token/event data in `CanaryHits` and delivery state in `NotificationOutbox` |
| Notification handler | Recorded console/SMTP delivery outcomes independently of Sentinel ingestion |
| Logs Ingestion adapter | Sent normalized events through the Direct DCR into `CanaryHit_CL` |
| Sentinel rule | Evaluated callback rows every five minutes and created a high-severity incident |
| Managed identity | Used scoped `AcrPull`, `Storage Table Data Contributor`, and `Monitoring Metrics Publisher` roles for registry, storage, and DCR access |

## Source files

- [Receiver and routing](app/main.py)
- [Azure Table backend](app/azure_storage.py) and [local SQLite backend](app/db.py)
- [Logs Ingestion adapter](app/azure_ingestion.py)
- [Infrastructure and Sentinel rule](infra/main.bicep)

Events were stored before notification delivery. SMTP failures retained a failed status and did not skip the Sentinel adapter. An absent adapter was recorded as disabled.

[Receiver boundaries and event fields](docs/architecture.md) · [Azure deployment](AZURE_DEPLOYMENT.md) · [Operational limits](LIMITATIONS.md)
