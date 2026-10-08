"""Provision isolated, builder-owned Python environments for optional PDF exports."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
import sysconfig
try:
    import venv
except ImportError:
    venv = None
from contextlib import contextmanager
from pathlib import Path


class PdfEnvironmentError(RuntimeError):
    """A PDF dependency environment could not safely be used or prepared."""


_OWNER = "pdf-owner.json"
_READY = "pdf-ready.json"
_PROBE = """
import sys
sys.dont_write_bytecode = True
import importlib.metadata, json, pathlib
import typst
if sys.version_info < (3, 11):
    import tomli
print(json.dumps({'version': list(sys.version_info[:2]),
                  'prefix': str(pathlib.Path(sys.prefix).resolve()),
                  'typst': importlib.metadata.version('typst')}))
"""


def _configuration(builder_dir: Path) -> tuple[Path, Path, dict, str]:
    requirements = builder_dir / "exporter" / "requirements-pdf.txt"
    content = requirements.read_bytes()
    pins = re.findall(r"^\s*typst==([\w.+-]+)\s*(?:#.*)?$", content.decode(), re.M)
    if len(pins) != 1:
        raise PdfEnvironmentError(f"PDF requirements must pin one typst version: {requirements}")
    executable = Path(sys.executable).resolve()
    stat = executable.stat()
    identity = {
        "owner": "md-book-builder-pdf-v1",
        "requirements": hashlib.sha256(content).hexdigest(),
        "interpreter": str(executable),
        "interpreter_stat": [stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns],
        "version": list(sys.version_info[:3]),
        "cache_tag": sys.implementation.cache_tag,
        "platform": [sys.platform, platform.machine(), sysconfig.get_platform()],
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:24]
    label = re.sub(r"[^a-zA-Z0-9_.-]", "-", f"{sys.implementation.cache_tag}-{sys.platform}-{platform.machine()}")
    target = builder_dir / ".venv" / f"pdf-{label}-{digest}"
    return target, requirements, identity, pins[0]


def _marker_matches(path: Path, identity: dict) -> bool:
    if path.is_symlink():
        return False
    try:
        return json.loads(path.read_text(encoding="utf-8")) == identity
    except (OSError, ValueError):
        return False


def _guard_target(target: Path, identity: dict) -> None:
    if target.parent.is_symlink():
        raise PdfEnvironmentError(f"Refusing symlinked PDF cache: {target.parent}. Use a real builder-owned directory.")
    if target.is_symlink() or (target.exists() and not _marker_matches(target / _OWNER, identity)):
        raise PdfEnvironmentError(f"Refusing unowned PDF environment: {target}. Move it aside manually before retrying.")


def _python(target: Path) -> Path:
    return target / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def _valid(target: Path, identity: dict, pin: str) -> bool:
    return _marker_matches(target / _READY, identity) and _working(target, pin)


def _working(target: Path, pin: str) -> bool:
    if not _python(target).is_file():
        return False
    try:
        result = subprocess.run(
            [str(_python(target)), "-I", "-c", _PROBE],
            check=True, capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        return data == {"version": list(sys.version_info[:2]), "prefix": str(target.resolve()), "typst": pin}
    except (OSError, subprocess.SubprocessError, ValueError):
        return False


def _check_lock(target: Path) -> None:
    lock = target.with_name(target.name + ".lock")
    if lock.exists() or lock.is_symlink():
        raise PdfEnvironmentError(
            f"PDF environment setup is already locked: {lock}. Retry after setup finishes; "
            "if setup was terminated, remove this lock manually only after confirming no setup is running."
        )


@contextmanager
def _setup_lock(target: Path):
    lock = target.with_name(target.name + ".lock")
    try:
        lock.mkdir()
    except FileExistsError:
        _check_lock(target)
        raise PdfEnvironmentError(f"PDF setup lock changed unexpectedly: {lock}. Retry setup.")
    # Only remove the directory we created, never a pre-existing/replaced lock.
    identity = lock.stat()
    try:
        yield
    finally:
        if not lock.is_symlink() and lock.exists():
            current = lock.stat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                lock.rmdir()


def _write_marker(path: Path, identity: dict) -> None:
    # Exclusive creation refuses symlinks and never overwrites an unrelated file.
    with path.open("x", encoding="utf-8") as stream:
        json.dump(identity, stream, sort_keys=True)


def _guard_contents(target: Path) -> None:
    for path in target.rglob("*"):
        if not path.is_symlink():
            continue
        resolved = path.resolve()
        if resolved.is_relative_to(target.resolve()):
            continue
        # Standard venv links to the creating interpreter are expected.
        if path.parent == target / "bin" and path.name.startswith("python") and resolved == Path(sys.executable).resolve():
            continue
        raise PdfEnvironmentError(f"Refusing external symlink in managed PDF environment: {path}. Move it aside manually.")


def _prepare(target: Path, requirements: Path, identity: dict, pin: str) -> Path:
    _guard_target(target, identity)
    if _valid(target, identity, pin):
        return _python(target)
    if not target.exists():
        target.mkdir()
        _write_marker(target / _OWNER, identity)
    ready = target / _READY
    if ready.is_symlink():
        raise PdfEnvironmentError(f"Refusing symlinked PDF completion marker: {ready}. Move it aside manually.")
    ready.unlink(missing_ok=True)
    _guard_contents(target)
    print(f"Preparing isolated PDF dependencies in {target}", file=sys.stderr, flush=True)
    if venv is None:
        raise PdfEnvironmentError("Python venv is unavailable. Install Python's venv/ensurepip support (for example python3-venv), then retry PDF export.")
    venv.EnvBuilder(with_pip=True).create(target)
    subprocess.run(
        [str(_python(target)), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)],
        check=True, timeout=600,
    )
    # Verify dependencies before publishing the completion marker.
    if not _working(target, pin):
        raise PdfEnvironmentError(f"PDF environment verification failed: {target}. Retry PDF export to repair it.")
    _write_marker(ready, identity)
    return _python(target)


def ensure_pdf_python(builder_dir: Path, *, allow_install: bool = True) -> Path:
    """Return a verified managed interpreter; never inspect/install host dependencies.

    Incomplete owned environments are repaired in place. Unknown environments and
    active (or stale) locks are never removed automatically.
    """
    try:
        target, requirements, identity, pin = _configuration(Path(builder_dir).resolve())
        _guard_target(target, identity)
        _check_lock(target)
        if _valid(target, identity, pin):
            return _python(target)
        if not allow_install:
            raise PdfEnvironmentError("No valid managed PDF environment is available. Enable PDF dependency installation and retry.")
        target.parent.mkdir(parents=True, exist_ok=True)
        with _setup_lock(target):
            return _prepare(target, requirements, identity, pin)
    except PdfEnvironmentError:
        raise
    except subprocess.TimeoutExpired as exc:
        raise PdfEnvironmentError("PDF environment setup timed out. Check network access and retry PDF export.") from exc
    except subprocess.CalledProcessError as exc:
        raise PdfEnvironmentError(
            "PDF dependency setup failed. Check the pip output/network access and that this Python has venv/ensurepip "
            "(install python3-venv if needed), then retry PDF export."
        ) from exc
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        raise PdfEnvironmentError(
            f"Cannot prepare PDF environment: {exc}. Check filesystem permissions and Python venv/ensurepip support, then retry PDF export."
        ) from exc
