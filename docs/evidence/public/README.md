# Honey Token — screenshot walkthrough

Project walkthrough recorded on 7 September 2026, covering setup, deployment, document retrieval, event triage, Sentinel ingestion, and tests. Word and GitHub images are application captures. Azure images display saved API and query records, rather than the Azure portal. No teardown was performed.

Account details, email addresses, source IPs, tenant/subscription identifiers, callback tokens, and resource endpoints are redacted or excluded. Raw records remain outside this package.

[Open the offline gallery](index.html). Image hashes are recorded in [captions.json](captions.json).

## Browse the evidence

[Deployment](#03-infrastructure-deployment) · [Word callback](#07-word-callback-and-triage) · [Sentinel incident](#11-sentinel-incident) · [Tests](#15-local-regression-and-smtp-delivery)

## 01. Purpose and architecture

**Design summary** — Source: `ARCHITECTURE.md`.

Extended the local document-token receiver with Azure Table Storage and Sentinel ingestion. Word and cloud callbacks were exercised separately.

![Purpose and architecture](01-evidence.jpg)

## 02. Starting state and baseline

**Archived record, captured 2026-09-07** — Source: `00-azure-start-state.json + docs/BASELINE.md`.

Recorded the local SQLite starting point and nine passing baseline tests before adding the Azure adapters.

![Starting state and baseline](02-evidence.jpg)

## 03. Infrastructure deployment

**Archived Azure deployment response** — Source: `03-bicep-final-deployment.json`.

Deployed the Bicep resources successfully. Resource identifiers and endpoint values are omitted from the saved response.

![Infrastructure deployment](03-evidence.jpg)

## 04. Receiver security configuration

**Source configuration evidence** — Source: `infra/main.bicep`.

Disabled registry admin access and storage shared keys, required HTTPS, and disabled public management routes in the deployment configuration.

![Receiver security configuration](04-evidence.jpg)

## 05. Deployed receiver health

**Archived HTTP result** — Source: `09-container-app-health.json`.

Requested the deployed health endpoint; it returned HTTP 200 with receiver-only mode and Azure Table Storage.

![Deployed receiver health](05-evidence.jpg)

## 06. Word renders the synthetic decoy

**Microsoft Word UI capture** — Source: `Word 16.0.20326.20132`.

Opened the generated synthetic document in Word. The local callback it produced is recorded in image 07.

![Word renders the synthetic decoy](06-word-decoy.png)

## 07. Word callback and triage

**Archived event from observed Word open** — Source: `word-viewer-result.json`.

Captured the Office User-Agent and high-severity event when Word requested the loopback pixel.

![Word callback and triage](07-evidence.jpg)

## 08. Persisted events and delivery outcomes

**Archived Azure Table query** — Source: `table-events-sanitized.json`.

Queried stored events and retained both successful delivery outcomes and the first failed ingestion attempt.

![Persisted events and delivery outcomes](08-evidence.jpg)

## 09. Log Analytics ingestion

**Archived CanaryHit_CL query** — Source: `log-analytics-latest.json`.

Queried four ingested records, including a scanner classification and a suppressed repeat notification.

![Log Analytics ingestion](09-evidence.jpg)

## 10. Sentinel analytic rule

**Archived rule configuration** — Source: `sentinel-rule.json`.

Deployed a five-minute Sentinel rule with a ten-minute lookback and incident creation enabled. The query selected all callback rows; scanner and repeat rows were included.

![Sentinel analytic rule](10-evidence.jpg)

## 11. Sentinel incident

**Archived Sentinel incident response** — Source: `sentinel-incidents.json`.

Recorded the resulting high-severity Sentinel incident. Account and resource identifiers are omitted.

![Sentinel incident](11-evidence.jpg)

## 12. GitHub main CI status

**GitHub UI capture** — Source: `Actions run 34152044446, commit 2858824`.

Captured the completed main-branch CI run after the application fixes.

![GitHub main CI status](12-github-ci-status.jpg)

## 13. GitHub test job

**GitHub UI capture** — Source: `Actions run 34152044446`.

Captured the successful test job in the same GitHub Actions run.

![GitHub test job](13-github-test-job.jpg)

## 14. GitHub pytest log

**GitHub UI capture** — Source: `Job 101836165394 in Actions run 34152044446`.

Captured the pytest output from the completed GitHub test job.

![GitHub pytest log](14-github-pytest-output.jpg)

## 15. Local regression and SMTP delivery

**Recorded test output** — Source: `tests/test_smtp_delivery.py + portfolio/pytest.txt`.

The integration test opened a real loopback SMTP connection, sent one DATA message after two callbacks, and confirmed two persisted events with sent/suppressed alert states. SMTP identities and callback tokens are redacted from the public record.

![Local regression and SMTP delivery](15-evidence.jpg)

## 16. Secret scanning

**Gitleaks output** — Source: `portfolio/gitleaks.txt`.

Scanned the tracked history with Gitleaks; the recorded scan found no secrets.

![Secret scanning](16-evidence.jpg)

## 17. Limitations and teardown status

**Operational notes** — Source: `LIMITATIONS.md + COST_AND_TEARDOWN.md`.

Recorded the resource state at the end of the run. The cleanup command and operational constraints are documented separately.

![Limitations and teardown status](17-evidence.jpg)
