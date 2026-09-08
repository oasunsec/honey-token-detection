# From local callback to Sentinel incident

Extended a local document-token service into an Azure receiver and traced a controlled event through Table Storage, Log Analytics, and Microsoft Sentinel. The local SQLite path stayed in place for document testing.

The recorded run used Windows 11, Python 3.13.14, and Azure `southcentralus` on 7 September 2026.

[![Honey Token: separate local Word and Azure-to-Sentinel event paths](docs/diagrams/tested-event-paths.png)](docs/diagrams/tested-event-paths.png)

## Starting point

The baseline had nine passing tests. It already created and revoked tokens, generated DOCX and HTML decoys, classified scanner-like requests, suppressed repeats, and sent console or SMTP alerts. It had no Azure storage backend, receiver-only deployment mode, or Sentinel adapter.

## What I changed

Added an Azure Table backend beside SQLite. The receiver now writes the event before attempting notification or Logs Ingestion, and records each delivery outcome independently.

Bicep provisioned the registry, managed identity, Container App, Table Storage, Log Analytics workspace, Direct DCR, and Sentinel rule. The runtime received only `AcrPull`, `Storage Table Data Contributor`, and `Monitoring Metrics Publisher`. Storage shared keys and ACR admin access stayed disabled.

The deployed `/health` route returned 200 with receiver-only mode enabled. `/api/events` returned 404. Token creation remained in the local operator process. Controlled callbacks returned the 34-byte GIF and created Table Storage records.

## The ingestion failure

The first callback was stored but did not reach Log Analytics. The receiver used a regional ingestion hostname that failed DNS resolution. Table Storage retained the hit with `sentinel_status=failed`, so the delivery defect did not erase the event.

Changed the deployment to read `dcr.properties.endpoints.logsIngestion` from the deployed rule. Four later records appeared in `CanaryHit_CL`, and the scheduled rule created **Canary document access detected** with high severity.

## The Word run

Word 16.0.20326.20132 opened the synthetic document and requested its loopback pixel at 18:27 UTC. The local event recorded the Office User-Agent, source metadata, high severity, and a sent console alert. The [compatibility record](COMPATIBILITY.md) identifies the exact viewer and the limits of that test.

The Word run and the Azure run were separate. Word exercised the local receiver; controlled HTTPS callbacks exercised the cloud path.

## Failure handling and regression coverage

An SMTP exception could previously interrupt the callback response and prevent the Sentinel adapter from running. The fix retained the event, recorded the failed notification, continued the independent ingestion attempt, and returned the GIF. A [regression test](tests/test_app.py) covers that path.

A non-ASCII management key could trigger a server error during comparison. The corrected comparison returns 401. Missing Sentinel configuration now records `sentinel_status=disabled` instead of leaving an ambiguous pending state.

The baseline suite passed 16 tests with two dependency deprecation warnings. The Docker build context is allowlisted, Compose binds to loopback, and Uvicorn access logs are disabled because callback paths contain live tokens.

## Preserving triage in Sentinel

The first integration dropped receiver severity from its ingestion schema. Its single High rule selected scanner and repeat rows along with genuine-looking access. I added structured triage fields, two severity-specific analytics, repeat counts, and an investigation query keyed by a hashed canary ID.

The first upgraded cloud run exposed rotating ingress peer addresses. Including SourceIp in the repeat key caused consecutive callbacks to appear as separate first hits. I changed suppression to canary plus User-Agent and grouped incidents by canary ID. Every source remains stored; two clients with the same canary and UA share the suppression window. Proxy trust stays disabled.

The release now persists the observation before triage, isolates both delivery attempts, removes raw SDK error text from diagnostics, and excludes repeated rows from both analytic rules. [Release validation](VALIDATION.md) records the deployed results and continuous Word test without changing the original evidence.

## Closing the Word-to-cloud gap

Opened a newly generated DOCX in Word with its external image pointing to the deployed receiver. Word requested the pixel at `2026-09-08T00:29:38.667730Z`. I matched event `762163e649744aa4bd129ef081e1db4d` across Table Storage and Log Analytics, then matched the Sentinel alert to **High incident 17**. Office and endpoint policies stayed unchanged.

The same release test sent three controlled non-scanner callbacks and two scanner callbacks. Six total events, including Word, reached storage and Log Analytics. Sentinel created two High incidents and one Medium scanner incident. The three repeat rows stayed searchable, with repeat counts 1, 2, and 1, and created no extra alerts. The [cloud evidence](docs/evidence/public/upgrade/README.md) contains the event-to-incident joins.

## Scope of the result

The evidence now includes the original separate tests and a continuous Word-to-Sentinel run. It does not identify the person behind a callback, prove document exfiltration, or cover every Office and network policy. [Operational limits](LIMITATIONS.md) and [viewer coverage](COMPATIBILITY.md) keep those boundaries explicit.

[View the screenshots](docs/evidence/public/README.md) · [Run the project](docs/SETUP.md) · [Test details](TESTING.md)
