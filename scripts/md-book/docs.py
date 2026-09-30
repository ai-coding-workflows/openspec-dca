#!/usr/bin/env python3
"""Build or serve with native mdBook by default, or the Docker toolchain."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

from book_paths import read_book_paths

SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY = SCRIPT_DIR.parent.parent
COMPOSE_FILE = SCRIPT_DIR / "docker" / "compose.yml"
EXPORTER_DIR = SCRIPT_DIR.parent / "book-exporter"
EXPORTER_SCRIPT = EXPORTER_DIR / "export_book.py"
MD_BOOK_DOWNLOADER = SCRIPT_DIR / "download-latest-mdbook.py"


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> int:
    try:
        return subprocess.run(command, cwd=cwd, env=env, check=False).returncode
    except FileNotFoundError:
        print(f"Required command not found: {command[0]}", file=sys.stderr)
        return 127


def free_port(requested: int) -> int:
    if not 0 <= requested <= 65535:
        raise ValueError("--port must be between 0 and 65535")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", requested))
        return listener.getsockname()[1]


def serve_process(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None,
    port: int,
    open_browser: bool,
) -> int:
    url = f"http://127.0.0.1:{port}/"
    try:
        process = subprocess.Popen(command, cwd=cwd, env=env)
    except OSError as exc:
        print(f"Could not start documentation server: {exc}", file=sys.stderr)
        return 127

    deadline = time.monotonic() + 60
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return process.returncode or 1
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if response.status < 500:
                        break
            except OSError:
                time.sleep(0.25)
        else:
            print(f"Documentation server did not become ready at {url}", file=sys.stderr)
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            return 1

        print(f"Serving documentation at {url}", flush=True)
        if open_browser:
            try:
                if not webbrowser.open(url, new=2):
                    print(f"Open this URL in your browser: {url}", file=sys.stderr)
            except webbrowser.Error as exc:
                print(f"Could not open a browser ({exc}); open {url}", file=sys.stderr)
        return process.wait()
    except KeyboardInterrupt:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        return 130


def native_command(action: str, paths, port: int | None, open_browser: bool) -> int:
    uv = shutil.which("uv")
    if action == "build" and not uv:
        print("native docs build requires uv to export the single-file handbook.", file=sys.stderr)
        return 127

    commands = {
        "mdbook": shutil.which("mdbook"),
        "mdbook-mermaid": shutil.which("mdbook-mermaid"),
    }
    missing = [name for name, command in commands.items() if not command]
    if missing:
        cache_dir = paths.output_root / "native-tools"
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
        try:
            installed = json.loads(downloaded.stdout.strip().splitlines()[-1])
            for name in missing:
                commands[name] = installed[name]
        except (IndexError, KeyError, json.JSONDecodeError):
            print("mdBook toolchain downloader returned an invalid result.", file=sys.stderr)
            return 1
        if downloaded.stderr:
            print(downloaded.stderr, end="", file=sys.stderr)
    else:
        for name, command in commands.items():
            print(f"Using {name} from PATH: {command}", file=sys.stderr)

    mdbook = commands["mdbook"]
    mermaid = commands["mdbook-mermaid"]
    if not mdbook or not mermaid:
        print("mdBook toolchain installation is incomplete.", file=sys.stderr)
        return 1
    tool_env = os.environ.copy()
    tool_dirs = os.pathsep.join(
        dict.fromkeys((str(Path(mdbook).parent), str(Path(mermaid).parent)))
    )
    tool_env["PATH"] = tool_dirs + os.pathsep + tool_env.get("PATH", "")

    if action == "serve":
        return serve_process(
            [mdbook, "serve", "--hostname", "127.0.0.1", "--port", str(port)],
            cwd=REPOSITORY,
            env=tool_env,
            port=port,
            open_browser=open_browser,
        )

    result = run([mdbook, "build"], cwd=REPOSITORY, env=tool_env)
    if result:
        return result
    return run(
        [uv, "run", "--no-cache", "--project", str(EXPORTER_DIR), "python", str(EXPORTER_SCRIPT), str(REPOSITORY / "book.toml")],
        cwd=REPOSITORY,
    )


def docker_command(action: str, paths, port: int | None, open_browser: bool) -> int:
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
    if action == "serve":
        environment["DOCS_HOST_PORT"] = str(port)
    if hasattr(os, "getuid"):
        environment["GUIDE_UID"] = str(os.getuid())
        environment["GUIDE_GID"] = str(os.getgid())

    command = [docker, "compose", "-f", str(COMPOSE_FILE)]
    result = run([*command, "build", "handbook"], cwd=REPOSITORY, env=environment)
    if result:
        return result
    if action == "serve":
        return serve_process(
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
            port=port,
            open_browser=open_browser,
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
    parser.add_argument("--docker", action="store_true", help="use the pinned Docker Compose mdBook image")
    parser.add_argument("--port", type=int, default=0, help="serve port; 0 picks an available port")
    parser.add_argument("--no-open", action="store_true", help="do not open the served site in a browser")
    parser.add_argument("action", nargs="?", choices=("build", "serve"), default="build")
    args = parser.parse_args()

    try:
        paths = read_book_paths(REPOSITORY / "book.toml")
        port = free_port(args.port) if args.action == "serve" else None
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    if args.docker:
        return docker_command(args.action, paths, port, not args.no_open)
    return native_command(args.action, paths, port, not args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
