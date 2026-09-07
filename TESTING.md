# Testing

Local regression tests run with `.\.venv\Scripts\pytest.exe -q` and cover token callbacks, duplicate suppression, scanner triage, disabled tokens, DOCX external relationships, management authentication, receiver-only routing, public event redaction, console/SMTP rendering, and persisted SMTP failures.

The Azure validation sequence is:

1. Deploy the dedicated resource group with `scripts/azure/deploy.ps1`.
2. Seed a DOCX token locally with `CANARY_STORAGE_BACKEND=azure_table`, the storage table URL, and the Azure callback base URL. This uses the operator's Entra login and does not expose management routes.
3. Open the DOCX in a controlled Word endpoint or make a controlled callback request for receiver validation.
4. Confirm HTTP 200, Azure Table persistence, notification delivery, `CanaryHit_CL` ingestion and Sentinel rule/incident evidence.
5. Repeat from a second controlled endpoint and record duplicate/scanner behavior.

Viewer-side callback behavior is recorded as tested, blocked, partial, or not tested. No Office or endpoint policy is bypassed.

The suite includes actual SMTP delivery to a threaded ephemeral loopback sink,
checks triage fields in the received message, and verifies duplicate suppression.
An SMTP outage must preserve a failed status, still return the GIF, and still
attempt independently configured Sentinel ingestion. An absent Sentinel adapter
is recorded as disabled. Run `pytest -q`; collection is restricted to `tests/`
so ignored evidence copies do not become tests.
