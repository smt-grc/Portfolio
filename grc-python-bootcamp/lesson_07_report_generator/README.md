# Lesson 7 — Automated Compliance Report Generator (Jinja2)

**GRC problem:** Every quarter you hand-build the same status report (control
status, top risks, evidence freshness) in a doc. It's slow and drifts out of
date. This tool renders a Markdown report from a JSON data file via a template,
so regenerating it after each control test takes one command.

**Python you'll learn:** the **Jinja2** templating engine — loading templates,
passing a context dict, and using template loops, conditionals, and filters
(`selectattr`, `join`, `length`). This is the same engine Ansible and Flask use.

> New dependency: `jinja2`. Install with `pip install -r ../requirements.txt`.

---

## Run it

```bash
cd lesson_07_report_generator
python report_generator.py                 # prints the report to the terminal
python report_generator.py --out report.md # also saves report.md
```

It reads `report_data.json` + `templates/compliance_report.md.j2` and produces a
clean Markdown report with a control table, controls-needing-attention list, top
risks, and an evidence-freshness section that shows an ACTION REQUIRED callout
only when something is overdue.

## How it works

- **Separation of concerns:** `report_data.json` is the data (often produced by
  Lessons 3/5/6), `templates/*.j2` is the layout. Analysts edit the template;
  engineers feed it data.
- `Environment(loader=FileSystemLoader("templates"))` is the standard way to
  load templates from disk.
- Inside the template, `{% for c in controls %}` loops, `{% if ... %}` branches,
  and **filters** like `controls | selectattr("status","equalto","Deficient")`
  do real logic without leaving the template.
- `trim_blocks`/`lstrip_blocks` keep the Markdown tidy (no stray blank lines).

## Try these exercises

1. Wire it together: have Lesson 6 write `top_risks` into the JSON, then
   regenerate the report — a real pipeline.
2. Add an HTML template (`compliance_report.html.j2`) and render that too. Note
   `autoescape` is already on for `.html`/`.xml`.
3. Add a `{{ generated_on }}`-based filename so each run is archived.

## What "good" looks like

You keep layout in templates and data in JSON, and you can regenerate a
board-ready report from fresh data with a single command.
