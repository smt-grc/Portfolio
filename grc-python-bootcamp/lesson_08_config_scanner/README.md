# Lesson 8 — Cloud Configuration Compliance Scanner

**GRC problem:** Most breaches trace back to a misconfiguration: a public S3
bucket, an admin without MFA, SSH open to the world. This tool parses a cloud
account export and checks it against a security baseline (SOC 2 CC6/CC7, ISO
27001 A.8.9, CIS AWS Benchmark) — the same idea behind AWS Config, Prowler, and
Scout Suite, in ~120 readable lines.

**Python you'll learn:** organizing logic into many small **check functions**, a
registry pattern (`CHECKS = [...]`) so new checks are one line, walking nested
JSON, building a structured findings list, and a CI gate via `--fail-on`.

---

## Run it

```bash
cd lesson_08_config_scanner
python config_scanner.py
python config_scanner.py --min-severity HIGH
python config_scanner.py --json findings.json
python config_scanner.py --fail-on CRITICAL; echo "exit: $?"
```

Output (abridged):

```
Scanned account 123456789012: 11 finding(s) at/above LOW

[CRITICAL] s3:acme-customer-data    bucket is publicly accessible  (control CC6.1)
[CRITICAL] iam:root                 root account has active access keys  (control CC6.1)
[CRITICAL] sg:sg-ssh                SSH (port 22) open to the internet (0.0.0.0/0)  (control CC6.6)
...
By severity: CRITICAL=4, HIGH=3, MEDIUM=1, LOW=3
```

## How it works

- Each `check_*()` function focuses on one resource type and returns findings —
  small, independently testable, easy to read.
- The **registry** `CHECKS = [check_s3, check_iam, check_security_groups]` means
  `scan()` doesn't care how many checks exist. Adding a new control = write a
  function + add it to the list.
- `finding()` enforces a consistent finding **shape** (`severity`, `resource`,
  `message`, `control`) so downstream tools (Lesson 7 report, Lesson 10 monitor)
  can consume it.
- `--fail-on CRITICAL` turns the scanner into a deploy gate.

## From sample data to the real thing

The sample JSON mimics an AWS snapshot. To scan a **real** account, replace the
file load with `boto3` calls (e.g. `boto3.client("s3").list_buckets()`), keeping
the same finding shape. Start read-only with least-privilege credentials.

## Try these exercises

1. Add `check_rds()` for unencrypted or publicly-accessible databases.
2. Add a `--baseline baseline.json` so thresholds (e.g. allowed open ports) are
   configurable data, not code.
3. Feed `findings.json` into the Lesson 7 report generator.

## What "good" looks like

Adding a new compliance check is a tiny, isolated change, and every finding has
a consistent shape mapped to a named control.
