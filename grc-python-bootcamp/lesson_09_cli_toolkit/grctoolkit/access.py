"""`grctool access-review` - a compact version of Lesson 2's access review."""

import csv
from datetime import datetime, date


def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def review_row(row, today, stale_days):
    findings = []
    status = row.get("status", "").lower()
    if status in {"terminated", "disabled", "inactive"}:
        findings.append(f"status '{status}' still in export")
    last = parse_date(row.get("last_login"))
    if last is None:
        findings.append("no last-login date")
    elif (today - last).days > stale_days:
        findings.append(f"stale ({(today - last).days}d)")
    if row.get("privileged", "").lower() in {"true", "yes", "1"} and \
       row.get("mfa_enabled", "").lower() not in {"true", "yes", "1"}:
        findings.append("privileged without MFA")
    return findings


def add_parser(subparsers):
    parser = subparsers.add_parser("access-review", help="Flag risky accounts in a user export.")
    parser.add_argument("--file", required=True, help="CSV export of accounts.")
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--today", default=None, help="Override today (YYYY-MM-DD).")
    parser.set_defaults(func=run)


def run(args):
    today = parse_date(args.today) or date.today()
    with open(args.file, "r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    flagged = 0
    for row in rows:
        findings = review_row(row, today, args.stale_days)
        if findings:
            flagged += 1
            print(f"[FLAG] {row.get('username', '?'):<10} {'; '.join(findings)}")
    print(f"\n{flagged}/{len(rows)} accounts need attention (as of {today}).")
    return 1 if flagged else 0
