"""Optional, project-local svgbob executable built in a disposable Rust container."""
from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

from book_paths import tomllib

REVISION = "1d2b053859c509af3dcb5b2dae83eb5ccf214176"
RUST_IMAGE = "rust:1.94-bookworm"
DOCKERFILE = Path(__file__).parent / "docker" / "svgbob.Dockerfile"


def host_target() -> tuple[str, str]:
    machine = platform.machine().lower()
    arch = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine)
    if sys.platform.startswith("linux") and arch:
        return ("x86_64" if arch == "amd64" else "aarch64") + "-unknown-linux-musl", f"linux/{arch}"
    if sys.platform == "win32" and arch == "amd64":
        return "x86_64-pc-windows-gnu", "linux/amd64"
    raise RuntimeError(
        "Docker svgbob builds support Linux x86-64/ARM64 and Windows x86-64. "
        "For native macOS, install mdbook-svgbob with Cargo on PATH, "
        "or use docs --docker to render inside Linux."
    )


def destination(cache: Path, target: str) -> Path:
    name = "mdbook-svgbob.exe" if "windows" in target else "mdbook-svgbob"
    recipe = hashlib.sha256(DOCKERFILE.read_bytes() + RUST_IMAGE.encode()).hexdigest()[:12]
    return cache / "mdbook-svgbob" / target / f"{REVISION}-{recipe}" / name


def valid_binary(binary: Path) -> bool:
    marker = Path(f"{binary}.sha256")
    if not binary.is_file() or not marker.is_file():
        return False
    if marker.read_text().strip() != hashlib.sha256(binary.read_bytes()).hexdigest():
        return False
    return os.name == "nt" or os.access(binary, os.X_OK)


def install(cache: Path, target: str, docker_platform: str) -> Path:
    binary = destination(cache, target)
    if valid_binary(binary):
        return binary
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("Enabling svgbob requires Docker or mdbook-svgbob on PATH.")
    name = "openspec-svgbob-" + uuid.uuid4().hex
    # No host bind mount: docker cp keeps the resulting executable host-owned.
    binary.parent.mkdir(parents=True, exist_ok=True)
    print(f"Building svgbob for {target} in Docker (first build can take several minutes)", file=sys.stderr)
    def call(*args: str, check: bool = True):
        return subprocess.run([docker, *args], check=check, stdout=sys.stderr)
    try:
        call("build", "--no-cache", "--platform", docker_platform, "--tag", name,
             "--build-arg", f"RUST_IMAGE={RUST_IMAGE}", "--file", str(DOCKERFILE), str(DOCKERFILE.parent))
        call("create", "--platform", docker_platform, "--name", name,
             "--env", f"SVGBOB_TARGET={target}",
             "--env", f"SVGBOB_REVISION={REVISION}", name)
        call("start", "--attach", name)
        # docker start --attach need not propagate the container's exit status.
        status = subprocess.run([docker, "inspect", "--format", "{{.State.ExitCode}}", name],
                                check=True, capture_output=True, text=True)
        if status.stdout.strip() != "0":
            raise RuntimeError("svgbob Rust compilation failed; see container output above")
        with tempfile.TemporaryDirectory(dir=binary.parent) as temporary:
            staged = Path(temporary) / binary.name
            call("cp", f"{name}:/output/{binary.name}", str(staged))
            if os.name != "nt":
                staged.chmod(0o755)
            digest = hashlib.sha256(staged.read_bytes()).hexdigest()
            os.replace(staged, binary)
            Path(f"{binary}.sha256").write_text(digest + "\n")
        return binary
    finally:
        # Only remove this invocation's resources, never shared images or caches.
        call("rm", "--force", "--volumes", name, check=False)
        call("image", "rm", "--force", name, check=False)


def prepare(book: Path, cache: Path, *, docker_mode: bool = False) -> Path | None:
    if tomllib is None:
        raise RuntimeError("Reading book.toml requires Python 3.11+ or tomli")
    config = tomllib.loads(book.read_text(encoding="utf-8"))
    options = config.get("preprocessor", {}).get("svgbob")
    if options is None:
        return None
    if options.get("command", "mdbook-svgbob") != "mdbook-svgbob":
        return None  # A custom command is managed by the book's author.
    if not docker_mode:
        existing = shutil.which("mdbook-svgbob")
        if existing:
            return Path(existing)
        target, docker_platform = host_target()
    else:
        arch = platform.machine().lower()
        if arch not in {"x86_64", "amd64", "arm64", "aarch64"}:
            raise RuntimeError(f"Unsupported Docker svgbob architecture: {arch}")
        arm = arch in {"arm64", "aarch64"}
        target = ("aarch64" if arm else "x86_64") + "-unknown-linux-musl"
        docker_platform = "linux/arm64" if arm else "linux/amd64"
    return install(cache, target, docker_platform)
