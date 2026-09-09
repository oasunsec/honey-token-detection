# Validation results

The local tests ran on 7 September 2026. The final cloud events were recorded on 8 September UTC. The saved [cloud evidence](docs/evidence/public/upgrade/README.md) includes the event IDs and incident links.

## Main results

- Word opened a generated DOCX and requested the Azure callback image.
- Six cloud callbacks became six stored events and six Log Analytics rows.
- Two non-scanner first hits created High incidents.
- One scanner first hit created a Medium incident.
- Three repeat callbacks were stored, kept their repeat counts, and created no extra alerts.
- All 11 KQL files ran against the deployed workspace.
- The receiver health check returned 200. Management, docs, and OpenAPI routes returned 404 in receiver-only mode.
- The local SMTP sink accepted one message after two callbacks.

## Tests

`pytest -q` passed **43 tests**, with two dependency deprecation warnings. Bicep compilation passed. [GitHub Actions](https://github.com/oasunsec/honey-token-detection/actions/runs/34173877877) passed the test/infrastructure job and the history secret scan.

The tests cover token and decoy creation, scanner and repeat decisions, persistence order, revoked tokens, DOCX relationships, authentication, receiver-only routes, SMTP delivery, delivery failures, ingestion fields, raw-token removal, migration, and concurrent callbacks.

## Sentinel results

| Scenario | Stored / ingested | Notification | Incident |
| --- | --- | --- | --- |
| Controlled non-scanner | 3 / 3 | First sent; two repeats suppressed | 18, High |
| Controlled scanner | 2 / 2 | First sent; repeat suppressed | 16, Medium |
| Word cloud request | 1 / 1 | Sent | 17, High |

The event contract includes the time, event ID, hashed canary ID, filename, connection details, triage decision, repeat flags, alert status, and receiver version. It does not include the raw callback token.

## SMTP and Azure

The [SMTP transcript](docs/evidence/public/upgrade/smtp-result.txt) shows two callbacks, two saved events, one accepted message, and one suppressed repeat. Cloud SMTP was not configured.

The Word event came from opening the document, not from a separate controlled request to that token. The [Word evidence](docs/evidence/public/upgrade/README.md#word-to-sentinel) shows the matching records.

## Limits

The documents use synthetic data. A callback does not identify who opened a file or prove exfiltration. Scanner detection is a heuristic, and incident grouping was checked only for the recorded run.
