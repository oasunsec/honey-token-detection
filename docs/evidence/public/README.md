# Canary lab: screenshot walkthrough

This portfolio documents an authorized defensive canary lab from baseline to release review. Four images are fresh application captures (Word and GitHub). The remaining images are clearly labelled views of saved records, design, or fresh command output. They are not original Azure portal screenshots. No before-deployment or teardown screenshot was recovered or invented. Teardown was not performed.

PII handling: account details, tenant/subscription IDs, emails, IP addresses, raw callback tokens and resource endpoints are omitted, replaced by labelled redactions, or excluded through capture boundaries. Only this public folder is included in the ZIP; raw private records and excluded screenshots are not included.

## 01. Purpose and architecture

**Design summary** — Source: `ARCHITECTURE.md + CODEX_TASK.md`.

Detect interaction in an authorized lab. A callback is a signal, not proof of exfiltration or identity.

![Purpose and architecture](01-evidence.jpg)

## 02. Starting state and baseline

**Archived record, captured 2026-09-07** — Source: `00-azure-start-state.json + docs/BASELINE.md`.

Shows the recorded starting point. This is a view of archived records, not an original portal screenshot.

![Starting state and baseline](02-evidence.jpg)

## 03. Infrastructure deployment

**Archived Azure deployment response** — Source: `03-bicep-final-deployment.json`.

Records the actual deployment result while withholding subscription, tenant, principal and endpoint values.

![Infrastructure deployment](03-evidence.jpg)

## 04. Receiver security configuration

**Source configuration evidence** — Source: `infra/main.bicep`.

Shows checked-in controls. Role configuration alone does not prove a fresh live access review.

![Receiver security configuration](04-evidence.jpg)

## 05. Deployed receiver health

**Archived HTTP result** — Source: `09-container-app-health.json`.

HTTP 200 with receiver-only mode and Azure Table storage in the saved deployment validation.

![Deployed receiver health](05-evidence.jpg)

## 06. Word renders the synthetic decoy

**Fresh Microsoft Word UI capture** — Source: `Word 16.0.20326.20132`.

The generated DOCX renders in Word. Account controls are cropped out. Callback proof is the separately saved event in image 07; reopening for this screenshot is not claimed as a new end-to-end run.

![Word renders the synthetic decoy](06-word-decoy.png)

## 07. Word callback and triage

**Archived event from observed Word open** — Source: `word-viewer-result.json`.

Word 16.0.20326.20132 requested the local callback under existing settings. This does not establish Protected View or remote HTTPS behavior.

![Word callback and triage](07-evidence.jpg)

## 08. Durable events and duplicate suppression

**Archived Azure Table query** — Source: `table-events-sanitized.json`.

Saved Azure Table rows retain alert and ingestion outcomes, including scanner severity. These rows are not duplicates; suppression is verified by the regression tests.

![Durable events and duplicate suppression](08-evidence.jpg)

## 09. Log Analytics ingestion

**Archived CanaryHit_CL query** — Source: `log-analytics-latest.json`.

Saved query rows connect receiver events to the SIEM ingestion path. Raw callback tokens and source IPs are excluded.

![Log Analytics ingestion](09-evidence.jpg)

## 10. Sentinel analytic rule

**Archived rule configuration** — Source: `sentinel-rule.json`.

Shows scheduled detection logic and incident creation configuration. The evaluation schedule introduces delay.

![Sentinel analytic rule](10-evidence.jpg)

## 11. Sentinel incident

**Archived Sentinel incident response** — Source: `sentinel-incidents.json`.

Actual saved incident response; owner, incident URL, related resource IDs and tenant identifiers are omitted.

![Sentinel incident](11-evidence.jpg)

## 12. GitHub main CI status

**Fresh capture of completed GitHub run** — Source: `Actions run 34152044446, commit 2858824`.

The completed main-branch run reports Success. Account details and navigation are excluded from the crop.

![GitHub main CI status](12-github-ci-status.jpg)

## 13. GitHub test job

**Fresh GitHub UI capture** — Source: `Actions run 34152044446`.

The workflow graph shows a successful test job. This is a cropped view of the actual GitHub page.

![GitHub test job](13-github-test-job.jpg)

## 14. GitHub pytest log

**Fresh GitHub UI capture** — Source: `Job 101836165394 in Actions run 34152044446`.

The actual pytest log shows completed assertions and dependency warnings. The full local summary is also visible in image 15.

![GitHub pytest log](14-github-pytest-output.jpg)

## 15. Local regression and SMTP delivery

**Fresh verification output** — Source: `portfolio/pytest.txt + tests/test_smtp_delivery.py`.

The suite includes a real ephemeral loopback SMTP sink, triage-field verification, duplicate suppression, and notification-failure isolation. No external mailbox credentials are used.

![Local regression and SMTP delivery](15-evidence.jpg)

## 16. Secret-history verification

**Fresh Gitleaks output** — Source: `portfolio/gitleaks.txt`.

The tracked Git history scan passed. Live canary evidence remains private and ignored; a clean history does not imply the whole local disk has no secrets.

![Secret-history verification](16-evidence.jpg)

## 17. Release boundary and teardown

**Documented final state** — Source: `VALIDATION_REPORT.md + COST_AND_TEARDOWN.md`.

The repository remains private. Publishing source and operating a production service are separate decisions.

![Release boundary and teardown](17-evidence.jpg)
