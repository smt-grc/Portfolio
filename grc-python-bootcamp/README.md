# GRC Python Bootcamp — Learn Python by Building Compliance Tools

A hands-on study plan that teaches you Python by building **real GRC automation
tools**. There is no "hello world" busywork here — every lesson ends with a
working script you can point at your own data and use in your compliance program
today. You learn a new Python concept *because a real GRC problem needs it*.

> **Who this is for:** GRC analysts, auditors, and security folks who want to
> stop doing repetitive spreadsheet work and start automating. No prior
> programming experience required.

---

## How this course works

- **Learn by doing.** Each lesson is a self-contained folder with: a working
  tool, realistic sample data, and a `README.md` that explains the GRC problem,
  the Python concepts, how to run it, and exercises to extend it.
- **Difficulty ramps up gradually.** Lessons 1–3 use only Python's standard
  library. Lessons 4, 6, 7, and 10 each introduce exactly one popular library.
- **Everything is runnable now.** Run the bundled sample data first, then swap
  in your own exports (CSV/JSON) — the tools are built to take real inputs.
- **The tools compose.** By Lesson 10 you orchestrate the earlier tools into a
  single continuous-compliance pipeline.

## Setup (one time, ~5 minutes)

```bash
# 1. Install Python 3.10+  (check with: python --version)
# 2. From this folder, install the few libraries the later lessons use:
pip install -r requirements.txt
# 3. Start with Lesson 1:
cd lesson_01_password_policy
python password_policy_checker.py
```

That's it. Each lesson tells you exactly what to run.

---

## The curriculum at a glance

| # | Tool you build | GRC problem it solves | New Python you learn |
|---|----------------|-----------------------|----------------------|
| 1 | **Password Policy Checker** | Enforce & evidence a password policy | variables, strings, functions, `if`, loops, file read, `argparse` |
| 2 | **User Access Review Helper** | Flag stale / terminated / no-MFA accounts | `csv` module, dict-per-row, `datetime` math, CSV output |
| 3 | **Control Mapping & Crosswalk** | Map controls across SOC 2 / ISO / NIST; gap analysis | `json`, nested data, `set` operations, subcommands |
| 4 | **CVE / Vulnerability Checker** | Find known CVEs for your software stack (NVD API) | `requests`, REST APIs, error handling, offline mode |
| 5 | **Evidence Freshness Tracker** | Catch overdue audit evidence before audit week | `timedelta` math, bucketing, exit codes as gates |
| 6 | **Risk Register Analyzer** | Score & prioritize risks; report by category | **pandas**: DataFrames, vectorized math, `groupby` |
| 7 | **Compliance Report Generator** | Auto-generate a status report from data | **Jinja2** templating: loops, conditionals, filters |
| 8 | **Cloud Config Scanner** | Detect public buckets, no-MFA admins, open ports | check-function registry, nested JSON, severity, CI gate |
| 9 | **`grctool` CLI Toolkit** | Bundle your tools into one real command | `argparse` subparsers, **packages**, exit codes |
| 10 | **Continuous Compliance Monitor** | Run all checks on a schedule → dashboard | **PyYAML**, `subprocess`, orchestration, scheduling |

**Suggested pace:** one lesson per sitting (45–90 min each). Do the exercises at
the end of each lesson README before moving on — that's where the learning
sticks.

---

## The skills ladder (what you'll be able to do after each stage)

- **After Lessons 1–3 (Python foundations):** read/write files, work with CSV
  and JSON, write functions that return structured results, and build small
  command-line tools. You can already automate a lot of spreadsheet drudgery.
- **After Lessons 4–7 (working with real data & services):** call external APIs,
  analyze data with pandas, and generate polished reports. This is the bread and
  butter of a "GRC engineer."
- **After Lessons 8–10 (engineering & automation):** structure code into
  packages, build multi-command CLIs, and orchestrate everything into a
  scheduled, alert-able pipeline.

## How the tools connect

By the end, the pieces form a pipeline:

```
   inventory.csv ─► (4) CVE checker ─┐
 accounts.csv ───► (2/9) access review ┤
 evidence.csv ───► (5) freshness ──────┤──► (10) monitor ──► dashboard.md
 cloud.json ─────► (8) config scan ────┤        │             results.json
 risks.csv ──────► (6) risk analyzer ──┘        └─► (7) report generator ─► report.md
```

The **Lesson 10 monitor** runs the checks and produces a dashboard; the
**Lesson 7 generator** turns collected data into a readable report. Together
they're a miniature continuous-compliance program.

---

## Conventions used throughout

- **Data lives in files, logic lives in code.** You tune controls by editing
  CSV/JSON, not by editing Python.
- **Tools return structured results** (lists of findings), not just `True/False`
  — auditors want to know *why*.
- **Reproducible evidence.** Tools that depend on "today" accept a `--today`
  flag so a run can be re-created exactly later.
- **Exit codes matter.** Tools exit non-zero when they find problems, so they
  can gate pipelines and trigger alerts.

## Where to go next

- Replace sample data with your real exports (Okta/AD, AWS IAM, your risk
  register).
- Swap Lesson 8's file load for live `boto3` calls (read-only, least-privilege).
- Schedule Lesson 10 with cron or a GitHub Actions scheduled workflow.

Happy automating — and welcome to GRC engineering.
