"""Lesson 3 - Control Mapping & Crosswalk Tool.

A GRC tool that loads a control library (JSON) where each internal control is
mapped to one or more framework requirements (SOC 2, ISO 27001, NIST CSF). It
answers the two questions you get asked constantly:

    1. "We already do SOC 2 - what does ISO 27001 add?"  -> crosswalk
    2. "Which framework requirements aren't covered yet?" -> gap analysis

Concepts taught: the `json` module, nested dictionaries and lists, `set`
operations (for gap analysis), and structuring a program into small functions.

Run it:
    python control_mapping.py list
    python control_mapping.py crosswalk --framework ISO27001 --ref A.5.17
    python control_mapping.py coverage --framework SOC2
    python control_mapping.py gaps --framework ISO27001 --required-file iso_required.txt
"""

import argparse
import json


def load_library(path):
    """Load the control library JSON into a list of control dicts."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)["controls"]


def cmd_list(controls, _args):
    """Print every internal control and its framework references."""
    for control in controls:
        refs = ", ".join(
            f"{fw}:{'/'.join(ids)}" for fw, ids in control["frameworks"].items()
        )
        print(f"{control['id']:<6} {control['name']:<45} [{refs}]")


def cmd_crosswalk(controls, args):
    """Given a framework requirement, show the internal control AND the
    equivalent requirements in every other framework."""
    matches = [
        c for c in controls
        if args.ref in c["frameworks"].get(args.framework, [])
    ]
    if not matches:
        print(f"No internal control maps to {args.framework} {args.ref}.")
        return
    for control in matches:
        print(f"{control['id']} - {control['name']} (owner: {control['owner']})")
        for fw, ids in control["frameworks"].items():
            marker = "  <- you asked about this" if fw == args.framework else ""
            print(f"    {fw:<10} {', '.join(ids)}{marker}")


def cmd_coverage(controls, args):
    """List every requirement of a framework that IS covered by a control."""
    covered = {}  # framework ref -> internal control id
    for control in controls:
        for ref in control["frameworks"].get(args.framework, []):
            covered.setdefault(ref, []).append(control["id"])
    if not covered:
        print(f"No controls reference framework '{args.framework}'.")
        return
    print(f"{args.framework} requirements currently covered:")
    for ref in sorted(covered):
        print(f"  {ref:<10} <- {', '.join(covered[ref])}")
    print(f"\nTotal covered requirements: {len(covered)}")


def cmd_gaps(controls, args):
    """Compare the framework requirements we cover against a list of ALL
    required references (one per line in --required-file). Print the gaps."""
    covered = set()
    for control in controls:
        covered.update(control["frameworks"].get(args.framework, []))

    with open(args.required_file, "r", encoding="utf-8") as handle:
        required = {line.strip() for line in handle if line.strip()}

    gaps = required - covered           # set difference: required but not covered
    extra = covered - required          # covered but not in the required list

    print(f"{args.framework}: {len(covered & required)}/{len(required)} required "
          f"requirements covered.\n")
    if gaps:
        print("GAPS (required but no control maps to them):")
        for ref in sorted(gaps):
            print(f"  - {ref}")
    else:
        print("No gaps - every required reference is covered.")
    if extra:
        print("\nNote - controls reference these, but they're not in your required list:")
        for ref in sorted(extra):
            print(f"  ? {ref}")


def main():
    parser = argparse.ArgumentParser(description="Map and crosswalk GRC controls across frameworks.")
    parser.add_argument("--file", default="control_mappings.json", help="Control library JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all internal controls.")

    p_cross = sub.add_parser("crosswalk", help="Crosswalk one framework reference to the others.")
    p_cross.add_argument("--framework", required=True, help="e.g. SOC2, ISO27001, NIST_CSF")
    p_cross.add_argument("--ref", required=True, help="e.g. A.5.17")

    p_cov = sub.add_parser("coverage", help="Show covered requirements for a framework.")
    p_cov.add_argument("--framework", required=True)

    p_gaps = sub.add_parser("gaps", help="Gap analysis against a required-references file.")
    p_gaps.add_argument("--framework", required=True)
    p_gaps.add_argument("--required-file", required=True)

    args = parser.parse_args()
    controls = load_library(args.file)

    dispatch = {
        "list": cmd_list,
        "crosswalk": cmd_crosswalk,
        "coverage": cmd_coverage,
        "gaps": cmd_gaps,
    }
    dispatch[args.command](controls, args)


if __name__ == "__main__":
    main()
