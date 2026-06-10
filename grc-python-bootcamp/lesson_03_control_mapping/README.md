# Lesson 3 — Control Mapping & Crosswalk Tool

**GRC problem:** You maintain one set of internal controls but report against
several frameworks (SOC 2, ISO 27001, NIST CSF). Leadership asks "if we're SOC 2
compliant, how far are we from ISO 27001?" — and an auditor asks "show me the
control that satisfies ISO A.5.17." This tool answers both from a single source
of truth.

**Python you'll learn:** the `json` module, navigating **nested** dictionaries
and lists, `set` operations for gap analysis (`required - covered`), and using
`argparse` **subcommands** to build a multi-function tool.

---

## Run it

```bash
cd lesson_03_control_mapping
python control_mapping.py list
python control_mapping.py crosswalk --framework ISO27001 --ref A.5.17
python control_mapping.py coverage --framework SOC2
python control_mapping.py gaps --framework ISO27001 --required-file iso_required.txt
```

`crosswalk` output:

```
AC-02 - Multi-factor authentication for privileged access (owner: IT)
    SOC2       CC6.1
    ISO27001   A.5.17  <- you asked about this
    NIST_CSF   PR.AC-7
```

`gaps` output:

```
ISO27001: 6/10 required requirements covered.

GAPS (required but no control maps to them):
  - A.8.15
  - A.8.34
```

## How it works

- The control library lives in **`control_mappings.json`** — keeping data
  separate from code is a core principle. Analysts edit JSON; the code never
  changes.
- `json.load()` gives you Python lists/dicts. `control["frameworks"]["ISO27001"]`
  walks the nested structure.
- **Sets** make gap analysis trivial: `required - covered` is exactly "the
  requirements we're missing." This single line replaces a painful manual
  spreadsheet diff.
- `argparse` **subcommands** (`list`, `crosswalk`, `coverage`, `gaps`) are how
  real CLIs (git, docker, aws) are structured — you'll reuse this in Lesson 9.

## Try these exercises

1. Add a new framework (e.g. `PCI_DSS`) to a couple of controls and re-run
   `crosswalk` — notice you didn't touch the code.
2. Add a `coverage --json` flag that prints machine-readable output.
3. Extend `gaps` to also print the **owner** who should build each missing
   control (you'll need the reverse lookup).

## What "good" looks like

You can explain why a set difference (`required - covered`) is the right tool
for gap analysis, and you keep *data in JSON, logic in Python*.
