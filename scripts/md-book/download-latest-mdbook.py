#!/usr/bin/env python3
"""Fetch the latest stable mdBook toolchain into a project-local cache."""
from __future__ import annotations

import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

MAX_ASSET_SIZE = 32 * 1024 * 1024


@dataclass(frozen=True)
class Tool:
    name: str
    repository: str
    asset_prefix: str


TOOLS = (
    Tool("mdbook", "rust-lang/mdBook", "mdbook"),
    Tool("mdbook-mermaid", "badboy/mdbook-mermaid", "mdbook-mermaid"),
)


def target_asset() -> tuple[str, str]:
    machine = platform.machine().lower()
    if sys.platform.startswith("linux"):
        targets = {
            "x86_64": "x86_64-unknown-linux-musl",
            "amd64": "x86_64-unknown-linux-musl",
            "aarch64": "aarch64-unknown-linux-musl",
            "arm64": "aarch64-unknown-linux-musl",
        }
        target = targets.get(machine)
        if target:
            return target, "tar.gz"
    elif sys.platform == "darwin":
        targets = {
            "x86_64": "x86_64-apple-darwin",
            "amd64": "x86_64-apple-darwin",
            "aarch64": "aarch64-apple-darwin",
            "arm64": "aarch64-apple-darwin",
        }
        target = targets.get(machine)
        if target:
            return target, "tar.gz"
    elif sys.platform == "win32" and machine in {"x86_64", "amd64"}:
        return "x86_64-pc-windows-msvc", "zip"

    raise RuntimeError(
        f"unsupported platform/architecture: {platform.system()} {machine}; "
        "see the official mdBook and mdbook-mermaid release assets"
    )


def request_bytes(url: str, *, accept: str = "application/octet-stream") -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "OpenSpec-DDD-native-docs",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read(MAX_ASSET_SIZE + 1)
    if len(payload) > MAX_ASSET_SIZE:
        raise RuntimeError("GitHub response exceeded the 32 MiB safety limit")
    return payload


def latest_release(tool: Tool) -> dict:
    api_url = f"https://api.github.com/repos/{tool.repository}/releases/latest"
    payload = request_bytes(api_url, accept="application/vnd.github+json")
    release = json.loads(payload)
    if release.get("draft") or release.get("prerelease"):
        raise RuntimeError(
            f"GitHub latest endpoint returned a draft or prerelease for {tool.name}"
        )
    return release


def cached_binary_is_valid(binary: Path, digest: str, tag: str) -> bool:
    marker = Path(f"{binary}.sha256")
    if not binary.is_file() or not marker.is_file():
        return False
    if marker.read_text(encoding="ascii").strip() != digest:
        return False
    if os.name != "nt" and not os.access(binary, os.X_OK):
        return False
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return tag.removeprefix("v") in (result.stdout + result.stderr)


def extract_binary(archive: bytes, archive_type: str, binary_name: str) -> bytes:
    if archive_type == "zip":
        with zipfile.ZipFile(io.BytesIO(archive)) as package:
            member = next(
                (
                    item
                    for item in package.infolist()
                    if Path(item.filename).name == binary_name and not item.is_dir()
                ),
                None,
            )
            if member is None:
                raise RuntimeError(f"release archive does not contain {binary_name}")
            return package.read(member)

    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        member = next(
            (
                item
                for item in package.getmembers()
                if Path(item.name).name == binary_name and item.isfile()
            ),
            None,
        )
        if member is None:
            raise RuntimeError(f"release archive does not contain a regular {binary_name}")
        stream = package.extractfile(member)
        if stream is None:
            raise RuntimeError(f"cannot read {binary_name} from release archive")
        return stream.read()


def install_tool(cache_root: Path, tool: Tool, target: str, archive_type: str) -> Path:
    binary_name = f"{tool.name}.exe" if archive_type == "zip" else tool.name
    extension = "zip" if archive_type == "zip" else "tar.gz"
    release = latest_release(tool)
    tag = release.get("tag_name")
    if not isinstance(tag, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", tag):
        raise RuntimeError(f"unexpected {tool.name} release tag: {tag!r}")

    asset_name = f"{tool.asset_prefix}-{tag}-{target}.{extension}"
    asset = next(
        (
            item
            for item in release.get("assets", [])
            if item.get("name") == asset_name
        ),
        None,
    )
    if asset is None:
        raise RuntimeError(f"latest {tool.name} release {tag} has no asset for {target}")

    digest = asset.get("digest")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
        raise RuntimeError(f"GitHub supplied no SHA-256 digest for {asset_name}")
    expected_digest = digest.removeprefix("sha256:").lower()

    url = asset.get("browser_download_url", "")
    parsed_url = urllib.parse.urlparse(url)
    expected_path = f"/{tool.repository}/releases/download/"
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "github.com"
        or not parsed_url.path.startswith(expected_path)
    ):
        raise RuntimeError(f"unexpected release asset URL: {url!r}")

    size = asset.get("size")
    if not isinstance(size, int) or size <= 0 or size > MAX_ASSET_SIZE:
        raise RuntimeError(f"unexpected release asset size for {asset_name}: {size!r}")

    destination = cache_root / tool.name / target / tag / binary_name
    if cached_binary_is_valid(destination, digest, tag):
        print(f"Using cached {tool.name} {tag}: {destination}", file=sys.stderr)
        return destination

    print(f"Downloading latest {tool.name} release {tag} from GitHub", file=sys.stderr)
    archive = request_bytes(url)
    actual_digest = hashlib.sha256(archive).hexdigest()
    if actual_digest != expected_digest:
        raise RuntimeError(f"SHA-256 mismatch for {asset_name}")

    executable = extract_binary(archive, archive_type, binary_name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent, prefix=f".{binary_name}.", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        temporary.write(executable)

    try:
        if os.name != "nt":
            temporary_path.chmod(0o755)
        os.replace(temporary_path, destination)
        Path(f"{destination}.sha256").write_text(digest + "\n", encoding="ascii")
    finally:
        temporary_path.unlink(missing_ok=True)

    if not cached_binary_is_valid(destination, digest, tag):
        raise RuntimeError(f"downloaded {tool.name} binary failed its version check: {destination}")
    return destination


def install(cache_root: Path) -> dict[str, Path]:
    target, archive_type = target_asset()
    return {
        tool.name: install_tool(cache_root, tool, target, archive_type)
        for tool in TOOLS
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} CACHE_DIRECTORY", file=sys.stderr)
        return 2
    try:
        installed = install(Path(sys.argv[1]).expanduser().resolve())
        print(json.dumps({name: str(path) for name, path in installed.items()}))
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        urllib.error.URLError,
        tarfile.TarError,
        zipfile.BadZipFile,
        RuntimeError,
    ) as error:
        print(f"mdBook toolchain download: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
