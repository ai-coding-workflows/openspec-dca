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
from book_runtime import staged_book
from book_discovery import discover_books, validate_outputs
from book_servers import serve_books
from svgbob import prepare as prepare_svgbob

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
    tool_env["MDBOOK_BUILD__BUILD_DIR"] = json.dumps(str(paths.build_dir))
    svgbob = prepare_svgbob(paths.config_file, paths.output_root / "native-tools")
    if svgbob:
        tool_env["PATH"] = str(svgbob.parent) + os.pathsep + tool_env["PATH"]

    with staged_book(paths) as runtime:
        if action == "serve":
            return serve_process(
                [mdbook, "serve", "--hostname", "127.0.0.1", "--port", str(port)],
                cwd=runtime,
                env=tool_env,
                port=port,
                open_browser=open_browser,
            )

        result = run([mdbook, "build"], cwd=runtime, env=tool_env)
        if result:
            return result
        return run(
            [uv, "run", "--no-cache", "--project", str(EXPORTER_DIR), "python", str(EXPORTER_SCRIPT), str(paths.config_file)],
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
    environment["MDBOOK_BUILD__BUILD_DIR"] = json.dumps((Path("/book") / build_path).as_posix())
    environment["DOCS_BOOK_BUILD_HOST"] = paths.build_dir.as_posix()
    environment["DOCS_BOOK_BUILD_PATH"] = build_path.as_posix()
    svgbob = prepare_svgbob(paths.config_file, paths.output_root / "native-tools", docker_mode=True)
    if svgbob:
        try:
            tool_path = svgbob.parent.relative_to(REPOSITORY)
        except ValueError:
            raise ValueError("Docker svgbob cache must be inside the repository")
        environment["DOCS_SVGBOB_BIN"] = f"/book/{tool_path.as_posix()}"
    if action == "serve":
        environment["DOCS_HOST_PORT"] = str(port)
    if hasattr(os, "getuid"):
        environment["GUIDE_UID"] = str(os.getuid())
        environment["GUIDE_GID"] = str(os.getgid())

    command = [docker, "compose", "-f", str(COMPOSE_FILE)]
    with staged_book(paths, docker_mode=True) as runtime:
        book_root = runtime.relative_to(REPOSITORY)
        environment["DOCS_BOOK_ROOT"] = (Path("/book") / book_root).as_posix()
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
            [uv, "run", "--no-cache", "--project", str(EXPORTER_DIR), "python", str(EXPORTER_SCRIPT), str(paths.config_file)],
            cwd=REPOSITORY,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", "--book", help="select one book alias, directory, book.toml or *.book.toml path")
    parser.add_argument("--map", type=Path, help="book mapping TOML (default: docs-books.toml)")
    parser.add_argument("--docker", action="store_true", help="use the pinned Docker Compose mdBook image")
    parser.add_argument("--port", type=int, default=0, help="first serve port; subsequent books use available ports; 0 picks all ports")
    parser.add_argument("--no-open", action="store_true", help="do not open the served site in a browser")
    parser.add_argument("action", nargs="?", choices=("build", "serve"), default="build")
    args = parser.parse_args()

    try:
        configs = discover_books(REPOSITORY, args.book, args.map)
        books = [read_book_paths(config) for config in configs]
        validate_outputs(books)
        ports = []
        if args.action == "serve":
            ports.append(free_port(args.port))
            while len(ports) < len(books):
                port = free_port(0)
                if port not in ports:
                    ports.append(port)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 2

    try:
        if args.action == "serve" and len(books) > 1:
            return serve_books(Path(__file__).resolve(), configs, ports,
                               docker=args.docker, open_browser=not args.no_open)
        command = docker_command if args.docker else native_command
        result = 0
        for paths in books:
            print(f"Processing {paths.config_file.relative_to(REPOSITORY)}", flush=True)
            status = command(args.action, paths, ports[0] if ports else None, not args.no_open)
            result = result or status
        return result
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"docs: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
