# Security notes

This repository is intended for authorized defensive-security testing and deception controls.

- Use synthetic decoy content only. Do not place real payroll, customer, financial, or authentication data inside bait files.
- A callback source IP may represent a NAT gateway, VPN, proxy, DNS resolver, email-security scanner, or sandbox. Do not use it alone to identify a person.
- Callback-based tokens can fail when a host is offline, air-gapped, in Protected View, or configured to block external content.
- Protect the management API before exposing the service beyond a lab network.
- Terminate TLS in front of the service for non-local deployments.
- Decoy filenames are restricted to plain file names so a malformed management request cannot escape the selected output directory. Keep the output directory itself controlled and writable only by the service account.
- Keep secrets out of source control.

Report defects privately to the repository owner before public disclosure.
