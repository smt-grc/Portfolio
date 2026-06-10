"""`grctool evidence` - a compact version of Lesson 5's evidence tracker."""

import csv
from datetime import datetime, timedelta, date


def parse_date(value):
    value = (value or "").strip()
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def add_parser(subparsers):
    parser = subparsers.add_parser("evidence", help="Report overdue / due-soon evidence.")
    parser.add_argument("--file", required=True, help="Evidence register CSV.")
    parser.add_argument("--warn-days", type=int, default=14)
    parser.add_argument("--today", default=None, help="Override today (YYYY-MM-DD).")
    parser.set_defaults(func=run)


def run(args):
    today = parse_date(args.today) or date.today()
    with open(args.file, "r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assessed = []
    for row in rows:
        due = parse_date(row["last_collected"]) + timedelta(days=int(row["frequency_days"]))
        days_left = (due - today).days
        status = "OVERDUE" if days_left < 0 else ("DUE SOON" if days_left <= args.warn_days else "OK")
        assessed.append((days_left, status, row["evidence_id"], due))

    overdue = 0
    for days_left, status, ev_id, due in sorted(assessed):
        if status == "OK":
            continue
        if status == "OVERDUE":
            overdue += 1
        print(f"[{status:<8}] {ev_id:<8} due {due} ({days_left:+d}d)")
    print(f"\n{overdue} overdue evidence item(s) as of {today}.")
    return 1 if overdue else 0
