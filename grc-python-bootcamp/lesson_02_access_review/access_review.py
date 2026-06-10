"""Lesson 2 - User Access Review (UAR) Helper.

A GRC tool that reads an export of user accounts (CSV) and flags the accounts
an access review should question: terminated employees who still have access,
stale accounts that haven't logged in for a long time, privileged accounts
without MFA, and so on.

Concepts taught: the `csv` module, dictionaries per row, `datetime` math,
list filtering, and writing results back out to a CSV.

Run it:
    python access_review.py                       # reads sample_users.csv
    python access_review.py --file my_export.csv
    python access_review.py --stale-days 60       # tighten the stale threshold
    python access_review.py --out findings.csv    # also write findings to CSV
"""

import argparse
import csv
from datetime import datetime, date


def parse_date(value):
    """Parse an ISO date (YYYY-MM-DD). Return None if blank/unparseable."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def review_account(row, today, stale_days):
    """Return a list of findings (strings) for a single account row."""
    findings = []

    status = row.get("status", "").strip().lower()
    is_privileged = row.get("privileged", "").strip().lower() in {"true", "yes", "1"}
    mfa_enabled = row.get("mfa_enabled", "").strip().lower() in {"true", "yes", "1"}
    last_login = parse_date(row.get("last_login", ""))

    # 1. Terminated/disabled users that still appear in the access export.
    if status in {"terminated", "disabled", "inactive"}:
        findings.append(f"account is '{status}' but still present in access export")

    # 2. Stale accounts: no login within the threshold.
    if last_login is None:
        findings.append("no recorded last-login date")
    else:
        idle_days = (today - last_login).days
        if idle_days > stale_days:
            findings.append(f"stale: last login {idle_days} days ago (> {stale_days})")

    # 3. Privileged accounts without MFA - a high-severity finding.
    if is_privileged and not mfa_enabled:
        findings.append("PRIVILEGED account without MFA")

    return findings


def load_accounts(path):
    """Read the CSV export into a list of dict rows."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_findings(path, findings_rows):
    """Write findings to a CSV so you can attach it to the review ticket."""
    fieldnames = ["username", "department", "severity", "finding"]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(findings_rows)


def main():
    parser = argparse.ArgumentParser(description="Flag risky accounts for a user access review.")
    parser.add_argument("--file", default="sample_users.csv", help="CSV export of user accounts.")
    parser.add_argument("--stale-days", type=int, default=90, help="Idle days before an account is 'stale'.")
    parser.add_argument("--out", default=None, help="Optional path to write findings as CSV.")
    parser.add_argument("--today", default=None, help="Override 'today' (YYYY-MM-DD) for reproducible runs.")
    args = parser.parse_args()

    today = parse_date(args.today) or date.today()
    accounts = load_accounts(args.file)

    print(f"Reviewing {len(accounts)} account(s) as of {today} "
          f"(stale threshold: {args.stale_days} days)\n")

    findings_rows = []
    flagged = 0
    for row in accounts:
        findings = review_account(row, today, args.stale_days)
        if not findings:
            continue
        flagged += 1
        username = row.get("username", "<unknown>")
        department = row.get("department", "")
        for finding in findings:
            severity = "HIGH" if "PRIVILEGED" in finding else "MEDIUM"
            print(f"[{severity}] {username} ({department}): {finding}")
            findings_rows.append({
                "username": username,
                "department": department,
                "severity": severity,
                "finding": finding,
            })

    print(f"\n{flagged}/{len(accounts)} account(s) need attention "
          f"({len(findings_rows)} total finding(s)).")

    if args.out:
        write_findings(args.out, findings_rows)
        print(f"Findings written to {args.out}")


if __name__ == "__main__":
    main()
