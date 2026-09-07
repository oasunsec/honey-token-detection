# Limitations

- A callback requires network access and a viewer that resolves the external DOCX relationship.
- Protected View, Office external-content policy, proxy controls, DNS, or endpoint security may block the request.
- The callback proves that the canary resource was requested; it does not prove a human read the document or that a compromise occurred.
- Source IP may represent NAT, VPN, a corporate proxy, a mobile carrier, or a security scanner.
- A knowledgeable adversary can inspect or remove an external relationship.
- Table Storage is durable project evidence but is not a tamper-evident forensic store.
- The outbox records delivery state. Failed deliveries require manual investigation; there is no automatic retry worker.
- Management APIs are intentionally unavailable in Azure receiver-only mode; provisioning uses an authenticated local operator process.
