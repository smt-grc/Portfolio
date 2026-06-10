# Lesson 2 — User Access Review (UAR) Helper

**GRC problem:** Quarterly access reviews (SOC 2 CC6.2/CC6.3, ISO 27001 A.5.18,
NIST AC-2) are tedious and error-prone when done by eye in a spreadsheet. This
tool reads an account export and automatically flags the rows a reviewer
should challenge: terminated users with lingering access, stale accounts, and
privileged accounts without MFA.

**Python you'll learn:** the `csv` module (`DictReader`/`DictWriter`),
treating each row as a dictionary, `datetime` math to compute idle days, list
filtering, and writing results back to a CSV you can attach to a ticket.

---

## Run it

```bash
cd lesson_02_access_review
python access_review.py
python access_review.py --stale-days 60
python access_review.py --out findings.csv
# Reproducible run (pin "today" so the output never changes):
python access_review.py --today 2026-06-10 --out findings.csv
```

Expected output (abridged):

```
[MEDIUM] cjones (Sales): account is 'terminated' but still present in access export
[HIGH]   dlopez (IT): PRIVILEGED account without MFA
[MEDIUM] ekim (Marketing): stale: last login 220 days ago (> 90)
...
6/10 account(s) need attention (9 total finding(s)).
```

## How it works

- **`csv.DictReader`** turns each CSV row into a dictionary keyed by the header
  row, so `row["status"]` reads the `status` column. This is how you'll ingest
  almost every system export (Okta, AD, AWS IAM, Workday) in real GRC work.
- **`datetime` / `date`** lets you compute `(today - last_login).days`. Note the
  `--today` flag: pinning "today" makes the tool's output **deterministic**,
  which matters when an auditor re-runs your evidence months later.
- **`review_account()`** again returns a *list of findings* (same pattern as
  Lesson 1) so the logic is reusable and testable.

## Try these exercises

1. Add a `--department Finance` filter so you can scope the review to one team.
2. Add a severity for "privileged + stale" and make it CRITICAL.
3. Sort the printed findings by severity (HIGH first). Hint: a small priority
   dict `{"HIGH": 0, "MEDIUM": 1}` plus `sorted(..., key=...)`.

## What "good" looks like

You can ingest a brand-new CSV export with different columns and adapt the tool
in under five minutes — because you understand that `DictReader` keys come from
the header row.
