"""Lesson 11 - AWS Security Hub Compliance Summary (applied lesson).

Extract compliance findings from AWS Security Hub and turn them into an
executive-friendly summary report. Security Hub aggregates checks from the AWS
Foundational Security Best Practices, CIS, and PCI standards into a common
schema (ASFF). This tool pulls those findings, scores your posture, highlights
the worst controls, and writes a Markdown report - exactly what you'd attach to
a monthly compliance update (SOC 2 CC7.1, ISO 27001 A.8.8 / Clause 9.1).

It runs two ways:
  * --offline : reads a bundled ASFF sample (no AWS account needed)
  * (default) : live, using boto3's securityhub get_findings paginator

Concepts taught: reading a real cloud API's nested schema (ASFF), lazy imports
(so offline mode needs no boto3), aggregation with collections.Counter, building
a Markdown report, and exit codes for gating.

Run it:
    python security_hub_report.py --offline
    python security_hub_report.py --offline --md report.md --json summary.json
    python security_hub_report.py --region us-east-1            # live
    python security_hub_report.py --region us-east-1 --status FAILED --fail-on CRITICAL
"""

import argparse
import json
import sys
from collections import Counter

SEVERITY_ORDER = {"INFORMATIONAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def normalize(finding):
    """Flatten one ASFF finding into the handful of fields we report on.

    ASFF is deeply nested and fields are optional, so we use .get() with
    sensible defaults everywhere - defensive parsing is the whole game when
    consuming a real cloud API.
    """
    compliance = finding.get("Compliance", {})
    resources = finding.get("Resources", [{}])
    return {
        "account": finding.get("AwsAccountId", "unknown"),
        "control": compliance.get("SecurityControlId")
        or finding.get("ProductFields", {}).get("ControlId", "unknown"),
        "title": finding.get("Title", ""),
        "severity": finding.get("Severity", {}).get("Label", "INFORMATIONAL").upper(),
        "status": compliance.get("Status", "UNKNOWN"),
        "workflow": finding.get("Workflow", {}).get("Status", "NEW"),
        "resource": resources[0].get("Id", "") if resources else "",
    }


def fetch_findings_offline(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle).get("Findings", [])


def fetch_findings_live(region, only_status):
    """Pull active findings from Security Hub using a paginator.

    boto3 is imported here (lazily) so that --offline mode works on a machine
    with no AWS SDK installed and no credentials configured.
    """
    import boto3  # noqa: PLC0415 - intentional lazy import

    client = boto3.client("securityhub", region_name=region)
    filters = {"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
    if only_status:
        filters["ComplianceStatus"] = [{"Value": only_status, "Comparison": "EQUALS"}]

    findings = []
    paginator = client.get_paginator("get_findings")
    for page in paginator.paginate(Filters=filters):
        findings.extend(page.get("Findings", []))
    return findings


def summarize(findings, include_suppressed):
    """Aggregate normalized findings into the numbers a report needs.

    The compliance score always compares PASSED vs FAILED, so it stays
    meaningful regardless of any server-side --status filter.
    """
    rows = [normalize(f) for f in findings]
    if not include_suppressed:
        rows = [r for r in rows if r["workflow"] != "SUPPRESSED"]

    failed = [r for r in rows if r["status"] == "FAILED"]
    passed = [r for r in rows if r["status"] == "PASSED"]
    scored = len(failed) + len(passed)
    score = round(len(passed) / scored * 100, 1) if scored else 0.0

    # Counter is the fast way to tally - {key: count} without manual loops.
    by_severity = Counter(r["severity"] for r in failed)
    by_account = Counter(r["account"] for r in failed)
    top_controls = Counter(r["control"] for r in failed)

    return {
        "total": len(rows),
        "failed": len(failed),
        "passed": len(passed),
        "compliance_score": score,
        "by_severity": dict(by_severity),
        "by_account": dict(by_account),
        "top_controls": top_controls.most_common(5),
        "critical_high": [r for r in failed if SEVERITY_ORDER.get(r["severity"], 0) >= 3],
        "failed_rows": sorted(failed, key=lambda r: SEVERITY_ORDER.get(r["severity"], 0), reverse=True),
    }


def render_markdown(s):
    lines = [
        "# AWS Security Hub Compliance Summary",
        "",
        f"**Compliance score:** {s['compliance_score']}%  "
        f"({s['passed']} passed / {s['failed']} failed)",
        "",
        "## Failed findings by severity",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if s["by_severity"].get(sev):
            lines.append(f"| {sev} | {s['by_severity'][sev]} |")

    lines += ["", "## Top failing controls", ""]
    for control, count in s["top_controls"]:
        lines.append(f"- **{control}** — {count} failing finding(s)")

    lines += ["", "## Failed findings by account", ""]
    for account, count in sorted(s["by_account"].items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- `{account}` — {count}")

    if s["critical_high"]:
        lines += ["", "## Critical / High items needing action", ""]
        for r in s["critical_high"]:
            lines.append(f"- **[{r['severity']}] {r['control']}** — {r['title']}  "
                         f"(`{r['account']}`, {r['resource']})")
    return "\n".join(lines) + "\n"


def print_summary(s):
    print(f"Compliance score: {s['compliance_score']}%  "
          f"({s['passed']} passed / {s['failed']} failed, {s['total']} findings considered)\n")
    print("Failed by severity:")
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if s["by_severity"].get(sev):
            print(f"  {sev:<9} {s['by_severity'][sev]}")
    print("\nTop failing controls:")
    for control, count in s["top_controls"]:
        print(f"  {control:<16} {count}")
    if s["critical_high"]:
        print(f"\nCritical/High needing action ({len(s['critical_high'])}):")
        for r in s["critical_high"]:
            print(f"  [{r['severity']:<8}] {r['control']:<16} {r['title']}")


def main():
    parser = argparse.ArgumentParser(description="Summarize AWS Security Hub compliance findings.")
    parser.add_argument("--offline", action="store_true", help="Use bundled ASFF sample (no AWS needed).")
    parser.add_argument("--file", default="sample_findings.json", help="ASFF JSON file for offline mode.")
    parser.add_argument("--region", default="us-east-1", help="AWS region for live mode.")
    parser.add_argument("--status", default=None, choices=["FAILED", "PASSED", "WARNING"],
                        help="Live mode only: server-side filter to reduce data pulled (e.g. FAILED).")
    parser.add_argument("--include-suppressed", action="store_true",
                        help="Include findings whose workflow status is SUPPRESSED.")
    parser.add_argument("--md", default=None, help="Write a Markdown report to this path.")
    parser.add_argument("--json", default=None, help="Write the summary as JSON to this path.")
    parser.add_argument("--fail-on", default=None, choices=list(SEVERITY_ORDER),
                        help="Exit 1 if any FAILED finding is at/above this severity.")
    args = parser.parse_args()

    if args.offline:
        findings = fetch_findings_offline(args.file)
        source = f"offline sample ({args.file})"
    else:
        try:
            findings = fetch_findings_live(args.region, args.status)
        except Exception as exc:  # boto3/credential/region errors
            print(f"Live Security Hub query failed: {exc}\n"
                  f"Tip: run with --offline to use the bundled sample.", file=sys.stderr)
            sys.exit(2)
        source = f"live Security Hub ({args.region})"

    print(f"Source: {source}\n")
    summary = summarize(findings, args.include_suppressed)
    print_summary(summary)

    if args.md:
        with open(args.md, "w", encoding="utf-8") as handle:
            handle.write(render_markdown(summary))
        print(f"\nMarkdown report written to {args.md}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        print(f"JSON summary written to {args.json}")

    if args.fail_on:
        gate = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER.get(r["severity"], 0) >= gate for r in summary["failed_rows"]):
            print(f"\nFAIL: FAILED findings at/above {args.fail_on} present.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
