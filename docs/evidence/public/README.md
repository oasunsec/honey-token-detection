# Honey Token — screenshot walkthrough

Recorded evidence from the 7 September 2026 run: baseline, deployment, document retrieval, event triage, Sentinel ingestion, and tests. Word and GitHub images are application captures. Azure images show saved API and query records rather than Azure portal screenshots. Teardown was not run.

Account details, email addresses, source IPs, tenant and subscription identifiers, callback tokens, and resource endpoints are redacted or omitted. Raw records remain outside this package.

[Open the offline gallery](index.html). Image hashes are recorded in [captions.json](captions.json).

## Browse the evidence

[Deployment](#03-infrastructure-deployment) · [Word callback](#07-word-callback-and-triage) · [Sentinel incident](#11-sentinel-incident) · [Tests](#15-local-regression-and-smtp-delivery)

## 01. Purpose and architecture

**Design summary** — Source: `ARCHITECTURE.md`.

The diagram separates the local Word callback from the controlled Azure-to-Sentinel path.

![Purpose and architecture](01-evidence.jpg)

## 02. Starting state and baseline

**Archived record, captured 2026-09-07** — Source: `00-azure-start-state.json + docs/BASELINE.md`.

The local SQLite service started with nine passing tests before the Azure adapters were added.

![Starting state and baseline](02-evidence.jpg)

## 03. Infrastructure deployment

**Archived Azure deployment response** — Source: `03-bicep-final-deployment.json`.

Bicep deployed the receiver infrastructure. Resource identifiers and endpoint values are omitted.

![Infrastructure deployment](03-evidence.jpg)

## 04. Receiver security configuration

**Source configuration evidence** — Source: `infra/main.bicep`.

The deployment disabled registry admin access and storage shared keys, required HTTPS, and disabled public management routes.

![Receiver security configuration](04-evidence.jpg)

## 05. Deployed receiver health

**Archived HTTP result** — Source: `09-container-app-health.json`.

The deployed health endpoint returned HTTP 200 with receiver-only mode and Azure Table Storage.

![Deployed receiver health](05-evidence.jpg)

## 06. Word renders the synthetic decoy

**Microsoft Word UI capture** — Source: `Word 16.0.20326.20132`.

Word opened the generated synthetic document. Its local callback appears in image 07.

![Word renders the synthetic decoy](06-word-decoy.png)

## 07. Word callback and triage

**Archived event from observed Word open** — Source: `word-viewer-result.json`.

The event recorded the Office User-Agent, source metadata, high severity, and a sent console alert when Word requested the loopback pixel.

![Word callback and triage](07-evidence.jpg)

## 08. Persisted events and delivery outcomes

**Archived Azure Table query** — Source: `table-events-sanitized.json`.

The query retained successful delivery outcomes and the first failed ingestion attempt.

![Persisted events and delivery outcomes](08-evidence.jpg)

## 09. Log Analytics ingestion

**Archived `CanaryHit_CL` query** — Source: `log-analytics-latest.json`.

Four records reached Log Analytics, including a scanner classification and a suppressed repeat notification.

![Log Analytics ingestion](09-evidence.jpg)

## 10. Sentinel analytic rule

**Archived rule configuration** — Source: `sentinel-rule.json`.

The rule ran every five minutes with a ten-minute lookback and incident creation enabled. It selected callback rows, including scanner and repeat rows.

![Sentinel analytic rule](10-evidence.jpg)

## 11. Sentinel incident

**Archived Sentinel incident response** — Source: `sentinel-incidents.json`.

The rule created a high-severity incident. Account and resource identifiers are omitted.

![Sentinel incident](11-evidence.jpg)

## 12. GitHub main CI status

**GitHub UI capture** — Source: `Actions run 34152044446, commit 2858824`.

The main-branch CI run completed after the application fixes.

![GitHub main CI status](12-github-ci-status.jpg)

## 13. GitHub test job

**GitHub UI capture** — Source: `Actions run 34152044446`.

The test job completed successfully in the same run.

![GitHub test job](13-github-test-job.jpg)

## 14. GitHub pytest log

**GitHub UI capture** — Source: `Job 101836165394 in Actions run 34152044446`.

The job log recorded the pytest run from the completed Actions job.

![GitHub pytest log](14-github-pytest-output.jpg)

## 15. Local regression and SMTP delivery

**Recorded test output** — Source: `portfolio/pytest.txt + tests/test_smtp_delivery.py`.

Sixteen tests passed, including local SMTP delivery and the SMTP-failure regression.

![Local regression and SMTP delivery](15-evidence.jpg)

## 16. Secret scanning

**Gitleaks output** — Source: `portfolio/gitleaks.txt`.

The tracked history scan found no secrets.

![Secret scanning](16-evidence.jpg)

## 17. Limits and teardown status

**Operational notes** — Source: `LIMITATIONS.md + COST_AND_TEARDOWN.md`.

The package records the remaining operational limits and the fact that resource cleanup was not run.

![Limitations and teardown status](17-evidence.jpg)
