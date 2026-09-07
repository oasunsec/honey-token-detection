# Validation report

**Run date:** 2026-09-07
**Environment:** Windows 11, Python 3.13.14, Azure `southcentralus`, private GitHub repository
**Scope:** Authorized defensive canary validation from the existing MVP codebase

## Results

Controlled HTTP requests exercised the cloud receiver path:

`Controlled HTTP callback -> public HTTPS Container App -> Azure Table Storage event -> triage -> console alert decision -> DCR ingestion -> CanaryHit_CL -> scheduled Sentinel rule -> Sentinel incident`

The Azure receiver returned HTTP 200 with the transparent GIF, persisted the event in the project Table Storage, ran the existing triage code, emitted the normal console alert, sent a normalized record through the resource-specific DCR endpoint, and produced a Sentinel incident. The receiver also preserved evidence when the first DCR configuration was wrong: that event remains durable with `sentinel_status=failed` and a bounded DNS error. The endpoint was corrected to use the DCR endpoint emitted by Azure, and subsequent events ingested successfully.

Word retrieval was tested separately against a local loopback receiver. A Word-to-Azure test was not performed.

## Tests and observed results

| Check | Result |
| --- | --- |
| Dependency installation | Passed in `.venv` from `requirements.txt` |
| `pytest -q` | **16 passed, 2 deprecation warnings** |
| Bicep compile | Passed; only known BCP318 nullable conditional output warning remains |
| Azure resource deployment | Passed for the dedicated project resource group |
| Managed identity RBAC | Verified `AcrPull`, `Storage Table Data Contributor`, and `Monitoring Metrics Publisher` on project scopes |
| Runtime identity cleanup | Temporary local operator Table role removed after seeding and inspection; remaining count verified as zero |
| Public `/health` | HTTP 200; receiver reports `receiver_only=true` and `storage_backend=azure_table` |
| Public management API | `/api/events` returned HTTP 404 from the receiver-only Container App |
| Office-like callback | HTTP 200 with 34-byte `image/gif`; Azure event persisted, triaged high, console alert sent, DCR status sent |
| Scanner callback | HTTP 200; `curl/8.10.1` classified `Possible automated scanner interaction` with medium severity, alert sent, DCR status sent |
| Duplicate callback | HTTP 200; event persisted with `duplicate=true`, alert status `suppressed`, DCR row `FirstHit=false`, `RepeatCount=1` |
| Disabled token | HTTP 404; token was re-enabled after the negative test |
| Azure Table evidence | Five events persisted, including the initial DCR failure and four post-fix events |
| Log Analytics evidence | Four post-fix rows present in `CanaryHit_CL` with normalized fields and no raw callback token |
| Sentinel analytic rule | Deployed as `Canary document access detected`, five-minute frequency, ten-minute lookback, incident creation enabled |
| Sentinel incident | A new incident was observed with title `Canary document access detected`, severity `High`, and status `New` |
| DOCX package | OOXML relationship pointed to the unique token callback with `TargetMode="External"` |
| Word viewer | Word 16.0.20326.20132 rendered a locally generated DOCX and requested its loopback callback; event and console alert persisted |
| Local SMTP test | Passed against an ephemeral loopback sink through the normal triage and alert path; no external mailbox or credential used |
| Azure SMTP alert | Not configured; Azure validation used console alerts and recorded that limitation |

An initial pytest run failed during discovery because the host denied access to its temporary directory. The ignored `.pytest-tmp/` directory and explicit `tests/` discovery scope resolved collection; application assertions then passed.

## Cloud flow evidence

The dedicated resource group was `rg-canary-cloudsec-validation` in `southcentralus`. It contains the project ACR, managed identity, Container Apps environment and receiver, Standard LRS Table Storage, Log Analytics workspace, `CanaryHit_CL`, Direct DCR, Sentinel onboarding, and the scheduled analytic rule.

The first callback used the pre-fix regional hostname and persisted a failure with:

```text
Failed to resolve 'southcentralus-1.ingest.monitor.azure.com'
```

The Bicep deployment now injects `dcr.properties.endpoints.logsIngestion`, which resolved to the resource-specific DCR endpoint. The next four events were accepted by the DCR and appeared in `CanaryHit_CL`. This failure was fixed in code and retained in the evidence record rather than removed.

The normalized Log Analytics payload contains `TimeGenerated`, `EventType`, hashed `CanaryId`, `ArtifactName`, `SourceIp`, `UserAgent`, `Classification`, `FirstHit`, `RepeatCount`, `Receiver`, `NotificationStatus`, and `EventId`. The raw callback token and request path are not sent to the DCR.

## SMTP result

The local SMTP test used an ephemeral loopback server that accepted a message for `qa-inbox@local.test` and captured it in memory. STARTTLS and authentication were disabled only for this isolated sink. The message contained the filename, severity, event time, source IP, User-Agent, hashed canary identifier, and triage reason. Azure was intentionally left in console-alert mode because no real mailbox or SMTP secret was supplied.

## DOCX behavior

The generated DOCX package was inspected as an OOXML ZIP. Its external relationship targeted the token-specific callback URL and used `TargetMode="External"`. Word version 16.0.20326.20132 rendered the synthetic document and requested the token URL at 2026-09-07T18:27:35.267154+00:00. The recorded User-Agent was `Mozilla/4.0 (compatible; ms-office; MSOffice 16)`, severity was high, and console alert status was sent. This was a local-file to loopback test under existing settings, not a Protected View or cloud Word test. Protected View, Office external-content policy, proxies, firewalls, offline hosts, and viewer behavior can prevent a callback; no control was bypassed.

## False positives and limitations

- Security scanners and link-protection services can request the resource. The scanner test was downgraded to medium but remained alert-worthy by design.
- Preview services, sandboxes, administrators, NAT gateways, VPNs, proxies, and DNS/security infrastructure can create events or obscure the originating identity.
- A callback proves that the unique resource was requested. It does not prove a human opened the document, that data was read, or that data was exfiltrated.
- Offline or air-gapped hosts, copied files, and viewers that block external content may never produce a callback.
- The callback endpoint is intentionally unauthenticated because the token is the tripwire. The public receiver has no rate limiter, custom domain, WAF, gateway, or separate management plane.
- Table Storage is durable project evidence, not a tamper-evident forensic archive. The outbox is persisted but no retry worker was added.
- Azure SMTP delivery was not exercised; console delivery was used for the cloud run.
- The scheduled Sentinel rule adds evaluation delay of up to its five-minute frequency and depends on Log Analytics ingestion.

## Security changes and remaining weaknesses

The Azure runtime uses a user-assigned managed identity. Storage shared-key access and ACR admin credentials are disabled. Management routes are unavailable in receiver-only mode, and provisioning remains local. The DCR payload excludes raw callback secrets. A failed alert or failed DCR call is persisted with a bounded diagnostic rather than dropping the event.

Remaining work before a production or broadly exposed deployment includes a real secret-store-backed management policy, rate limiting, trusted proxy/TLS guidance, retention and integrity controls, scanner allowlisting, broader Word/Office policy compatibility testing, and operational alert retry. The project still does not provide encryption, DLP, EDR, endpoint controls, removable-media controls, or identity correlation.

## Git and secret-history review

Gitleaks v8.30.1 found no secrets in the tracked history or public evidence files during the 2026-09-07 review. Runtime databases, raw callbacks, generated decoys, logs, `.env` files, and `evidence-private/` are excluded from Git. Private runtime records contain live tokens and are excluded from the downloadable evidence package.

## GitHub result

The repository remains private at [oasunsec/canary-honeytoken-detection](https://github.com/oasunsec/canary-honeytoken-detection). The screenshot-package checkpoint `fd06b0a` passed [GitHub Actions run 34154930533](https://github.com/oasunsec/canary-honeytoken-detection/actions/runs/34154930533). Later runs are listed in [Actions](https://github.com/oasunsec/canary-honeytoken-detection/actions).

## Teardown

The project-specific teardown script is prepared but has not been run. It requires an explicit `-Confirm` flag and deletes only `rg-canary-cloudsec-validation`. The resource inventory, Log Analytics query output, Sentinel incident, Table evidence, and GitHub status should be retained before any teardown decision.

## Recommendation

Continue as an experimental detection project. The local Word callback, SMTP sink test, and cloud receiver-to-Sentinel path passed under the conditions above. Production deployment still needs retry handling, ingress controls, retention, and broader viewer testing. Repository visibility remains private pending the owner's publication decision.

## Final release status

`READY_FOR_PUBLIC_REVIEW`

## Fixes verified on 2026-09-07

- Baseline: 13 tests passed. Final local suite: 16 passed, with two upstream
  TestClient deprecation warnings. The real loopback SMTP integration test
  received one triage-derived email for two callbacks; both events persisted.
- Fixed SMTP failure handling: a persisted hit still returns the GIF, and an
  independent Sentinel adapter still runs with `NotificationStatus=failed`.
  Regression tests cover this failure path. Unconfigured ingestion is disabled,
  not indefinitely pending.
- Fixed non-ASCII management header comparison so malformed credentials return
  401 instead of causing a server error; regression test passes.
- Docker build context now allowlists source files, Compose binds to loopback,
  and the container disables access logs containing callback tokens. README
  uses the same logging option and shows the actual health response.
- A scan staging copy initially caused duplicate pytest module collection;
  `testpaths = tests` now keeps private evidence outside test discovery.
- Prior Azure Table, DCR, and Sentinel evidence above is retained from the prior
  run. This follow-up did not redeploy cloud resources or configure cloud SMTP.
- Automatic retries, distributed atomic deduplication, retention, WAF/rate limits,
  and tamper-evident storage remain operational limitations of this MVP.
