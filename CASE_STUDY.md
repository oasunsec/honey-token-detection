# From a local document token to a Sentinel incident

Extended a local document-token service into a deployed Azure receiver, then traced a controlled callback through Table Storage and Log Analytics to a Sentinel incident. The implementation kept token management local and retained the original SQLite path for document testing.

The run used Windows 11, Python 3.13.14, and Azure in `southcentralus` on 7 September 2026.

[![Honey Token: separate local Word and Azure-to-Sentinel event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

## Started with the local receiver

The [baseline](docs/BASELINE.md) had nine passing tests. Token creation, revocation, DOCX/HTML generation, scanner classification, and duplicate suppression were already present. Azure storage and Sentinel ingestion were missing.

Added an Azure Table backend alongside SQLite. The receiver stored callback events before attempting notifications and recorded alert and ingestion outcomes separately.

## Deployed the cloud path

Bicep provisioned a container registry, managed identity, Container Apps receiver, Table Storage, Log Analytics workspace, Direct Data Collection Rule, and Sentinel rule. The runtime used scoped `AcrPull`, `Storage Table Data Contributor`, and `Monitoring Metrics Publisher` roles. Storage shared keys and registry admin access were disabled.

The deployed receiver returned 200 from `/health` and 404 from `/api/events`. Token provisioning remained local. Controlled requests to the public callback returned the 34-byte GIF and created Table Storage events. The [deployment and health records](docs/evidence/public/README.md#03-infrastructure-deployment) capture that state.

## Fixed the first ingestion failure

The first event did not reach Log Analytics. The receiver was using a regional ingestion hostname that failed DNS resolution. Table Storage retained the hit with `sentinel_status=failed`, which exposed the delivery failure without losing the callback.

Changed the deployment to read `dcr.properties.endpoints.logsIngestion` from the deployed rule. Four subsequent records appeared in `CanaryHit_CL`. The scheduled rule created a new high-severity incident titled **Canary document access detected**. The [saved query and incident](docs/evidence/public/README.md#09-log-analytics-ingestion) show the post-fix result.

## Opened the generated document in Word

Word 16.0.20326.20132 displayed the synthetic financial document and requested its loopback pixel at 18:27 UTC. The [SQLite event](docs/evidence/public/README.md#07-word-callback-and-triage) recorded the Office User-Agent, high severity, and a sent console alert.

The document test ran against the local receiver under the existing Office and endpoint policies. The Azure test used controlled HTTP requests.

## Exercised repeats, scanners, and revocation

A curl request received medium severity and the classification `Possible automated scanner interaction`. A repeated request remained stored but its notification was suppressed; the ingested row recorded `FirstHit=false` and `RepeatCount=1`. Disabling the token changed the callback response to HTTP 404.

The SMTP test delivered a message containing the event classification and severity to a temporary local mail sink. Two callbacks produced one email, and both events remained stored. No external mailbox was used.

## Fixed notification and management failures

An SMTP exception could interrupt the callback response and prevent the Sentinel adapter from running. The fix preserved the failed notification status, continued the independent ingestion attempt, and returned the GIF. A [regression test](tests/test_app.py#L207) covered that path.

A non-ASCII management key could also cause a server error during comparison. The corrected comparison returned 401 for malformed credentials. The ingestion status was also changed to `disabled` when no Sentinel adapter was configured.

The Docker build context was restricted to application files, Compose was bound to loopback, and Uvicorn access logs were disabled because callback paths contained live tokens. The [final suite](TESTING.md) passed 16 tests with two dependency deprecation warnings.

## Project scope

Testing covered local Word callbacks and a separate Azure-to-Sentinel path. User attribution and exfiltration detection were outside the project's scope. [Operational limits](LIMITATIONS.md) and [viewer coverage](COMPATIBILITY.md) are documented separately.

[View the screenshots](docs/evidence/public/README.md) · [Run the project](docs/SETUP.md) · [Test details](TESTING.md)
