"""`grctool passwords` - a compact version of Lesson 1's policy checker.

Each toolkit module exposes two things the CLI relies on:
  * add_parser(subparsers) - registers the subcommand and its arguments
  * run(args)              - executes the subcommand
"""

import string

COMMON = {"password", "password1", "123456", "qwerty", "letmein", "admin", "changeme"}


def check_password(password, min_length):
    failures = []
    if len(password) < min_length:
        failures.append(f"too short (<{min_length})")
    if not any(c.isupper() for c in password):
        failures.append("no uppercase")
    if not any(c.islower() for c in password):
        failures.append("no lowercase")
    if not any(c.isdigit() for c in password):
        failures.append("no digit")
    if not any(c in string.punctuation for c in password):
        failures.append("no symbol")
    if password.lower() in COMMON:
        failures.append("blocklisted")
    return failures


def add_parser(subparsers):
    parser = subparsers.add_parser("passwords", help="Check passwords against the policy.")
    parser.add_argument("--file", required=True, help="File with one password per line.")
    parser.add_argument("--min-length", type=int, default=12)
    parser.set_defaults(func=run)


def run(args):
    with open(args.file, "r", encoding="utf-8") as handle:
        passwords = [line.strip() for line in handle if line.strip()]
    passed = 0
    for pw in passwords:
        failures = check_password(pw, args.min_length)
        masked = pw[0] + "*" * (len(pw) - 1) if pw else ""
        if failures:
            print(f"[FAIL] {masked:<14} {', '.join(failures)}")
        else:
            passed += 1
            print(f"[PASS] {masked:<14}")
    print(f"\n{passed}/{len(passwords)} passwords compliant.")
    return 0 if passed == len(passwords) else 1
