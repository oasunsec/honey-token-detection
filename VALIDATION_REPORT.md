# Validation report

**Run date:** 2026-09-07  
**Environment:** Windows 11, Python 3.13.14, private working copy  
**Scope:** Authorized local lab validation of the canary-honeytoken MVP

## Executive result

The core hypothesis was demonstrated in a local lab. A generated decoy callback returned the transparent GIF, created a SQLite event, ran the triage rule, produced an alert from the triaged event, and left the event available through `/api/events`. Console alerting and delivery to a loopback SMTP test sink both worked, with the persisted event recording `alert_status=sent`. Duplicate callbacks remained persisted while only the first matching event was alert-worthy. An obvious scanner User-Agent was classified as medium severity. Disabled tokens returned 404. Management routes now require the configured API key for remote use and record alert failures as evidence.

The DOCX packages contained the intended unique external relationship, but no Microsoft Word or LibreOffice viewer was installed in this environment, so viewer-side retrieval was not tested. The callback therefore must not be treated as guaranteed for every document open.

## Tests and observed results

| Check | Result |
| --- | --- |
| Dependency installation | Passed in `.venv` with `requirements.txt` |
| `pytest -q` | **6 passed, 2 deprecation warnings** after configuring an ignored repo-local pytest temp root |
| FastAPI process | Uvicorn started successfully on loopback |
| `/health` | HTTP 200, `{"status":"ok"}` |
| Required decoy names | Created `Synthetic_Forecast.docx` and `Executive_Bonus_2027.docx` with the CLI |
| Callback response | HTTP 200 with `image/gif` and no-cache headers |
| Event persistence | SQLite row with `event_type=canary_trigger`, UTC time, token, path, source IP and User-Agent |
| Triage | Normal lab request classified high with `Honeytoken trigger - potential unauthorized access` |
| Console alert | Printed the filename, severity, event time, source IP, User-Agent, token, and triage reason |
| Duplicate suppression | Both callbacks were logged; the second event had `duplicate=1` and did not emit a second alert |
| Scanner heuristic | `curl/8.10` was classified `Possible automated scanner interaction` with medium severity |
| Token disable | Disabled token callback returned HTTP 404 |
| DOCX package | Both `word/_rels/document.xml.rels` files contained the correct unique callback URL with `TargetMode="External"` |
| Management protection | Missing key returned 401 when configured; remote access without a key returned 503; valid key returned 200; `/health` stayed public |
| Alert outcome evidence | Events recorded `sent`, `suppressed`, `disabled`, or `failed`; a safe SMTP failure test persisted the bounded error |

The first unmodified `pytest -q` attempt hit `PermissionError: [WinError 5]` while pytest scanned the host's ACL-protected `C:\Users\oasun\AppData\Local\Temp\pytest-of-oasun`. The repository now uses `.pytest-tmp/`, which is ignored and makes the documented command pass on this host. This was an environment failure rather than an application test failure.

## SMTP result

SMTP rendering and delivery were tested against a temporary loopback SMTP server implemented only for this validation run. It listened on `127.0.0.1` on an ephemeral port, accepted the message for `qa-inbox@local.test`, and captured it in memory. STARTTLS and authentication were disabled for this isolated sink; no real mailbox, password, API key, or external SMTP provider was used. The received message contained the decoy filename, severity, event time, source IP, User-Agent, token identifier, and triage reason. The alert went through the normal triage and duplicate decision path.

## DOCX behavior

The generated OOXML relationship was inspected directly from each ZIP package and pointed to that token's callback URL. No compatible Word or LibreOffice viewer was available on the validation host, so whether a viewer requested the URL was not observed. Protected View, external-content policy, proxies, firewalls, offline hosts, and viewer behavior can block the request; no control was bypassed.

## False positives and limitations

- A scanner or link-protection service can request the resource. The simulated `curl/8.10` request was recorded and downgraded to medium, but it still produced an alert because the MVP treats medium events as alert-worthy.
- Preview services, sandboxes, authorized administrators, NAT gateways, VPNs, proxies, and DNS/security infrastructure can generate events or obscure the originating identity.
- A callback proves that the unique resource was requested. It does not prove that a human opened the file, that data was exfiltrated, or that the source IP identifies an attacker.
- An offline or air-gapped host, copied file, or viewer that blocks external content may never produce a callback.
- The callback endpoint intentionally has no authentication; the token is the tripwire identifier. Management routes require `X-Canary-API-Key` when configured and otherwise accept loopback clients only; role separation and rate limiting are still absent.
- SMTP connection or authentication failure still causes the callback request to fail so delivery problems are visible, but the event now persists `alert_status=failed` and a bounded error for diagnosis.

## Security weaknesses and changes

The management API now has an API-key/loopback boundary, but still needs role separation, rotation through a secret store, rate limiting, TLS deployment, and a management audit trail before exposure beyond a controlled lab. SQLite is a local evidence store, not an encrypted or tamper-evident archive. Retention, access control, and backup protection still belong to the deployment. `CANARY_TRUST_PROXY_HEADERS` must only be enabled behind a trusted proxy. Filename path components are rejected to prevent decoy generation from escaping its selected output directory; the output directory itself must still be controlled by the operator.

The project does not provide encryption, DLP, least privilege, endpoint controls, removable-media controls, or SIEM correlation. Those controls remain necessary prevention and investigation layers.

## Git and secret-history review

The working tree and every committed revision were inspected with Git status, `git diff --check`, history-aware pattern searches, and review of tracked paths. No real credentials, `.env` files, runtime databases, logs, generated decoys, virtual environments, or local caches are tracked. `.gitignore` covers those classes. `gitleaks` was not installed, so the history check was manual and documented here.

## GitHub result

The repository is private at [oasunsec/canary-honeytoken-detection](https://github.com/oasunsec/canary-honeytoken-detection), with `main` tracking the pushed local branch. GitHub verified `private=true` before the first push. The first Actions run failed during test collection because the `pytest` executable did not include the repository root on `sys.path` (`ModuleNotFoundError: No module named 'app'`); that failure was reproduced locally and fixed with `pythonpath = .` in `pytest.ini`. The corrective commit `7cd171e` passed the exact CI command in [Actions run 34098455507](https://github.com/oasunsec/canary-honeytoken-detection/actions/runs/34098455507). The earlier failed run remains visible as [34098248436](https://github.com/oasunsec/canary-honeytoken-detection/actions/runs/34098248436) and is explained here rather than hidden.

## Recommendation

Continue the project as a private defensive-security MVP. Before any public release or non-lab deployment, add management-plane authentication and authorization, TLS and trusted-proxy guidance, alert-delivery evidence, retention/integrity controls, a trusted scanner policy, and a controlled Word/Office viewer test. The current evidence supports code review of the MVP; it does not support treating a callback as guaranteed detection or using the service as a standalone preventive control.

## Final release status

`READY_FOR_PUBLIC_REVIEW`
