"""Read shared handbook build paths from book.toml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    try:
        import tomli as tomllib
    except ModuleNotFoundError:  # pragma: no cover - depends on runtime
        tomllib = None


@dataclass(frozen=True)
class BookPaths:
    repository: Path
    build_dir: Path
    output_root: Path


def read_book_paths(book_toml: Path) -> BookPaths:
    """Resolve the configured mdBook output directory and its generated-file root."""
    if tomllib is None:
        raise RuntimeError(
            "Reading book.toml requires Python 3.11+ or the 'tomli' package on Python 3.10"
        )

    book_toml = book_toml.resolve()
    if not book_toml.is_file():
        raise ValueError(f"book configuration not found: {book_toml}")

    try:
        config = tomllib.loads(book_toml.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"cannot read {book_toml}: {exc}") from exc

    build = config.get("build", {})
    if not isinstance(build, dict):
        raise TypeError(f"[build] in {book_toml} must be a table")
    value = build.get("build-dir", "book")
    if not isinstance(value, str):
        raise TypeError(f"[build].build-dir in {book_toml} must be a string")
    if not value.strip():
        raise ValueError(f"[build].build-dir in {book_toml} must be a non-empty path")

    repository = book_toml.parent
    raw_build_dir = Path(value)
    build_dir = (
        raw_build_dir if raw_build_dir.is_absolute() else repository / raw_build_dir
    ).resolve()
    if build_dir == repository:
        raise ValueError("[build].build-dir must be a child path of the repository")
    if build_dir.parent == repository:
        output_root = build_dir
    else:
        output_root = build_dir.parent
    return BookPaths(repository, build_dir, output_root)
