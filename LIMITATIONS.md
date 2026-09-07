# Operational limits

## Collection and attribution

The DOCX callback depends on network access and a viewer loading the external image relationship. External-content policy, Protected View, proxies, DNS controls, or endpoint security can block it. The relationship can also be removed from the document.

A stored callback records a resource request. Source IPs can belong to NAT gateways, VPNs, proxies, or scanners. The project did not correlate these records with identity or endpoint telemetry and did not detect data exfiltration.

## Delivery and storage

Delivery remained synchronous. Failed notifications were recorded, but no automatic retry worker was implemented. Duplicate suppression was best effort across concurrent receiver instances; it did not provide atomic suppression across instances.

Azure Table Storage retained events and delivery outcomes. It was not configured as a tamper-evident archive, and no project retention policy was implemented.

## Cloud deployment

The receiver used Azure HTTPS ingress without a project-level rate limiter or WAF. Management routes were disabled in the deployed receiver. Provisioning used a separate local operator process.

The Sentinel rule used a five-minute schedule and ten-minute lookback. It selected all `canary_trigger` rows, including scanner and repeat events, and assigned the rule's configured high severity. Receiver notification suppression did not suppress Sentinel rule evaluation. Overlapping query windows could select the same event again.

## Coverage

SMTP delivery was exercised against a local test sink; cloud SMTP was not configured. [COMPATIBILITY.md](COMPATIBILITY.md) records Word and viewer coverage. [COST_AND_TEARDOWN.md](COST_AND_TEARDOWN.md) records resource lifecycle and cost status.
