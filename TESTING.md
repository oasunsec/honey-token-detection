# Tests exercised

The local baseline passed nine tests. After the Azure adapters and failure-handling fixes, the suite passed 16 tests with two dependency deprecation warnings.

| Scenario exercised | Result |
| --- | --- |
| Callback, scanner, repeat, and revoked token | Stored events, scanner classification, suppression, and 404 behavior matched the assertions |
| DOCX generation | Package contained the external image relationship; malformed filenames were rejected |
| Management authentication | Unauthenticated remote requests were rejected; non-ASCII credentials returned 401 |
| Receiver-only routing | Management endpoints returned 404 |
| SMTP sink | One triage-derived email arrived for two callbacks; both events persisted |
| SMTP failure | Event retained a failed status, response remained a GIF, Sentinel ingestion was still attempted |
| Missing Sentinel adapter | Ingestion status was recorded as disabled |
| Event redaction | Public event output excluded raw callback identifiers |

The Azure run used controlled HTTPS callbacks and produced Table records, Log Analytics rows, and a Sentinel incident. The separate Word test retrieved a loopback callback from a generated local DOCX. Cloud SMTP, Word-to-Azure retrieval, Protected View, and other viewers were not exercised.

## Run the suite

From the repository root, after installing dependencies:

```bash
pytest -q
```

Tests are under `tests/`. The SMTP integration test starts its own ephemeral loopback sink and uses no external credentials.
