# Receiver boundaries and event records

The implementation separated collection from management. `/t/{token_id}/pixel.gif` accepted active token callbacks without a management key. Without a configured key, local `/api/*` routes accepted only loopback clients. Once a key was configured, every management request required it, including loopback requests. The deployed receiver disabled those routes altogether.

Each stored event contained the token association, UTC timestamp, source IP, User-Agent, request path, classification, severity, repeat flag, and delivery status. Notification errors were stored as bounded diagnostic text. The SIEM adapter excluded the raw token and path and sent a hashed identifier instead.

The repeat test stored both callbacks and suppressed the second notification. The scanner request received medium severity. The tests did not correlate either event with Entra, endpoint, or file-audit logs, so no user attribution was established.

[Architecture diagram](../ARCHITECTURE.md) · [Security controls](../SECURITY.md)
