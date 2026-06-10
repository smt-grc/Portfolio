# Lesson 1 — Password Policy Checker

**GRC problem:** Almost every framework (SOC 2 CC6.1, ISO 27001 A.5.17, NIST
800-53 IA-5) requires you to enforce and *evidence* a password policy. This
tool turns a fuzzy policy statement into a repeatable check you can run on a
list of passwords and hand to an auditor as evidence.

**Python you'll learn:** variables, strings, f-strings, functions, `if`
statements, `for` loops, reading a text file, and a tiny `argparse` CLI.

---

## Run it

```bash
cd lesson_01_password_policy
python password_policy_checker.py                 # uses sample_passwords.txt
python password_policy_checker.py --min-length 14 # stricter length requirement
python password_policy_checker.py --file my_passwords.txt
```

Expected output (abridged):

```
[FAIL] p*******         -> too short (8 chars, need 12); ... ; appears on the common-password blocklist
[PASS] C************************! -> meets all policy requirements
Result: 3/10 passed (30% compliant).
```

## How it works (read the code top to bottom)

1. `DEFAULT_POLICY` is a **dictionary** — think of it as the control's
   configuration. Editing it is how a GRC analyst "tunes the control".
2. `check_password()` is a **function** that returns a *list of failures*.
   Returning structured data (instead of just printing) is the single most
   important habit in this whole course — it lets you reuse the logic later
   (Lesson 9 wraps this exact function in a CLI toolkit).
3. `load_passwords()` shows the safe file-reading pattern: `with open(...)`.
4. `main()` ties it together and **masks** passwords before printing — never
   log secrets in plaintext, even in a demo.

## Try these exercises

1. Add a rule that rejects passwords containing the user's name (hint: add a
   `--username` argument and check `username.lower() in password.lower()`).
2. Make the common-password blocklist load from a file instead of being
   hard-coded.
3. Output a CSV summary (`password_masked,status,reasons`) — this is your
   bridge to Lesson 2, which is all about CSV.

## What "good" looks like

You should be able to explain, out loud, why returning a *list of failure
reasons* is better than returning `True`/`False`. (Answer: an auditor wants to
know *why* a control failed, not just *that* it failed.)
