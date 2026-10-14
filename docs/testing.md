# Tests

The project has local unit, integration, Azure adapter, and SMTP tests. The final run passed **43 tests**.

| Area | What is covered |
| --- | --- |
| Callback handling | First hits, scanner-like requests, repeats, revoked tokens, and malformed tokens. |
| Decoys | DOCX external image relationships and filename validation. |
| Access control | Management API keys, loopback access, non-ASCII keys, and receiver-only routes. |
| Delivery | Console and loopback SMTP alerts, suppressed repeats, and SMTP failures. |
| SIEM data | Event IDs, triage fields, repeat counts, ingestion status, raw-token removal, and Azure adapter payloads. |
| Storage | Save-before-triage behavior, failed status writes, migrations, and concurrent callbacks. |

The local Word test uses the loopback receiver. The cloud Word test opened a document that called the public Azure receiver and matched the event to High Sentinel incident 17. Viewer behavior depends on Office and endpoint policy.

## Run the suite

From the repository root, after installing dependencies:

```bash
pytest -q
```

The SMTP integration test uses an ephemeral loopback sink and no external credentials.
