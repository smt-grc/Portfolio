"""Lesson 10 - Continuous Compliance Monitor.

The capstone. This tool reads a list of checks from a YAML config, runs each one
as a subprocess, records pass/fail by exit code, and produces a compliance
dashboard (terminal table + Markdown + JSON). Point a scheduler at it and you
have continuous control monitoring (SOC 2 CC4.1, ISO 27001 Clause 9.1).

Concepts taught: reading YAML config, running subprocesses and capturing their
exit code/output, orchestrating many tools, timestamping a run, writing both
human (Markdown) and machine (JSON) artifacts, and a final non-zero exit so a
scheduler/CI marks the run failed.

Run it:
    python monitor.py
    python monitor.py --md dashboard.md --json results.json
    python monitor.py --base-dir ..        # default; bootcamp root
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import yaml


def load_checks(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)["checks"]


def run_check(check, base_dir, timeout):
    """Run a single check's command and return a result dict."""
    workdir = os.path.join(base_dir, check.get("cwd", "."))
    try:
        completed = subprocess.run(
            check["cmd"],
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        passed = completed.returncode == 0
        detail = (completed.stdout.strip().splitlines() or [""])[-1]
    except subprocess.TimeoutExpired:
        passed, detail = False, f"timed out after {timeout}s"
    except OSError as exc:
        passed, detail = False, f"failed to launch: {exc}"

    return {
        "name": check["name"],
        "control": check.get("control", "-"),
        "status": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def write_markdown(path, results, ran_at):
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines = [
        "# Continuous Compliance Dashboard",
        "",
        f"**Run at:** {ran_at}",
        f"**Result:** {passed}/{len(results)} checks passing",
        "",
        "| Status | Control | Check | Detail |",
        "|--------|---------|-------|--------|",
    ]
    for r in results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        detail = r["detail"].replace("|", "\\|")[:80]
        lines.append(f"| {icon} | {r['control']} | {r['name']} | {detail} |")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run a suite of GRC checks and build a dashboard.")
    parser.add_argument("--config", default="checks.yaml", help="YAML file defining the checks.")
    parser.add_argument("--base-dir", default="..", help="Base dir checks' cwd is relative to.")
    parser.add_argument("--timeout", type=int, default=60, help="Per-check timeout (seconds).")
    parser.add_argument("--md", default=None, help="Write a Markdown dashboard here.")
    parser.add_argument("--json", default=None, help="Write machine-readable results here.")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    checks = load_checks(args.config)
    ran_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print(f"Running {len(checks)} compliance check(s) at {ran_at}\n")
    results = []
    for check in checks:
        result = run_check(check, base_dir, args.timeout)
        results.append(result)
        print(f"[{result['status']}] {result['control']:<7} {result['name']}")
        print(f"        -> {result['detail']}")

    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\nDashboard: {passed}/{len(results)} checks passing.")

    if args.md:
        write_markdown(args.md, results, ran_at)
        print(f"Markdown dashboard written to {args.md}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"ran_at": ran_at, "results": results}, handle, indent=2)
        print(f"JSON results written to {args.json}")

    # Non-zero exit if anything failed, so a scheduler/CI flags the run.
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
