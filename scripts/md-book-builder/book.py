#!/usr/bin/env python3
"""Build, preview, or export mdBook documentation with native Python tooling."""

from __future__ import annotations

import argparse
import hashlib
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

from book_paths import read_book_paths, tomllib
from book_root import resolve_project_root
from book_features import feature_policy
from book_toml import update_book_config
from mermaid_assets import native_mermaid_assets, ensure_mermaid_assets
from book_environment import container_path, javascript_environment, capture_environment, requires_asset_staging
from book_runtime import staged_book
from book_discovery import validate_outputs
from book_selection import EXPORT_FORMATS, select_books
from book_servers import serve_books
from book_capture import BookCaptureError, capture_book, capture_output
from pdf_runtime import PdfEnvironmentError, ensure_pdf_python
from svgbob import prepare as prepare_svgbob

SCRIPT_DIR = Path(__file__).resolve().parent
try:
    REPOSITORY = resolve_project_root(builder_dir=SCRIPT_DIR)
except ValueError:
    REPOSITORY = Path.cwd().resolve()  # Allow --help/import before explicit CLI --root.
COMPOSE_FILE = SCRIPT_DIR / "docker" / "compose.yml"
EXPORTER_DIR = SCRIPT_DIR / "exporter"
EXPORTER_SCRIPT = EXPORTER_DIR / "export_book.py"
CAPTURE_BACKEND = SCRIPT_DIR / "capture_backend.py"
MD_BOOK_DOWNLOADER = SCRIPT_DIR / "download-latest-mdbook.py"
NATIVE_TOOLS_CACHE = SCRIPT_DIR / ".cache" / "native-tools"


def requires_mermaid(config_file: Path) -> bool:
    """Only provision the standard preprocessor; custom commands are author-owned."""
    if tomllib is None:
        raise RuntimeError("Reading book.toml requires Python 3.11+ or tomli")
    config = tomllib.loads(config_file.read_text(encoding="utf-8"))
    preprocessors = config.get("preprocessor", {})
    if not isinstance(preprocessors, dict):
        raise ValueError("[preprocessor] must be a table")
    options = preprocessors.get("mermaid")
    if options is None:
        return False
    if not isinstance(options, dict):
        raise ValueError("[preprocessor.mermaid] must be a table")
    return options.get("command", "mdbook-mermaid") == "mdbook-mermaid"


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


def stop_process(process) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def wait_for_server(process, url: str) -> int:
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return process.returncode or 1
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return 0
        except OSError:
            time.sleep(0.25)
    print(f"Documentation server did not become ready at {url}", file=sys.stderr)
    stop_process(process)
    return 1


def open_server_browser(url: str) -> None:
    try:
        if not webbrowser.open(url, new=2):
            print(f"Open this URL in your browser: {url}", file=sys.stderr)
    except webbrowser.Error as exc:
        print(f"Could not open a browser ({exc}); open {url}", file=sys.stderr)


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

    try:
        result = wait_for_server(process, url)
        if result:
            return result
        print(f"Serving documentation at {url}", flush=True)
        if open_browser:
            open_server_browser(url)
        return process.wait()
    except KeyboardInterrupt:
        if process.poll() is None:
            stop_process(process)
        return 130


def download_native_tools(paths, commands, missing) -> int:
    downloaded = subprocess.run(
        [sys.executable, str(MD_BOOK_DOWNLOADER), str(NATIVE_TOOLS_CACHE), *missing],
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
    return 0


def native_toolchain(paths, *, mermaid: bool | None = None) -> tuple[dict[str, str | None], int]:
    """Find native tools, downloading only those missing from PATH."""
    required = ["mdbook"]
    if requires_mermaid(paths.config_file) if mermaid is None else mermaid:
        required.append("mdbook-mermaid")
    commands = {name: shutil.which(name) for name in required}
    missing = [name for name, command in commands.items() if not command]
    if missing:
        return commands, download_native_tools(paths, commands, missing)
    else:
        for name, command in commands.items():
            print(f"Using {name} from PATH: {command}", file=sys.stderr)

    return commands, 0


def export_command(paths, output_format: str = "markdown", template: Path | None = None, *,
                   allow_install: bool = True, render_context: Path | None = None) -> int:
    python = sys.executable
    if output_format == "pdf":
        try:
            python = str(ensure_pdf_python(SCRIPT_DIR, allow_install=allow_install))
        except PdfEnvironmentError as exc:
            print(f"book: {exc}", file=sys.stderr)
            return 2
    command = [python, str(EXPORTER_SCRIPT), "--format", output_format]
    if template is not None:
        command.extend(["--template", str(template)])
    if render_context is not None:
        command.extend(["--render-context", str(render_context)])
    command.append(str(paths.config_file))
    return run(command, cwd=REPOSITORY)


def export_commands(paths, output_formats: tuple[str, ...], template: Path | None = None, *,
                    allow_install: bool = True, render_context: Path | None = None) -> int:
    result = 0
    for output_format in dict.fromkeys(output_formats):
        status = export_command(paths, output_format, template, allow_install=allow_install,
                                render_context=render_context)
        result = result or status
    return result


def run_native_capture(destination: Path, mdbook: str, runtime: Path, environment) -> int:
    capture_env = capture_environment(environment, capture_output([sys.executable, str(CAPTURE_BACKEND)]))
    return run([mdbook, "build", "--dest-dir", str(destination)], cwd=runtime, env=capture_env)


def run_docker_capture(destination: Path, command: list[str], environment) -> int:
    output = capture_output(["python3", "/book-builder/capture_backend.py"])
    capture_env = capture_environment(environment, output)
    capture_env["DOCS_EXPORT_HOST"] = str(destination.parent)
    return run([*command, "run", "--rm", "--no-deps", "-e", f"MDBOOK_OUTPUT={output}",
                "-e", "MDBOOK_BUILD__CREATE_MISSING=false",
                "handbook", "build", "--dest-dir", "/book-export/output"],
               cwd=REPOSITORY, env=capture_env)


def prepared_svgbob(paths, *, enabled=None, docker_mode=False):
    options = {"docker_mode": True} if docker_mode else {}
    if enabled is not None:
        options["enabled"] = enabled
    return prepare_svgbob(paths.config_file, NATIVE_TOOLS_CACHE, **options)


def native_command(action: str, paths, port: int | None, open_browser: bool, *,
                   output_formats: tuple[str, ...] = ("markdown",), template: Path | None = None,
                   allow_install: bool = True, mermaid: bool | None = None,
                   svgbob: bool | None = None) -> int:
    policy = feature_policy(paths.config_file, mermaid=mermaid, svgbob=svgbob)
    commands, result = (native_toolchain(paths) if mermaid is None
                        else native_toolchain(paths, mermaid=policy.mermaid))
    if result:
        return result
    mdbook = commands["mdbook"]
    if not mdbook or not all(commands.values()):
        print("mdBook toolchain installation is incomplete.", file=sys.stderr)
        return 1
    tool_env = os.environ.copy()
    tool_dirs = os.pathsep.join(
        dict.fromkeys(str(Path(command).parent) for command in commands.values() if command)
    )
    tool_env["PATH"] = tool_dirs + os.pathsep + tool_env.get("PATH", "")
    tool_env["MDBOOK_BUILD__BUILD_DIR"] = json.dumps(str(paths.build_dir))
    bob = prepared_svgbob(paths, enabled=svgbob)
    if bob:
        tool_env["PATH"] = str(bob.parent) + os.pathsep + tool_env["PATH"]
    assets = native_mermaid_assets(Path(commands["mdbook-mermaid"]), SCRIPT_DIR) if policy.mermaid else ()
    update_book_config(paths.config_file, mermaid=policy.mermaid, svgbob=policy.svgbob, assets=assets)
    staging = {"force": True} if requires_asset_staging(paths.config_file, SCRIPT_DIR) else {}
    with staged_book(paths, **staging) as runtime:
        tool_env.update(javascript_environment(paths.config_file, project_root=REPOSITORY,
                                               builder_dir=SCRIPT_DIR, runtime=runtime))
        if action == "serve":
            return serve_process(
                [mdbook, "serve", "--hostname", "127.0.0.1", "--port", str(port)],
                cwd=runtime,
                env=tool_env,
                port=port,
                open_browser=open_browser,
            )

        launch = lambda destination: run_native_capture(destination, mdbook, runtime, tool_env)
        with capture_book(paths, launch) as context:
            if action == "build":
                result = run([mdbook, "build"], cwd=runtime, env=tool_env)
                if result:
                    return result
            return export_commands(paths, output_formats, template, allow_install=allow_install,
                                   render_context=context)


def docker_mermaid_assets(command, environment):
    recipe = (SCRIPT_DIR / "docker" / "toolchain.json").read_bytes()
    version = json.loads(recipe)["mdbook_mermaid_version"]
    identity = f"docker-v{version}-" + hashlib.sha256(recipe).hexdigest()[:20]

    def install(temporary):
        asset_env = environment.copy()
        asset_env["DOCS_ASSET_HOST"] = temporary.as_posix()
        status = run([*command, "run", "--rm", "--no-deps", "--entrypoint", "mdbook-mermaid",
                      "handbook", "install", "/book-assets"], cwd=REPOSITORY, env=asset_env)
        if status:
            raise RuntimeError(f"Docker Mermaid asset extraction failed ({status})")

    return ensure_mermaid_assets(SCRIPT_DIR, identity, install)


def docker_command(action: str, paths, port: int | None, open_browser: bool, *,
                   output_formats: tuple[str, ...] = ("markdown",), template: Path | None = None,
                   allow_install: bool = True, mermaid: bool | None = None,
                   svgbob: bool | None = None) -> int:
    policy = feature_policy(paths.config_file, mermaid=mermaid, svgbob=svgbob)
    docker = shutil.which("docker")
    if not docker:
        print("Docker mode requires the docker command.", file=sys.stderr)
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
    environment["DOCS_PROJECT_HOST"] = REPOSITORY.as_posix()
    environment["DOCS_BUILDER_HOST"] = SCRIPT_DIR.as_posix()
    environment["DOCS_BOOK_BUILD_HOST"] = paths.build_dir.as_posix()
    environment["DOCS_BOOK_BUILD_PATH"] = build_path.as_posix()
    environment["DOCS_WITH_MERMAID"] = "true" if policy.mermaid else "false"
    bob = prepared_svgbob(paths, enabled=svgbob, docker_mode=True)
    if bob:
        environment["DOCS_SVGBOB_BIN"] = container_path(bob.parent, REPOSITORY, SCRIPT_DIR)
    if action == "serve":
        environment["DOCS_HOST_PORT"] = str(port)
    if hasattr(os, "getuid"):
        environment["GUIDE_UID"] = str(os.getuid())
        environment["GUIDE_GID"] = str(os.getgid())

    command = [docker, "compose", "-f", str(COMPOSE_FILE)]
    staging = {"force": True} if policy.mermaid or requires_asset_staging(paths.config_file, SCRIPT_DIR) else {}
    with staged_book(paths, docker_mode=True, **staging) as runtime:
        book_root = runtime.relative_to(REPOSITORY)
        environment["DOCS_BOOK_ROOT"] = (Path("/book") / book_root).as_posix()
        result = run([*command, "build", "handbook"], cwd=REPOSITORY, env=environment)
        if result:
            return result
        assets = docker_mermaid_assets(command, environment) if policy.mermaid else ()
        update_book_config(paths.config_file, mermaid=policy.mermaid, svgbob=policy.svgbob, assets=assets)
        environment.update(javascript_environment(paths.config_file, project_root=REPOSITORY,
                                                  builder_dir=SCRIPT_DIR, docker_mode=True, runtime=runtime))
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

        return docker_build_export(action, paths, command, environment, output_formats,
                                   template, allow_install=allow_install)


def docker_build_export(action, paths, command, environment, output_formats, template, *,
                        allow_install: bool) -> int:
    launch = lambda destination: run_docker_capture(destination, command, environment)
    with capture_book(paths, launch) as context:
        if action == "build":
            result = run([*command, "run", "--rm", "--no-deps", "handbook", "build"],
                         cwd=REPOSITORY, env=environment)
            if result:
                return result
        return export_commands(paths, output_formats, template, allow_install=allow_install,
                               render_context=context)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="explicit project root, independent of builder location")
    parser.add_argument("-b", "--book", help="select one book alias, directory, book.toml or book.*.toml path")
    parser.add_argument("--config", "--map", dest="map", type=Path,
                        help="builder configuration TOML (default: root book-builder.toml)")
    parser.add_argument("--docker", action="store_true", help="use the pinned Docker Compose mdBook image")
    parser.add_argument("--port", type=int, default=0, help="first serve port; subsequent books use available ports; 0 picks all ports")
    parser.add_argument("--no-open", action="store_true", help="do not open the served site in a browser")
    parser.add_argument("--no-install", action="store_true",
                        help="require an existing managed PDF environment; do not create/install one")
    parser.add_argument("--format", choices=EXPORT_FORMATS, action="append",
                        help="override configured export formats; repeat for multiple (build/export only)")
    parser.add_argument("--template", type=Path,
                        help="Typst template relative to the selected book's directory (build/export only)")
    parser.add_argument("action", nargs="?", choices=("build", "serve", "export"), default="build")
    args = parser.parse_args()
    if args.action == "serve" and (args.format is not None or args.template is not None):
        parser.error("--format and --template are only supported with build/export")
    if args.format is not None:
        args.format = tuple(dict.fromkeys(args.format))
    return args


def preview_ports(args, count: int) -> list[int]:
    if args.action != "serve":
        return []
    ports = [free_port(args.port)]
    while len(ports) < count:
        port = free_port(0)
        if port not in ports:
            ports.append(port)
    return ports


def process_books(args, definitions, books, ports) -> int:
    if args.action == "serve" and len(books) > 1:
        return serve_books(Path(__file__).resolve(), [book.config_file for book in definitions], ports,
                           docker=args.docker, open_browser=not args.no_open,
                           project_root=REPOSITORY, mapping=args.map)
    command = docker_command if args.docker else native_command
    result = 0
    for definition, paths in zip(definitions, books):
        print(f"Processing {paths.config_file.relative_to(REPOSITORY)}", flush=True)
        output_formats = args.format or definition.export_formats
        features = {name: getattr(definition, name) for name in ("mermaid", "svgbob")
                    if getattr(definition, name, None) is not None}
        try:
            status = command(args.action, paths, ports[0] if ports else None, not args.no_open,
                             output_formats=output_formats, template=args.template, allow_install=not args.no_install,
                             **features)
        except BookCaptureError as exc:
            print(f"book: {exc}", file=sys.stderr)
            status = 1
        result = result or status
    return result


def main() -> int:
    global REPOSITORY
    args = parse_args()
    try:
        if args.root is not None:
            REPOSITORY = resolve_project_root(args.root)
        definitions = select_books(REPOSITORY, args.book, args.map, action=args.action)
        if not definitions:
            raise ValueError("No books enabled for general serve; select one explicitly with --book")
        books = [read_book_paths(book.config_file) for book in definitions]
        validate_outputs(books)
        ports = preview_ports(args, len(books))
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f"book: {exc}", file=sys.stderr)
        return 2

    try:
        return process_books(args, definitions, books, ports)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"book: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
