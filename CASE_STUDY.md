# From a local document token to a Sentinel incident

The starting service generated decoy documents, stored callbacks in SQLite, and sent console or SMTP alerts. The Azure work added a durable receiver and connected its events to Microsoft Sentinel without exposing the management API.

Work recorded on 7 September 2026 used Windows 11, Python 3.13.14, and Azure in `southcentralus`.

## Started with the local receiver

The baseline had nine passing tests. Token creation, revocation, DOCX/HTML generation, scanner classification, and duplicate suppression were already present. Azure storage and Sentinel ingestion were missing.

The implementation retained SQLite for local use and added an Azure Table backend for the deployed receiver. Callback events were stored before notification delivery. The receiver recorded alert and ingestion outcomes separately.

## Deployed the cloud path

Bicep provisioned a container registry, managed identity, Container Apps receiver, Table Storage, Log Analytics workspace, Direct Data Collection Rule, and Sentinel rule. The runtime used scoped `AcrPull`, `Storage Table Data Contributor`, and `Monitoring Metrics Publisher` roles. Storage shared keys and registry admin access were disabled.

The deployed receiver returned 200 from `/health` and 404 from `/api/events`. Token provisioning remained local. Controlled requests to the public callback returned the 34-byte GIF and created Table Storage events.

## Fixed the first ingestion failure

The first event did not reach Log Analytics. The receiver was using a regional ingestion hostname that failed DNS resolution. Table Storage retained the hit with `sentinel_status=failed`, which exposed the delivery failure without losing the callback.

The deployment was changed to read `dcr.properties.endpoints.logsIngestion` from the deployed rule. Four subsequent records appeared in `CanaryHit_CL`. The scheduled rule created a new high-severity incident titled **Canary document access detected**.

## Opened the generated document in Word

Word 16.0.20326.20132 displayed the synthetic financial document and requested its loopback pixel at `2026-09-07T18:27:35.267154+00:00`. SQLite recorded the Office User-Agent, high severity, and a sent console alert.

This was a local document-to-local receiver test. The Azure path used controlled HTTP requests; Word-to-Azure retrieval was not exercised. Office and endpoint policies were left unchanged.

## Exercised repeats, scanners, and revocation

A curl request received medium severity and the classification `Possible automated scanner interaction`. A repeated request remained stored but its notification was suppressed; the ingested row recorded `FirstHit=false` and `RepeatCount=1`. Disabling the token changed the callback response to HTTP 404.

The SMTP test delivered a triage-derived message to an ephemeral loopback sink. Two callbacks produced one email, and both events remained stored. No external mailbox was used.

## Fixed notification and management failures

An SMTP exception could interrupt the callback response and prevent the Sentinel adapter from running. The handler was changed to persist the failed notification, continue the independent ingestion attempt, and return the GIF. A regression test covered that path.

A non-ASCII management key could also cause a server error during comparison. The comparison was corrected and malformed credentials returned 401. An unconfigured Sentinel adapter now recorded `disabled` instead of leaving an event pending.

The Docker build context was restricted to application files, Compose was bound to loopback, and Uvicorn access logs were disabled because callback paths contained live tokens. The final suite passed 16 tests with two dependency deprecation warnings.

## Remaining work

No retry worker, distributed atomic suppression, ingress rate limiter, or tamper-evident archive was added. Cloud SMTP, Protected View, separate-endpoint Word, and mobile viewers remained untested. The resource group had not been torn down, and no cost measurement was captured.

The observed callbacks established resource retrieval. They did not establish who opened a document or whether data was exfiltrated.

[View the screenshots](docs/evidence/public/README.md) · [Run the project](docs/SETUP.md) · [Test details](TESTING.md)
