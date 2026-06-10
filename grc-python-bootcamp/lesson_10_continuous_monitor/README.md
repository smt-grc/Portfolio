# Lesson 10 — Continuous Compliance Monitor (capstone)

**GRC problem:** Point-in-time checks drift. Frameworks increasingly expect
*continuous* control monitoring (SOC 2 CC4.1, ISO 27001 Clause 9.1). This
capstone runs all your earlier tools on a schedule, collects pass/fail by exit
code, and produces a dashboard you can publish and a non-zero exit a scheduler
can alert on.

**Python you'll learn:** reading **YAML** config, running **subprocesses** and
capturing exit codes/output, orchestrating multiple tools, timestamping a run,
emitting both human (Markdown) and machine (JSON) artifacts, and a final exit
code for automation.

> New dependency: `pyyaml`. Install with `pip install -r ../requirements.txt`.

---

## Run it

```bash
cd lesson_10_continuous_monitor
python monitor.py
python monitor.py --md dashboard.md --json results.json
echo "overall exit code: $?"
```

Output (abridged):

```
Running 4 compliance check(s) at 2026-06-10 18:30 UTC

[PASS] CC6.1   Password policy enforcement
        -> Result: 4/10 passed (40% compliant).
[FAIL] CC1.4   Evidence freshness (no overdue)
        -> FAIL: overdue evidence present.
[FAIL] CC6.6   Cloud config baseline (no CRITICAL)
        -> FAIL: findings at/above CRITICAL present.
[FAIL] CC6.2   User access review (no flagged accounts)
        -> 6/10 accounts need attention (as of 2026-06-10).

Dashboard: 1/4 checks passing.
```

(Most checks "fail" on purpose — the sample data is intentionally messy so you
can see the monitor catching real problems.)

## How it works

- `checks.yaml` defines *what* to run (name, control, working dir, command).
  Data-driven: add a check by editing YAML, not code.
- `subprocess.run(cmd, shell=True, cwd=..., capture_output=True, timeout=...)`
  runs each tool and gives you `.returncode` and `.stdout`.
- A check **passes if it exits 0**. That's why Lessons 5/8 and the access-review
  subcommand expose `--fail-on*` flags — they make a tool's *findings* drive its
  *exit code*, which the monitor turns into a control status.
- The monitor writes a Markdown dashboard and a JSON file, then exits non-zero
  if anything failed.

## Schedule it (make it truly continuous)

```bash
# Run every weekday at 8am and append output to a log (Linux/macOS cron):
0 8 * * 1-5 cd /path/to/lesson_10_continuous_monitor && python monitor.py --md dashboard.md >> monitor.log 2>&1
```

In CI (GitHub Actions), run `python monitor.py` as a scheduled workflow; the
non-zero exit fails the job and notifies you.

## Try these exercises

1. Add a Slack/webhook notification when any check fails (`requests.post`).
2. Feed `results.json` into the Lesson 7 report generator for a styled report.
3. Add a `severity` field per check and only fail the run on `high` severity.

## What "good" looks like

Adding a new monitored control is a YAML edit, every tool exposes a meaningful
exit code, and the monitor produces both a dashboard and an alert-able exit
status. **You've now built an end-to-end continuous compliance pipeline.**
