"""Lesson 4 - CVE / Vulnerability Checker (live API).

A GRC tool that reads your software inventory (CSV) and queries the public NIST
National Vulnerability Database (NVD) for known CVEs affecting each product,
then filters to the severities you care about. This is the heart of a
vulnerability-management control (SOC 2 CC7.1, ISO 27001 A.8.8).

Concepts taught: calling a REST API with `requests`, query parameters, HTTP
status / timeout / error handling, parsing nested JSON responses, and a clean
*offline mode* so the tool still runs (and your evidence stays reproducible)
when you have no network.

Run it:
    python cve_checker.py --offline                 # uses bundled sample data
    python cve_checker.py                            # live query for each inventory row
    python cve_checker.py --keyword openssl --min-severity HIGH
    python cve_checker.py --min-severity CRITICAL --limit 5
"""

import argparse
import csv
import json
import sys

import requests

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "UNKNOWN": 0}


def extract_cvss(cve):
    """Pull (baseScore, baseSeverity) out of NVD's nested metrics block.

    NVD reports CVSS under several keys depending on the scoring version, so we
    try them in order of preference.
    """
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        entries = metrics.get(key)
        if entries:
            data = entries[0]["cvssData"]
            return data.get("baseScore", 0.0), data.get("baseSeverity", "UNKNOWN")
    return 0.0, "UNKNOWN"


def first_description(cve):
    for desc in cve.get("descriptions", []):
        if desc.get("lang") == "en":
            return desc.get("value", "")
    return ""


def fetch_cves(keyword, limit, offline):
    """Return the raw NVD 'vulnerabilities' list for a keyword.

    In offline mode we load a bundled sample file instead of hitting the API.
    """
    if offline:
        with open("sample_cve_response.json", "r", encoding="utf-8") as handle:
            return json.load(handle).get("vulnerabilities", [])

    params = {"keywordSearch": keyword, "resultsPerPage": limit}
    try:
        response = requests.get(NVD_URL, params=params, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"  ! network error querying NVD for '{keyword}': {exc}", file=sys.stderr)
        return []
    return response.json().get("vulnerabilities", [])


def filter_and_format(vulns, min_severity):
    """Turn raw NVD entries into simple dicts at or above min_severity."""
    threshold = SEVERITY_ORDER.get(min_severity.upper(), 0)
    results = []
    for entry in vulns:
        cve = entry["cve"]
        score, severity = extract_cvss(cve)
        if SEVERITY_ORDER.get(severity.upper(), 0) < threshold:
            continue
        results.append({
            "id": cve["id"],
            "score": score,
            "severity": severity,
            "summary": first_description(cve)[:100],
        })
    # Highest score first - that's the remediation priority order.
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def load_inventory(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser(description="Check software inventory against the NVD CVE database.")
    parser.add_argument("--file", default="inventory.csv", help="Inventory CSV (product,keyword,owner).")
    parser.add_argument("--keyword", default=None, help="Check a single keyword instead of the inventory file.")
    parser.add_argument("--min-severity", default="HIGH", help="LOW|MEDIUM|HIGH|CRITICAL (default HIGH).")
    parser.add_argument("--limit", type=int, default=10, help="Max CVEs to request per product.")
    parser.add_argument("--offline", action="store_true", help="Use bundled sample data (no network).")
    args = parser.parse_args()

    if args.offline:
        # Offline mode uses one bundled dataset, so scan a single sample target
        # rather than re-loading the same file for every inventory row.
        targets = [{"product": "sample dataset", "keyword": "sample", "owner": "-"}]
    elif args.keyword:
        targets = [{"product": args.keyword, "keyword": args.keyword, "owner": "-"}]
    else:
        targets = load_inventory(args.file)

    mode = "OFFLINE sample" if args.offline else "LIVE NVD API"
    print(f"Scanning {len(targets)} product(s) [{mode}], reporting severity >= {args.min_severity.upper()}\n")

    grand_total = 0
    for target in targets:
        vulns = fetch_cves(target["keyword"], args.limit, args.offline)
        findings = filter_and_format(vulns, args.min_severity)
        grand_total += len(findings)
        print(f"== {target['product']} (owner: {target['owner']}) - {len(findings)} matching CVE(s) ==")
        for f in findings:
            print(f"  {f['id']:<18} {f['severity']:<8} {f['score']:<4} {f['summary']}")
        if not findings:
            print("  (none at this severity)")
        print()

    print(f"Total CVEs at/above {args.min_severity.upper()}: {grand_total}")


if __name__ == "__main__":
    main()
