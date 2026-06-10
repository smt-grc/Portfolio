# Lesson 11 — AWS Security Hub Compliance Summary (applied lesson)

**GRC problem:** AWS Security Hub continuously evaluates your accounts against
standards (AWS Foundational Security Best Practices, CIS, PCI) and produces
hundreds of findings. Nobody reads raw findings. Leadership and auditors want a
**summary**: what's our score, what's failing, what's critical. This tool
extracts the findings and produces that report (supports SOC 2 CC7.1, ISO 27001
A.8.8 and Clause 9.1 monitoring).

**Builds on:** Lesson 4 (calling an API + offline mode) and Lesson 7 (reporting).
**New ideas:** consuming a real cloud schema (ASFF), lazy imports, and
`collections.Counter` for aggregation.

---

## Run it now (no AWS needed)

```bash
cd lesson_11_security_hub_report
python security_hub_report.py --offline
python security_hub_report.py --offline --md report.md --json summary.json
python security_hub_report.py --offline --fail-on CRITICAL; echo "exit: $?"
```

Output (abridged):

```
Compliance score: 22.2%  (2 passed / 7 failed, 9 findings considered)

Failed by severity:
  CRITICAL  1
  HIGH      3
  MEDIUM    3

Top failing controls:
  S3.5             2
  ...
Critical/High needing action (4):
  [CRITICAL] IAM.4   IAM root user access key should not exist
```

---

## The build, step by step

**Step 1 — Understand the data source.** Security Hub returns findings in the
*AWS Security Finding Format* (ASFF) — a big nested JSON document. The fields we
care about for a compliance summary are a tiny subset:
`AwsAccountId`, `Severity.Label`, `Compliance.Status` (PASSED/FAILED),
`Compliance.SecurityControlId`, `Workflow.Status`, `Title`, `Resources[].Id`.

**Step 2 — Get sample data first.** `sample_findings.json` is a realistic ASFF
file. Developing against a saved sample (offline mode) means you write and debug
the whole tool *before* touching AWS — faster and reproducible.

**Step 3 — Flatten each finding (`normalize`).** ASFF is deeply nested and many
fields are optional, so we read everything with `.get(...)` and defaults.
Defensive parsing is the entire game when consuming a real cloud API:

```python
"control": compliance.get("SecurityControlId")
           or finding.get("ProductFields", {}).get("ControlId", "unknown"),
"status":  compliance.get("Status", "UNKNOWN"),
```

**Step 4 — Aggregate (`summarize`).** `collections.Counter` tallies counts in one
line each — by severity, by account, and the top failing controls:

```python
by_severity = Counter(r["severity"] for r in failed)
top_controls = Counter(r["control"] for r in failed).most_common(5)
```

The compliance score is `passed / (passed + failed)` and always compares both,
so it stays meaningful. Suppressed findings are excluded by default (use
`--include-suppressed` to keep them).

**Step 5 — Render the report (`render_markdown`).** We build a Markdown string
with a score line, a severity table, top controls, a per-account breakdown, and
a Critical/High action list. Save with `--md report.md`, or `--json` for a
machine-readable feed into the Lesson 10 monitor.

**Step 6 — Go live with `boto3`.** Remove `--offline` and pass `--region`. The
tool uses a paginator so it pulls *all* findings, not just the first page:

```python
paginator = client.get_paginator("get_findings")
for page in paginator.paginate(Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}):
    findings.extend(page["Findings"])
```

`import boto3` is done **inside** that function (a lazy import) so offline mode
runs on a machine with no AWS SDK and no credentials.

**Step 7 — Schedule / gate it.** `--fail-on CRITICAL` exits non-zero when any
critical finding is failing, so cron or CI can alert. This is the same gate
pattern as Lessons 5, 8, and 10.

---

## Using it live (AWS setup)

1. Enable AWS Security Hub in your account/region.
2. Provide read-only credentials (env vars or a profile). Minimum permission:
   `securityhub:GetFindings` (the AWS managed `AWSSecurityHubReadOnlyAccess`
   policy is a safe superset).
   ```bash
   export AWS_ACCESS_KEY_ID=...
   export AWS_SECRET_ACCESS_KEY=...
   python security_hub_report.py --region us-east-1 --status FAILED --md report.md
   ```
   `--status FAILED` filters server-side to reduce data pulled.

> Tip: start read-only and least-privilege. You never need write access to
> *report* on compliance.

## Try these exercises

1. Add a `--min-severity HIGH` flag to drop low-noise findings.
2. Group the report by `Resources[0].Type` to see which service is worst.
3. Pipe `summary.json` into Lesson 10's monitor as another check.
4. Feed the numbers into Lesson 7's Jinja2 template for a branded report.

## What "good" looks like

You developed the entire tool offline against a saved sample, parsed a real
nested cloud schema defensively, and produced both a human report and a
machine-readable summary — then flipped one flag to run it live.
