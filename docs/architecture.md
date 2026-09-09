# Receiver details

The callback route is `/t/{token_id}/pixel.gif`. Management routes require the configured API key. When no key is set, they are limited to loopback clients. Receiver-only deployments return 404 for management, docs, and OpenAPI routes.

For each callback, the receiver:

1. saves the observation;
2. calculates the first-hit, repeat, and scanner fields;
3. saves the triage decision;
4. tries console or SMTP delivery; and
5. tries Logs Ingestion separately.

A delivery failure does not remove the event or stop the GIF response. Status-write failures log an exception category.

SQLite migrations add new columns without changing old events. Azure events include a UUID for SIEM correlation. Delivery status is saved on the event; the provisioned outbox table is unused.

The event includes the classification, severity, scanner flag, repeat data, reason, and recommended action. Public API output and SIEM records use a hashed canary ID. Stored request paths are redacted.

[Architecture](../ARCHITECTURE.md) - [Sentinel fields](../SENTINEL.md)
