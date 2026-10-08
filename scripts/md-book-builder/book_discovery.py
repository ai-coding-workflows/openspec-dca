"""Discover root-level documentation configurations without recursing."""

from pathlib import Path

from book_selection import select_books


def discover_books(repository: Path, selection: str | None = None,
                   mapping: Path | None = None) -> list[Path]:
    return [book.config_file for book in select_books(repository, selection, mapping)]


def validate_outputs(paths) -> None:
    """Prevent one build or export from replacing another book's generated files."""
    for index, current in enumerate(paths):
        for previous in paths[:index]:
            if (current.build_dir.is_relative_to(previous.build_dir)
                    or previous.build_dir.is_relative_to(current.build_dir)):
                raise ValueError(
                    f"Conflicting output directories for {previous.config_file.name} and "
                    f"{current.config_file.name}; configure non-overlapping "
                    "[build].build-dir paths (for example build/book and build/user)"
                )
