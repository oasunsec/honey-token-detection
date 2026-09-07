# Operational limits

## Collection and attribution

The DOCX callback depends on the viewer loading the external image relationship and having network access. Protected View, external-content policy, proxies, DNS controls, endpoint security, or document rewriting can block it.

The receiver stores the source IP observed at the ingress, User-Agent, timestamp, request path, triage result, severity, repeat decision, and delivery status. That source IP may belong to a NAT gateway, VPN, proxy, or scanner. The project did not correlate the event with identity, endpoint, or file-audit telemetry, so it cannot identify who opened the document or prove exfiltration.

## Delivery and storage

Delivery is synchronous. A failed notification is recorded, but no retry worker was implemented. Duplicate suppression is best effort across concurrent receiver instances and does not provide atomic suppression across instances.

Azure Table Storage retains events and delivery outcomes. No tamper-evident archive or project retention policy was implemented.

## Cloud deployment

The receiver uses Azure HTTPS ingress without a project-level rate limiter or WAF. Management routes are disabled in the deployed receiver, while provisioning remains a local operator action.

The Sentinel rule runs every five minutes with a ten-minute lookback. It selects all `canary_trigger` rows, including scanner and repeat events, and assigns the rule's configured high severity. Receiver notification suppression does not suppress Sentinel rule evaluation; overlapping windows can select an event again.

## Coverage

SMTP was exercised against a local test sink. Cloud SMTP was not configured. [COMPATIBILITY.md](COMPATIBILITY.md) records viewer coverage, and [COST_AND_TEARDOWN.md](COST_AND_TEARDOWN.md) records the resource lifecycle and cost status.
