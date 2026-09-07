# Receiver boundaries and event records

The receiver separates collection from management. `/t/{token_id}/pixel.gif` accepts an active callback without a management key. With no configured key, local `/api/*` routes accept loopback clients only; once a key is configured, every management request requires it, including loopback requests. The deployed receiver disables those routes altogether.

Each event stores the token association, UTC timestamp, source IP, User-Agent, request path, classification, severity, repeat flag, and delivery status. Notification errors are bounded diagnostic text. The SIEM adapter removes the raw token and path and sends a hashed identifier instead.

The repeat test stored both callbacks and suppressed the second notification. The scanner request received medium severity. Neither event was correlated with Entra, endpoint, or file-audit logs, so no user attribution was established.

[Architecture diagram](../ARCHITECTURE.md) · [Security controls](../SECURITY.md)
