# Starting point — 7 September 2026

The local FastAPI service already created and disabled tokens, generated HTML/DOCX decoys, stored callbacks in SQLite, classified scanner-like requests, suppressed repeat notifications, and rendered console/SMTP alerts. Docker and a GitHub Actions test workflow were present.

The baseline suite passed nine tests with two dependency warnings. Python compilation passed. There was no Azure Table backend, receiver-only cloud deployment, or Azure Monitor/Sentinel adapter.

The cloud work added those components while retaining the local generator and SQLite path. A dedicated resource group was used instead of the existing training resource groups. Subscription, tenant, and operator identifiers were excluded from this record.
