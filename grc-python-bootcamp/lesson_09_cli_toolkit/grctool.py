"""Lesson 9 - The `grctool` CLI Toolkit.

This ties the earlier lessons together into ONE command with subcommands:

    grctool passwords     --file ...
    grctool access-review --file ...
    grctool evidence      --file ...

Concepts taught: how to structure a real command-line tool with `argparse`
subparsers, a Python *package* (the `grctoolkit/` folder), per-command modules
that register themselves, and meaningful **exit codes** so the tool can be used
in automation.

Run it:
    python grctool.py --help
    python grctool.py passwords --file ../lesson_01_password_policy/sample_passwords.txt
    python grctool.py access-review --file ../lesson_02_access_review/sample_users.csv --today 2026-06-10
    python grctool.py evidence --file ../lesson_05_evidence_tracker/evidence_register.csv --today 2026-06-10
"""

import argparse
import sys

from grctoolkit import __version__, access, evidence, passwords

# Every module that adds a subcommand. To add a new command, write a module with
# add_parser()/run() and append it here - the rest of the CLI is untouched.
MODULES = [passwords, access, evidence]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="grctool",
        description="A small GRC automation toolkit (Devin's Python-for-GRC course).",
    )
    parser.add_argument("--version", action="version", version=f"grctool {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for module in MODULES:
        module.add_parser(subparsers)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    # Each subcommand set args.func via set_defaults(func=run).
    exit_code = args.func(args)
    sys.exit(exit_code or 0)


if __name__ == "__main__":
    main()
