#!/usr/bin/env python3
"""Build or serve the handbook with Docker Compose or a native mdBook binary."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from book_paths import read_book_paths


SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY = SCRIPT_DIR.parent
COMPOSE_FILE = SCRIPT_DIR / "md-book" / "compose.yml"
EXPORTER_DIR = SCRIPT_DIR / "book-exporter"
EXPORTER_SCRIPT = EXPORTER_DIR / "export_book.py"
MD_BOOK_DOWNLOADER = SCRIPT_DIR / "md-book" / "download-latest-mdbook.py"


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> int:
    try:
        return subprocess.run(command, cwd=cwd, env=env, check=False).returncode
    except FileNotFoundError:
        print(f"Required command not found: {command[0]}", file=sys.stderr)
        return 127


def native_command(action: str, paths) -> int:
    uv = shutil.which("uv")
    if action == "build" and not uv:
        print("native docs build requires uv to export the single-file handbook.", file=sys.stderr)
        return 127

    mdbook = shutil.which("mdbook")
    if mdbook:
        print(f"Using mdBook from PATH: {mdbook}", file=sys.stderr)
    else:
        cache_dir = paths.output_root / "native-tools" / "mdbook"
        downloaded = subprocess.run(
            [sys.executable, str(MD_BOOK_DOWNLOADER), str(cache_dir)],
            cwd=REPOSITORY,
            text=True,
            capture_output=True,
            check=False,
        )
        if downloaded.returncode:
            if downloaded.stdout:
                print(downloaded.stdout, end="", file=sys.stderr)
            if downloaded.stderr:
                print(downloaded.stderr, end="", file=sys.stderr)
            return downloaded.returncode
        mdbook = downloaded.stdout.strip().splitlines()[-1]
        if downloaded.stderr:
            print(downloaded.stderr, end="", file=sys.stderr)

    if action == "serve":
        return run(
            [mdbook, "serve", "--hostname", "127.0.0.1", "--port", "3002"],
            cwd=REPOSITORY,
        )

    result = run([mdbook, "build"], cwd=REPOSITORY)
    if result:
        return result
    return run(
        [uv, "run", "--no-cache", "--project", str(EXPORTER_DIR), "python", str(EXPORTER_SCRIPT), str(REPOSITORY / "book.toml")],
        cwd=REPOSITORY,
    )


def docker_command(action: str, paths) -> int:
    docker = shutil.which("docker")
    if not docker:
        print("Docker mode requires the docker command.", file=sys.stderr)
        return 127
    uv = shutil.which("uv")
    if action == "build" and not uv:
        print("Handbook export requires uv.", file=sys.stderr)
        return 127

    try:
        build_path = paths.build_dir.relative_to(REPOSITORY)
    except ValueError:
        print("Docker mode requires [build].build-dir to be inside the repository.", file=sys.stderr)
        return 2
    if not build_path.parts:
        print("Docker mode cannot use the repository root as [build].build-dir.", file=sys.stderr)
        return 2

    paths.build_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["DOCS_BOOK_BUILD_HOST"] = paths.build_dir.as_posix()
    environment["DOCS_BOOK_BUILD_PATH"] = build_path.as_posix()
    if hasattr(os, "getuid"):
        environment["GUIDE_UID"] = str(os.getuid())
        environment["GUIDE_GID"] = str(os.getgid())

    command = [docker, "compose", "-f", str(COMPOSE_FILE)]
    result = run([*command, "build", "handbook"], cwd=REPOSITORY, env=environment)
    if result:
        return result
    if action == "serve":
        return run(
            [
                *command,
                "run",
                "--rm",
                "--no-deps",
                "--service-ports",
                "handbook",
                "serve",
                "--hostname",
                "0.0.0.0",
                "--port",
                "3002",
            ],
            cwd=REPOSITORY,
            env=environment,
        )

    result = run([*command, "run", "--rm", "--no-deps", "handbook", "build"], cwd=REPOSITORY, env=environment)
    if result:
        return result
    return run(
        [uv, "run", "--no-cache", "--project", str(EXPORTER_DIR), "python", str(EXPORTER_SCRIPT), str(REPOSITORY / "book.toml")],
        cwd=REPOSITORY,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true", help="use mdBook from PATH or fetch its latest release")
    parser.add_argument("action", nargs="?", choices=("build", "serve"), default="build")
    args = parser.parse_args()

    try:
        paths = read_book_paths(REPOSITORY / "book.toml")
    except (ValueError, RuntimeError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    if args.native:
        return native_command(args.action, paths)
    return docker_command(args.action, paths)


if __name__ == "__main__":
    raise SystemExit(main())
