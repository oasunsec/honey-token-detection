# Security notes

This repository is intended for authorized defensive-security testing and deception controls.

- Use synthetic decoy content only. Do not place real payroll, customer, financial, or authentication data inside bait files.
- A callback source IP may represent a NAT gateway, VPN, proxy, DNS resolver, email-security scanner, or sandbox. Do not use it alone to identify a person.
- Callback-based tokens can fail when a host is offline, air-gapped, in Protected View, or configured to block external content.
- Set `CANARY_MANAGEMENT_API_KEY` before exposing the management API beyond a lab network. Without a key, management routes accept loopback clients only; the callback route remains public by design.
- Terminate TLS in front of the service for non-local deployments.
- Decoy filenames are restricted to plain file names so a malformed management request cannot escape the selected output directory. Keep the output directory itself controlled and writable only by the service account.
- Keep secrets out of source control.
- Alert failures are recorded on the event with a bounded error string, but the event store is not tamper-evident and should be protected and retained according to deployment policy.

Report defects privately to the repository owner before public disclosure.
