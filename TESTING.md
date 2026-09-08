# Tests exercised

The original baseline passed nine tests; the Azure integration reached 16. The detection upgrade adds structured metadata, privacy, migration, and delivery-isolation coverage. The [release report](VALIDATION.md) records the final count and CI run.

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

The original Azure run used controlled HTTPS callbacks; the original Word run used loopback. Release 0.2.2 added a real Word request to the public Azure receiver and matched its event to High Sentinel incident 17. [Viewer coverage](COMPATIBILITY.md) and [operational limits](LIMITATIONS.md) describe the remaining untested paths.

## Detection engineering regressions

[Detection tests](tests/test_detection.py) cover structured first/scanner triage, actual repeat counts, ingestion payloads, UUID event IDs, ingestion failures, observation persistence before triage, delivery-status write failure, malformed tokens, User-Agent token leakage, receiver-only schema hiding, forwarded-header rejection, repeat-window expiry, proxy peer rotation, Azure lookup failures, and additive SQLite migration.

Concurrency ordering, historical error redaction, and SMTP certificate verification have dedicated regressions. The final suite passed **43 tests** locally and in GitHub Actions.

The existing real loopback SMTP test remains in the suite. It sends through triage and persistence, receives one message for two callbacks, and checks the hashed canary ID and analyst context. Adapter tests use a captured upload call; they are not presented as Azure execution.

## Run the suite

From the repository root, after installing dependencies:

```bash
pytest -q
```

Tests are under `tests/`. The SMTP integration test starts an ephemeral loopback sink and uses no external credentials.
