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


def stop_servers(processes) -> None:
    for process in processes:
        if process.poll() is None:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass  # The child may exit between poll() and signalling.
            else:  # Stop descendants too, including the mdBook process.
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               check=False, capture_output=True)
    for process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()


def serve_books(script: Path, configs: list[Path], ports: list[int], *,
                docker: bool, open_browser: bool) -> int:
    processes = []
    try:
        for config, port in zip(configs, ports):
            command = [sys.executable, str(script), "--book", str(config),
                       "--port", str(port), "--no-open", "serve"]
            if docker:
                command.insert(2, "--docker")
            process = subprocess.Popen(command, start_new_session=(os.name == "posix"))
            processes.append(process)
            url = f"http://127.0.0.1:{port}/"
            # Child startup includes tool downloads or a cold Docker image build.
            deadline = time.monotonic() + 600
            while time.monotonic() < deadline:
                for child in processes:
                    if child.poll() is not None:
                        return child.returncode or 1
                try:
                    with urllib.request.urlopen(url, timeout=1) as response:
                        if response.status < 500:
                            break
                except OSError:
                    time.sleep(0.25)
            else:
                print(f"Documentation server did not become ready: {config.name} ({url})",
                      file=sys.stderr)
                return 1
            print(f"{config.name}: {url}", flush=True)
            if open_browser:
                try:
                    if not webbrowser.open(url, new=2):
                        print(f"Open this URL in your browser: {url}", file=sys.stderr)
                except webbrowser.Error as exc:
                    print(f"Could not open browser ({exc}); open {url}", file=sys.stderr)
        while True:
            for process in processes:
                if process.poll() is not None:
                    return process.returncode or 1
            time.sleep(0.25)
    except KeyboardInterrupt:
        return 130
    finally:
        stop_servers(processes)
