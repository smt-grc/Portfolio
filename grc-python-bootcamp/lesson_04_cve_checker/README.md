# Lesson 4 — CVE / Vulnerability Checker (live API)

**GRC problem:** Vulnerability management (SOC 2 CC7.1, ISO 27001 A.8.8, NIST
RA-5) requires you to know which known vulnerabilities affect your stack. This
tool reads your software inventory and pulls matching CVEs straight from the
NIST National Vulnerability Database (NVD), prioritised by CVSS severity.

**Python you'll learn:** calling a REST API with `requests`, query parameters,
HTTP error/timeout handling, parsing **nested JSON**, sorting by a key, and
designing an **offline mode** so your evidence is reproducible without network.

---

## Run it

```bash
cd lesson_04_cve_checker
python cve_checker.py --offline                      # no network needed
python cve_checker.py                                # live: scans inventory.csv
python cve_checker.py --keyword log4j --min-severity CRITICAL
python cve_checker.py --min-severity HIGH --limit 5
```

Offline output:

```
Scanning 1 product(s) [OFFLINE sample], reporting severity >= HIGH

== openssl (owner: -) - 3 matching CVE(s) ==
  CVE-...           HIGH     7.5  OpenSSL and SSLeay allow remote attackers to ...
```

> **Note on NVD:** the public API is rate-limited (a few requests per 30s
> without an API key). If you hit `403`/`429`, slow down or request a free key
> at <https://nvd.nist.gov/developers/request-an-api-key>. Always start with
> `--offline` while you read the code.

## How it works

- `requests.get(url, params=..., timeout=20)` builds the query string for you
  and **never hangs forever** thanks to `timeout`.
- `response.raise_for_status()` converts a bad HTTP code into an exception we
  catch — failing loudly is the right behavior for a security tool.
- `extract_cvss()` shows the reality of real-world JSON: the score lives under
  one of several version-specific keys, so we try them in order.
- `--offline` loads `sample_cve_response.json`. Offline/sample modes are a GRC
  superpower: your evidence run produces the **same** output every time.

## Try these exercises

1. Add an `--api-key` flag and send it in the `apiKey` header for higher rate
   limits.
2. Add a `--since 2024-01-01` filter using NVD's `pubStartDate` parameter.
3. Write findings to CSV (reuse the `DictWriter` pattern from Lesson 2) so this
   feeds your remediation tracker.

## What "good" looks like

You handle the unhappy path (timeout, 403, empty results) *before* the happy
path, and you can explain why an offline mode matters for audit evidence.
