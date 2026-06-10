"""Lesson 7 - Automated Compliance Report Generator (Jinja2).

A GRC tool that turns structured program data (JSON) into a polished Markdown
compliance status report using a template. Separating the *content* (a template
an analyst can edit) from the *data* (JSON produced by your other tools) is how
you generate board decks and audit status updates without copy-paste.

Concepts taught: the `jinja2` templating engine, loading templates from a
folder, passing a context dict, template loops/conditionals/filters, and
writing the rendered output to a file.

Run it:
    python report_generator.py                       # prints the report
    python report_generator.py --out report.md       # also saves it
    python report_generator.py --data report_data.json --template compliance_report.md.j2
"""

import argparse
import json
from datetime import date

from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_data(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def render(data, template_dir, template_name):
    """Render the template with the given data context."""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_name)
    # The context dict's keys become variables inside the template.
    context = dict(data)
    context["generated_on"] = date.today().isoformat()
    return template.render(**context)


def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown compliance report from JSON data.")
    parser.add_argument("--data", default="report_data.json", help="JSON data file.")
    parser.add_argument("--template-dir", default="templates", help="Folder containing the template.")
    parser.add_argument("--template", default="compliance_report.md.j2", help="Template filename.")
    parser.add_argument("--out", default=None, help="Optional path to write the rendered report.")
    args = parser.parse_args()

    data = load_data(args.data)
    output = render(data, args.template_dir, args.template)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(output)
        print(f"Report written to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
