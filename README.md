# Honey Token

Built an Azure-backed document honeytoken receiver and wired its events into Microsoft Sentinel. The local service already generated DOCX/HTML decoys and stored callbacks in SQLite; this pass added Azure Table Storage, managed-identity deployment, Logs Ingestion, and a scheduled Sentinel rule.

[Case study](CASE_STUDY.md) · [Screenshots](docs/evidence/public/README.md) · [Run locally](docs/SETUP.md) · [Architecture](ARCHITECTURE.md)

[![Honey Token: separate local Word and Azure-to-Sentinel event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

**Stack:** Python, FastAPI, SQLite, Azure Table Storage, Container Apps, Bicep, Log Analytics, KQL, Microsoft Sentinel, Docker, and GitHub Actions.

## Local demo

[![Document creation, Word, and the recorded callback](docs/demo/local-word-callback.gif)](docs/demo/local-word-callback.mp4)

[Watch the MP4](docs/demo/local-word-callback.mp4)

The recording covers the local Word path. The Azure-to-Sentinel path is shown separately in the [case study](CASE_STUDY.md).

## What changed

- Kept SQLite for local runs and added Azure Table Storage for deployed events and notification outcomes.
- Deployed a receiver-only Container App with HTTPS ingress, disabled management routes, and scoped managed-identity roles.
- Fixed the DCR endpoint after the first ingestion attempt failed DNS resolution; later events reached Log Analytics and created a Sentinel incident.
- Separated event persistence from notification and Sentinel delivery so a delivery failure did not discard a hit.
- Fixed SMTP failure handling, malformed management-key comparison, the Docker build context, and loopback Compose binding.

## Observed results

| Path | Result | Evidence |
| --- | --- | --- |
| Local Word document | Word requested the pixel; SQLite stored a high-severity event and the console alert was sent | [Word callback](docs/evidence/public/README.md#07-word-callback-and-triage) |
| Controlled Azure callback | Table Storage and Log Analytics received the event; the scheduled rule created a high-severity incident | [Sentinel incident](docs/evidence/public/README.md#11-sentinel-incident) |
| Repeat callback and local SMTP | Both events were stored; the repeat notification was suppressed and the local sink received one email | [Test details](TESTING.md) |

The Word and Azure paths were separate runs. [Viewer coverage](COMPATIBILITY.md) and [operational limits](LIMITATIONS.md) state what the evidence does not prove.

## Documentation

| Topic | Links |
| --- | --- |
| Build and investigation | [Case study](CASE_STUDY.md), [screenshots](docs/evidence/public/README.md), [starting point](docs/BASELINE.md) |
| Implementation | [Architecture](ARCHITECTURE.md), [Azure deployment](AZURE_DEPLOYMENT.md), [Sentinel rule and queries](SENTINEL.md) |
| Run and maintain | [Setup](docs/SETUP.md), [tests](TESTING.md), [security](SECURITY.md), [cost and teardown](COST_AND_TEARDOWN.md) |

Examples use synthetic documents and controlled test systems.

## License

[MIT](LICENSE)
