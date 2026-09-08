# Receiver boundaries and event records

Active callbacks use `/t/{token_id}/pixel.gif`. Management requires a configured key or loopback access when no key is set. Receiver-only deployments return 404 for management, docs, and OpenAPI.

The receiver commits an observation with pending triage, computes classification and matching-window metadata, and persists that decision. It attempts console/SMTP delivery, records the outcome, then independently attempts Logs Ingestion. Downstream failures preserve the event and pixel response. Status-write failures log only an exception category.

SQLite migrations add columns without changing historical events. Azure Table adds properties to new events. Each new observation has a UUID for SIEM correlation. Delivery outcomes live on event rows; the provisioned outbox table is unused.

`classification`, `severity`, `is_scanner`, `reason`, and `recommended_action` describe triage. `duplicate`, `first_hit`, and `repeat_count` describe the rolling token/UA window. The token association stays private; event API output and SIEM use a hashed ID. Stored request paths are redacted.

[Architecture](../ARCHITECTURE.md) · [SIEM contract](../SENTINEL.md) · [Security](../SECURITY.md)
