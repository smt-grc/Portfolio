"""Lesson 8 - Cloud Configuration Compliance Scanner.

A GRC tool that parses a cloud configuration export (JSON, in the shape of an
AWS account snapshot) and checks it against a set of security baseline rules:
public buckets, unencrypted storage, IAM users without MFA, root access keys,
and security groups open to the world. This is a miniature "config compliance"
control (SOC 2 CC6/CC7, ISO 27001 A.8.9 configuration management, CIS AWS
Benchmark).

Concepts taught: organizing many small check functions, walking nested JSON,
building a structured findings list (a list of dicts), severity levels, and
producing both a human summary and a machine-readable JSON export.

Run it:
    python config_scanner.py
    python config_scanner.py --file my_account.json
    python config_scanner.py --min-severity HIGH
    python config_scanner.py --json findings.json
"""

import argparse
import json
import sys

SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
RISKY_PORTS = {22: "SSH", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL"}


def finding(severity, resource, message, control):
    """Helper to build one finding dict in a consistent shape."""
    return {"severity": severity, "resource": resource, "message": message, "control": control}


def check_s3(config):
    findings = []
    for bucket in config.get("s3_buckets", []):
        name = bucket["name"]
        if bucket.get("public"):
            sev = "CRITICAL" if bucket.get("encryption", "none") == "none" else "HIGH"
            findings.append(finding(sev, f"s3:{name}", "bucket is publicly accessible", "CC6.1"))
        if bucket.get("encryption", "none") == "none":
            findings.append(finding("HIGH", f"s3:{name}", "bucket is not encrypted at rest", "CC6.7"))
        if not bucket.get("versioning"):
            findings.append(finding("LOW", f"s3:{name}", "versioning disabled (no tamper protection)", "A1.2"))
    return findings


def check_iam(config):
    findings = []
    for user in config.get("iam_users", []):
        name = user["username"]
        if name == "root" and user.get("access_keys", 0) > 0:
            findings.append(finding("CRITICAL", f"iam:{name}", "root account has active access keys", "CC6.1"))
        if user.get("admin") and not user.get("mfa_enabled"):
            findings.append(finding("HIGH", f"iam:{name}", "admin user without MFA", "CC6.1"))
        if user.get("access_keys", 0) > 1:
            findings.append(finding("MEDIUM", f"iam:{name}",
                                    f"{user['access_keys']} active access keys (rotate/remove extras)", "CC6.1"))
    return findings


def check_security_groups(config):
    findings = []
    for sg in config.get("security_groups", []):
        sg_id = sg["id"]
        if sg.get("source") == "0.0.0.0/0":
            for port in sg.get("open_ports", []):
                if port in RISKY_PORTS:
                    findings.append(finding("CRITICAL", f"sg:{sg_id}",
                                            f"{RISKY_PORTS[port]} (port {port}) open to the internet (0.0.0.0/0)",
                                            "CC6.6"))
    return findings


# Register every check function here - adding a new check is a one-line change.
CHECKS = [check_s3, check_iam, check_security_groups]


def scan(config):
    findings = []
    for check in CHECKS:
        findings.extend(check(config))
    findings.sort(key=lambda f: SEVERITY_ORDER[f["severity"]], reverse=True)
    return findings


def main():
    parser = argparse.ArgumentParser(description="Scan a cloud config export for misconfigurations.")
    parser.add_argument("--file", default="sample_cloud_config.json", help="Cloud config JSON export.")
    parser.add_argument("--min-severity", default="LOW", help="LOW|MEDIUM|HIGH|CRITICAL.")
    parser.add_argument("--json", default=None, help="Write findings to a JSON file.")
    parser.add_argument("--fail-on", default=None, help="Exit 1 if any finding >= this severity (CI gate).")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as handle:
        config = json.load(handle)

    threshold = SEVERITY_ORDER.get(args.min_severity.upper(), 1)
    findings = [f for f in scan(config) if SEVERITY_ORDER[f["severity"]] >= threshold]

    print(f"Scanned account {config.get('account_id', '<unknown>')}: "
          f"{len(findings)} finding(s) at/above {args.min_severity.upper()}\n")
    for f in findings:
        print(f"[{f['severity']:<8}] {f['resource']:<24} {f['message']}  (control {f['control']})")

    by_sev = {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
    print("\nBy severity:", ", ".join(f"{k}={v}" for k, v in sorted(
        by_sev.items(), key=lambda kv: SEVERITY_ORDER[kv[0]], reverse=True)) or "none")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(findings, handle, indent=2)
        print(f"Findings written to {args.json}")

    if args.fail_on:
        gate = SEVERITY_ORDER.get(args.fail_on.upper(), 99)
        if any(SEVERITY_ORDER[f["severity"]] >= gate for f in findings):
            print(f"\nFAIL: findings at/above {args.fail_on.upper()} present.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
