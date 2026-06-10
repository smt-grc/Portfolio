"""Lesson 5 - Compliance Evidence Freshness Tracker.

A GRC tool that reads your evidence register (CSV) and tells you which audit
evidence is fresh, expiring soon, or already overdue - based on each item's
collection frequency. This is how you avoid the audit-week scramble of
realizing half your evidence is stale.

Concepts taught: `datetime`/`timedelta` arithmetic, deriving new fields from
existing data, classifying records into buckets, sorting, and exiting with a
non-zero status code so the tool can gate an automated pipeline.

Run it:
    python evidence_tracker.py
    python evidence_tracker.py --today 2026-06-10        # reproducible run
    python evidence_tracker.py --warn-days 21            # warn earlier
    python evidence_tracker.py --fail-on-overdue         # exit 1 if anything overdue
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta, date


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def assess(row, today, warn_days):
    """Compute the due date and status bucket for one evidence item."""
    last = parse_date(row["last_collected"])
    frequency = int(row["frequency_days"])
    due = last + timedelta(days=frequency)
    days_left = (due - today).days

    if days_left < 0:
        status = "OVERDUE"
    elif days_left <= warn_days:
        status = "DUE SOON"
    else:
        status = "OK"

    return {
        "evidence_id": row["evidence_id"],
        "control": row["control"],
        "description": row["description"],
        "owner": row["owner"],
        "due": due,
        "days_left": days_left,
        "status": status,
    }


def load_register(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser(description="Track freshness of compliance evidence.")
    parser.add_argument("--file", default="evidence_register.csv", help="Evidence register CSV.")
    parser.add_argument("--warn-days", type=int, default=14, help="Days before due to start warning.")
    parser.add_argument("--today", default=None, help="Override 'today' (YYYY-MM-DD) for reproducible runs.")
    parser.add_argument("--fail-on-overdue", action="store_true",
                        help="Exit with status 1 if any evidence is overdue (useful in CI).")
    args = parser.parse_args()

    today = parse_date(args.today) or date.today()
    rows = [assess(r, today, args.warn_days) for r in load_register(args.file)]

    # Most urgent first: fewest days left at the top.
    rows.sort(key=lambda r: r["days_left"])

    print(f"Evidence freshness as of {today} (warn window: {args.warn_days} days)\n")
    print(f"{'STATUS':<9}{'ID':<8}{'CONTROL':<8}{'DUE':<12}{'DAYS':<6}OWNER / DESCRIPTION")
    counts = {"OVERDUE": 0, "DUE SOON": 0, "OK": 0}
    for r in rows:
        counts[r["status"]] += 1
        days = f"{r['days_left']:+d}"
        print(f"{r['status']:<9}{r['evidence_id']:<8}{r['control']:<8}{str(r['due']):<12}"
              f"{days:<6}{r['owner']} - {r['description']}")

    print(f"\nSummary: {counts['OVERDUE']} overdue, {counts['DUE SOON']} due soon, "
          f"{counts['OK']} ok.")

    if args.fail_on_overdue and counts["OVERDUE"] > 0:
        print("FAIL: overdue evidence present.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
