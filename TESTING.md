# Tests exercised

The local baseline passed nine tests. After the Azure adapters and failure-handling fixes, the suite passed 16 tests with two dependency deprecation warnings.

| Scenario | Observed result |
| --- | --- |
| Callback, scanner, repeat, and revoked token | Callbacks were stored; scanner requests received medium severity; repeats were suppressed; revoked tokens returned 404 |
| DOCX generation | The package contained an external image relationship; malformed filenames were rejected |
| Management authentication | Unauthenticated remote requests were rejected; non-ASCII credentials returned 401 |
| Receiver-only routing | Management endpoints returned 404 |
| SMTP sink | The loopback sink accepted one SMTP `DATA` message after two callbacks; two events persisted with `sent` and `suppressed` alert states ([test](tests/test_smtp_delivery.py), [transcript](docs/evidence/public/13-evidence.html)) |
| SMTP failure | The event retained a failed status, the response remained a GIF, and Sentinel ingestion was attempted |
| Missing Sentinel adapter | Ingestion status was recorded as disabled |
| Event redaction | Public event output excluded raw callback identifiers |

The Azure run used controlled HTTPS callbacks and produced Table records, Log Analytics rows, and a Sentinel incident. The separate Word run retrieved a loopback callback from a generated local DOCX. [Viewer coverage](COMPATIBILITY.md) and [operational limits](LIMITATIONS.md) describe the untested paths.

## Run the suite

From the repository root, after installing dependencies:

```bash
pytest -q
```

Tests are under `tests/`. The SMTP integration test starts an ephemeral loopback sink and uses no external credentials.
