"""Lesson 1 - Password Policy Checker.

A GRC tool that checks whether passwords meet your organization's password
policy. Use it to audit a list of sample/temporary passwords, validate a
proposed policy, or demonstrate control effectiveness for an auditor.

Concepts taught: variables, strings, f-strings, functions, conditionals,
loops, reading a text file, and a tiny command-line interface (argparse).

Run it:
    python password_policy_checker.py                 # checks the bundled sample file
    python password_policy_checker.py --file my.txt   # checks your own file (one password per line)
    python password_policy_checker.py --min-length 14 # enforce a stricter length
"""

import argparse
import string

# --- The policy ------------------------------------------------------------
# In GRC terms, this dict is the "control configuration". Change these values
# to match the password policy in your security standard (e.g. NIST 800-63B,
# CIS, or your own ISMS policy).
DEFAULT_POLICY = {
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_symbol": True,
}

# A small list of passwords we never want to see, no matter what.
COMMON_PASSWORDS = {
    "password", "password1", "123456", "qwerty", "letmein",
    "admin", "welcome", "changeme", "iloveyou", "abc123",
}


def check_password(password, policy):
    """Check one password against the policy.

    Returns a list of human-readable failure messages. An empty list means
    the password passed every rule.
    """
    failures = []

    if len(password) < policy["min_length"]:
        failures.append(
            f"too short ({len(password)} chars, need {policy['min_length']})"
        )

    if policy["require_uppercase"] and not any(c in string.ascii_uppercase for c in password):
        failures.append("missing an uppercase letter")

    if policy["require_lowercase"] and not any(c in string.ascii_lowercase for c in password):
        failures.append("missing a lowercase letter")

    if policy["require_digit"] and not any(c in string.digits for c in password):
        failures.append("missing a digit")

    if policy["require_symbol"] and not any(c in string.punctuation for c in password):
        failures.append("missing a symbol")

    if password.lower() in COMMON_PASSWORDS:
        failures.append("appears on the common-password blocklist")

    return failures


def load_passwords(path):
    """Read passwords from a file, one per line, ignoring blank lines."""
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def build_policy(args):
    """Start from the default policy and apply any command-line overrides."""
    policy = dict(DEFAULT_POLICY)
    if args.min_length is not None:
        policy["min_length"] = args.min_length
    return policy


def main():
    parser = argparse.ArgumentParser(description="Check passwords against a GRC password policy.")
    parser.add_argument("--file", default="sample_passwords.txt",
                        help="Path to a file with one password per line.")
    parser.add_argument("--min-length", type=int, default=None,
                        help="Override the minimum password length.")
    args = parser.parse_args()

    policy = build_policy(args)
    passwords = load_passwords(args.file)

    print(f"Auditing {len(passwords)} password(s) against policy: min_length="
          f"{policy['min_length']}, upper/lower/digit/symbol required\n")

    passed = 0
    for password in passwords:
        # Never print the real password in full - mask it like an auditor would.
        masked = password[0] + "*" * (len(password) - 1) if password else ""
        failures = check_password(password, policy)
        if failures:
            print(f"[FAIL] {masked:<16} -> {'; '.join(failures)}")
        else:
            passed += 1
            print(f"[PASS] {masked:<16} -> meets all policy requirements")

    total = len(passwords)
    rate = (passed / total * 100) if total else 0
    print(f"\nResult: {passed}/{total} passed ({rate:.0f}% compliant).")


if __name__ == "__main__":
    main()
