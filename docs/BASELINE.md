# Starting point - 7 September 2026

The local FastAPI service already created and disabled tokens, generated HTML and DOCX decoys, stored callbacks in SQLite, classified scanner-like requests, suppressed repeats, and rendered console or SMTP alerts. Docker and a GitHub Actions test workflow were already present.

The baseline suite passed nine tests with two dependency warnings. Python compilation passed. Azure Table Storage, receiver-only cloud mode, and the Azure Monitor/Sentinel adapter were the missing pieces.

The cloud work added those pieces while retaining the local generator and SQLite path. A dedicated resource group kept the run separate from existing training resources. Subscription, tenant, and operator identifiers are excluded from this record.
