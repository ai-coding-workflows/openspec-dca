"""Supervise one runner per book so native and Docker previews stay independent."""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser


def _signal_server(process) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGINT)
        except ProcessLookupError:
            pass  # The child may exit between poll() and signalling.
    else:  # Stop descendants too, including the mdBook process.
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       check=False, capture_output=True)


def _wait_for_shutdown(process) -> None:
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.wait()


def stop_servers(processes) -> None:
    for process in processes:
        _signal_server(process)
    for process in processes:
        _wait_for_shutdown(process)


def _child_exit_code(processes) -> int | None:
    for process in processes:
        if process.poll() is not None:
            return process.returncode or 1
    return None


def _wait_for_readiness(processes, config: Path, url: str) -> int | None:
    # Child startup includes tool downloads or a cold Docker image build.
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        exit_code = _child_exit_code(processes)
        if exit_code is not None:
            return exit_code
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return None
        except OSError:
            time.sleep(0.25)
    print(f"Documentation server did not become ready: {config.name} ({url})",
          file=sys.stderr)
    return 1


def _open_browser(url: str) -> None:
    try:
        if not webbrowser.open(url, new=2):
            print(f"Open this URL in your browser: {url}", file=sys.stderr)
    except webbrowser.Error as exc:
        print(f"Could not open browser ({exc}); open {url}", file=sys.stderr)


def _monitor_servers(processes) -> int:
    while True:
        exit_code = _child_exit_code(processes)
        if exit_code is not None:
            return exit_code
        time.sleep(0.25)


def serve_books(script: Path, configs: list[Path], ports: list[int], *,
                docker: bool, open_browser: bool,
                project_root: Path | None = None, mapping: Path | None = None) -> int:
    processes = []
    try:
        for config, port in zip(configs, ports):
            command = [sys.executable, str(script), "--book", str(config),
                       "--port", str(port), "--no-open", "serve"]
            if project_root is not None:
                command[2:2] = ['--root', str(project_root.resolve())]
            if mapping is not None:
                base = project_root if project_root is not None else Path.cwd()
                command[2:2] = ['--config', str((base / mapping).resolve())]
            if docker:
                command.insert(2, "--docker")
            process = subprocess.Popen(command, start_new_session=(os.name == "posix"))
            processes.append(process)
            url = f"http://127.0.0.1:{port}/"
            exit_code = _wait_for_readiness(processes, config, url)
            if exit_code is not None:
                return exit_code
            print(f"{config.name}: {url}", flush=True)
            if open_browser:
                _open_browser(url)
        return _monitor_servers(processes)
    except KeyboardInterrupt:
        return 130
    finally:
        stop_servers(processes)
