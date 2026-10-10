#!/usr/bin/env python3
"""Build schemas and project templates, documentation, or repository checks."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(*arguments):
    return subprocess.run([sys.executable, *arguments], cwd=ROOT, check=False).returncode


def check():
    cli = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec")
    if not cli:
        print("Checks require OpenSpec 1.13.1 on PATH or OPENSPEC_BIN.", file=sys.stderr)
        return 1
    version = subprocess.run([cli, "--version"], cwd=ROOT, text=True,
                             capture_output=True, check=False)
    if version.returncode or version.stdout.strip() != "1.13.1":
        print("Checks require OpenSpec 1.13.1; set OPENSPEC_BIN to that release.", file=sys.stderr)
        return version.returncode or 1
    result = run("-m", "unittest", "discover", "-s", "tests", "-v")
    if result:
        return result
    return run("scripts/md-book-builder/check.py", "--rendered")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Arguments after schemas, project_templates, or docs are forwarded to that tool. "
               "Paths are relative to the repository root. "
               "check requires a built handbook and OpenSpec 1.13.1.")
    parser.add_argument("command", nargs="?", default="bundle",
                        choices=("bundle", "schemas", "project_templates", "docs", "check", "all"),
                        help="Default: bundle (schemas and project templates). all also builds docs and runs checks.")
    parser.add_argument("arguments", nargs=argparse.REMAINDER,
                        help="Tool arguments, e.g. schemas --base --output build/custom/openspec-ddd")
    args = parser.parse_args(argv)
    if args.command in ("bundle", "check", "all") and args.arguments:
        parser.error(f"{args.command} takes no additional arguments")
    try:
        if args.command == "schemas":
            return run("scripts/schema-builder/build.py", *args.arguments)
        if args.command == "project_templates":
            return run("scripts/starter-builder/build.py", *args.arguments)
        if args.command == "bundle":
            for tool in ("schema-builder", "starter-builder"):
                result = run(f"scripts/{tool}/build.py")
                if result:
                    return result
            return 0
        if args.command == "docs":
            return run("scripts/md-book-builder/book.py", "build", *args.arguments)
        if args.command == "all":
            for arguments in (("scripts/schema-builder/build.py",),
                              ("scripts/starter-builder/build.py",),
                              ("scripts/md-book-builder/book.py", "build")):
                result = run(*arguments)
                if result:
                    return result
        return check()
    except OSError as error:
        print(f"Build command failed: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
