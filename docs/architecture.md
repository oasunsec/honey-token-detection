# Architecture notes

## Trust boundaries

The project has two different surfaces:

1. **Trigger plane** — `/t/{token_id}/pixel.gif` must be reachable by the environment being tested. It intentionally does not require authentication because the token itself is the tripwire identifier.
2. **Management plane** — `/api/*` creates tokens, lists telemetry and disables tokens. It accepts loopback clients only when `CANARY_MANAGEMENT_API_KEY` is empty; remote use requires the `X-Canary-API-Key` header. Authentication and TLS remain deployment requirements for internet-facing use.

## Event schema

Each trigger records:

- token ID;
- UTC timestamp;
- observed source IP;
- User-Agent;
- request path;
- `event_type=canary_trigger`;
- triage label;
- severity;
- duplicate flag.
- alert status (`sent`, `suppressed`, `disabled`, or `failed`);
- bounded alert error text when delivery fails.

## Detection semantics

A trigger means **the unique callback resource was requested**. It does not prove:

- a human opened the file;
- the source IP identifies the user;
- data exfiltration occurred;
- the endpoint was compromised.

Those conclusions require correlation.

## Recommended correlation sources

For a Microsoft-heavy environment, useful sources include:

- Entra sign-in logs;
- Microsoft Defender for Endpoint telemetry;
- Purview/endpoint DLP events;
- SharePoint/OneDrive audit events;
- proxy/firewall/DNS telemetry;
- Windows file-access auditing where appropriate.

Equivalent data sources can be used in other stacks.

## False positives

Expected sources include:

- security scanners;
- email/link protection systems;
- sandboxing;
- document preview services;
- legitimate administrators validating the decoy.

The MVP logs every callback but suppresses repeated notifications from the same token/IP/User-Agent tuple within the configured window.

## Data-at-rest control model

This project is intentionally one layer in a broader model:

```text
Encryption at rest
+ least privilege
+ endpoint/removable-media controls
+ endpoint/cloud DLP
+ audit telemetry
+ EDR/SIEM
+ deception canaries
```

The canary adds a high-signal detective control but does not provide confidentiality by itself.
