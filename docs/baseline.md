# Starting point - 7 September 2026

Before the Azure work, the local FastAPI app could:

- create and disable tokens;
- generate HTML and DOCX decoys;
- save callbacks in SQLite;
- mark scanner-like requests;
- suppress repeat alerts; and
- send console or SMTP alerts.

The baseline test run passed nine tests. Docker and GitHub Actions were already set up.

The missing pieces were Azure Table Storage, a cloud receiver-only mode, and the Microsoft Sentinel adapter.
