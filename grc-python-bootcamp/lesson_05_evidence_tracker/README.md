# Lesson 5 — Compliance Evidence Freshness Tracker

**GRC problem:** Continuous-monitoring frameworks expect evidence to be
collected on a cadence (monthly scans, quarterly access reviews, annual pen
tests). Evidence silently goes stale, and you only find out during audit week.
This tool computes each item's due date from its frequency and flags what's
**overdue** or **due soon**.

**Python you'll learn:** `datetime`/`timedelta` arithmetic, deriving new fields
(`due = last + frequency`), bucketing records by status, sorting by urgency, and
`sys.exit(1)` so the tool can **gate a CI pipeline**.

---

## Run it

```bash
cd lesson_05_evidence_tracker
python evidence_tracker.py --today 2026-06-10
python evidence_tracker.py --today 2026-06-10 --warn-days 21
python evidence_tracker.py --today 2026-06-10 --fail-on-overdue; echo "exit code: $?"
```

Output (abridged):

```
STATUS   ID      CONTROL DUE         DAYS  OWNER / DESCRIPTION
OVERDUE  EV-005  IR-01   2026-06-01  -9    Security - Incident response tabletop minutes
DUE SOON EV-002  VM-01   2026-06-19  +9    Security - Monthly vulnerability scan report
OK       EV-006  AC-02   2026-07-05  +25   IT - MFA enrollment report
...
Summary: 1 overdue, 2 due soon, 5 ok.
```

## How it works

- `timedelta(days=frequency)` added to `last_collected` gives the **due date** —
  this is the core date math you'll use everywhere in GRC.
- `days_left` drives a simple 3-bucket classification (`OVERDUE`/`DUE SOON`/`OK`).
- Sorting by `days_left` puts the fires at the top of the list.
- `--fail-on-overdue` makes the script exit non-zero. Combined with a scheduler
  (Lesson 10) this becomes an automated control that *fails loudly*.

## Try these exercises

1. Add a `--owner Security` filter to produce a per-owner to-do list.
2. Add a `--csv out.csv` export of only the OVERDUE + DUE SOON rows to email.
3. Group the summary by owner so each team sees its own overdue count.

## What "good" looks like

You always pass `--today` in evidence runs so results are reproducible, and you
understand why `sys.exit(1)` turns a report into an enforceable gate.
