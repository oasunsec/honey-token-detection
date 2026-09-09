# Honey Token case study

This is a short record of what I started with, what I changed, and what happened during testing.

[![Honey Token event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

## Starting point

The local app already created and disabled tokens, generated DOCX and HTML decoys, stored callbacks in SQLite, detected scanner-like requests, suppressed repeats, and sent console or SMTP alerts. The baseline had nine passing tests.

It did not have an Azure storage backend, a cloud receiver-only mode, or a Microsoft Sentinel adapter.

## What I changed

- Added Azure Table Storage beside SQLite.
- Added Azure deployment files for Container Apps, a managed identity, Log Analytics, a Direct DCR, and Sentinel.
- Saved each event before trying to send an alert or ingest it into Log Analytics.
- Added delivery status so alert and ingestion failures do not hide the original event.
- Added first-hit, repeat, scanner, severity, and repeat-count fields.
- Added separate High and Medium Sentinel rules.
- Added KQL queries for first hits, repeats, scanners, and individual canaries.

The cloud receiver exposes `/health` and the callback route. Management and documentation routes return 404. Token creation stays local.

## What happened

The first cloud callback was saved in Table Storage but did not reach Log Analytics. The deployment was using the wrong ingestion hostname. I changed it to use the `logsIngestion` endpoint returned by the deployed DCR. Later events reached `CanaryHit_CL`, and Sentinel created the expected incidents.

The Word test and the controlled Azure callback test were separate. The local Word run recorded an Office User-Agent and a high-severity event. The cloud run recorded the Word request in Table Storage and Log Analytics and matched it to High incident 17.

## Results

- Six cloud events were stored and ingested.
- Two non-scanner first hits created High incidents.
- One scanner first hit created a Medium incident.
- Three repeat events were stored but did not create extra alerts.
- The local SMTP test stored two events and accepted one email.
- `pytest -q` passed 43 tests. Bicep compilation and the GitHub Actions checks passed.

## Limits

The files use synthetic data. The project shows that a decoy requested its callback image; it does not identify who opened the file or prove document exfiltration. Scanner detection is based on request markers, and Word behavior can change with Office and endpoint settings.

[Screenshots](docs/evidence/public/README.md) - [Run locally](docs/SETUP.md) - [Test details](TESTING.md)
