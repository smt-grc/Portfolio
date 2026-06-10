# Lesson 9 — The `grctool` CLI Toolkit

**GRC problem:** By now you have several separate scripts. Real users (and
schedulers) want *one* tool with subcommands, consistent flags, and proper exit
codes — like `git`, `aws`, or `kubectl`. This lesson packages your work into a
single `grctool` command.

**Python you'll learn:** structuring a multi-command CLI with `argparse`
**subparsers**, building a Python **package** (`grctoolkit/` with
`__init__.py`), the self-registering module pattern (`add_parser`/`run`), and
returning **exit codes** for automation.

---

## Run it

```bash
cd lesson_09_cli_toolkit
python grctool.py --help
python grctool.py --version

python grctool.py passwords     --file ../lesson_01_password_policy/sample_passwords.txt
python grctool.py access-review --file ../lesson_02_access_review/sample_users.csv --today 2026-06-10
python grctool.py evidence      --file ../lesson_05_evidence_tracker/evidence_register.csv --today 2026-06-10
echo "last command exit code: $?"
```

## How it works

- `grctool.py` is the **entrypoint**. It builds the parser, asks each module to
  register its subcommand, parses args, and calls `args.func(args)`.
- `grctoolkit/` is a **package** (because it has `__init__.py`). Each module
  (`passwords.py`, `access.py`, `evidence.py`) owns one subcommand and exposes:
  - `add_parser(subparsers)` — declares the command + its flags
  - `run(args)` — does the work and **returns an exit code**
- `MODULES = [...]` is the registry. Adding a command is: write a module, add it
  to the list. Nothing else changes — this is the open/closed principle in
  practice.
- Exit codes matter: `passwords` returns `1` if any password fails, so
  `grctool.py ... && deploy.sh` won't deploy on a failure.

## Make it a real installed command (optional)

Add a `pyproject.toml` with a console-script entry point so you can type
`grctool` anywhere:

```toml
[project]
name = "grctoolkit"
version = "0.1.0"
[project.scripts]
grctool = "grctoolkit.cli:main"   # move grctool.py's main() into the package
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```

Then `pip install -e .` and run `grctool --help` from any directory.

## Try these exercises

1. Add a `risk` subcommand that wraps Lesson 6 (you'll add `pandas`).
2. Add a global `--quiet` flag handled in `main()` before dispatch.
3. Convert it to an installable package using the `pyproject.toml` above.

## What "good" looks like

You can add a brand-new subcommand without editing `grctool.py`'s logic, and
every subcommand returns a meaningful exit code.
