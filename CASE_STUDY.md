# Document honeytokens with Azure and Microsoft Sentinel

Honey Token turns a decoy document's external image request into an event that can be investigated. The project combines a Python/FastAPI receiver, document generation, durable storage, scanner-aware triage, and console, SMTP, or Sentinel integration.

## Problem and approach

A sensitive-looking decoy can provide an early signal when accessed outside its expected workflow. Each generated document contains a unique callback URL. When a compatible viewer requests that resource, the receiver stores the timestamp, source metadata, and document association before classifying the event and attempting notification.

The signal has a narrow meaning: the resource was requested. Security scanners and preview services can trigger it, while offline hosts or viewers that block external content may produce no event. Investigation requires identity, endpoint, and file-access context.

## Implementation

The local service uses SQLite and exposes management endpoints for creating, listing, and disabling tokens. DOCX files use an external image relationship; HTML decoys reference the same transparent pixel endpoint.

The Azure deployment uses Bicep to provision Container Apps, Table Storage, a managed identity, a container registry, Log Analytics, and Microsoft Sentinel. The public receiver exposes only health and callback routes. Management routes return 404, and provisioning runs through a local operator process.

```text
Callback -> stored event -> triage -> console / SMTP
                              |
                              +-> DCR -> Log Analytics -> Sentinel incident
```

The managed identity has scoped access to pull the container image, write table entities, and ingest logs. Storage shared keys and registry admin credentials are disabled. Log Analytics receives a hashed token identifier rather than the raw callback URL.

## Engineering decisions

- **Persist before delivery.** SMTP or ingestion failures leave a stored event and delivery status for investigation.
- **Keep delivery paths independent.** An SMTP failure does not prevent the Sentinel adapter from running or change a recorded callback into an HTTP 500.
- **Retain repeat events.** Duplicate suppression reduces notifications while retaining callback records.
- **Separate management from collection.** Local management uses an API key for remote clients; the Azure receiver disables management routes entirely.
- **Exclude tokens from access logs.** Callback paths contain live identifiers, so the container disables Uvicorn access logging.

## Observed behavior

The following observations were recorded on 7 September 2026 using Windows 11, Python 3.13.14, and Azure in `southcentralus`.

| Scenario | Observation |
| --- | --- |
| Local document retrieval | Word 16.0.20326.20132 displayed the generated DOCX and requested its loopback callback. The event was classified high and a console alert was recorded. |
| Cloud callback | A controlled HTTP request returned a 34-byte GIF and produced a Table Storage event, Log Analytics row, and Sentinel incident. |
| Scanner request | A curl User-Agent received medium severity with the classification `Possible automated scanner interaction`. |
| Repeat request | The event remained stored; its notification was suppressed and the SIEM row recorded `FirstHit=false`. |
| Disabled token | The callback returned HTTP 404. |
| SMTP delivery | An ephemeral local SMTP sink received a message containing the event's triage fields. Two callbacks produced one email within the suppression window. |

The Word and Azure paths were exercised separately. Word-to-Azure retrieval, Protected View, mobile viewers, and cloud SMTP delivery were not tested. The [compatibility matrix](COMPATIBILITY.md) records viewer coverage; the [screenshot walkthrough](docs/evidence/public/README.md) shows the saved records and application captures.

## Ingestion failure and fix

The first Azure ingestion attempt failed because the receiver used a regional hostname that did not resolve. The hit remained in Table Storage with `sentinel_status=failed`. Bicep now supplies `dcr.properties.endpoints.logsIngestion`, the endpoint returned by the deployed Data Collection Rule. Subsequent events reached `CanaryHit_CL` and generated a Sentinel incident.

This failure illustrates why collection and notification have separate outcomes: an ingestion outage should remain distinguishable from a missing callback.

## Operational limits

Delivery is synchronous and has no automatic retry worker. Duplicate suppression is best effort across concurrent instances. Table Storage is durable but does not provide a tamper-evident forensic archive. A broader deployment needs ingress rate limits, retention rules, failed-delivery monitoring, and additional viewer testing.

The Sentinel rule runs every five minutes with a ten-minute lookback, so incidents depend on ingestion and scheduled evaluation. Callback IP addresses may identify a proxy or scanner rather than the originating user.

## Explore the implementation

- [Architecture](ARCHITECTURE.md) and [trust boundaries](docs/architecture.md)
- [Azure deployment](AZURE_DEPLOYMENT.md) and [Sentinel queries](SENTINEL.md)
- [Tests](TESTING.md), [security notes](SECURITY.md), and [cost and teardown](COST_AND_TEARDOWN.md)
