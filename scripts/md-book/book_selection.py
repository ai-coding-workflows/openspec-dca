"""Select repository-local mdBook configurations by alias or path."""

from pathlib import Path

from book_paths import tomllib


def select_book(repository: Path, selection: str | None = None,
                mapping: Path | None = None) -> Path:
    repository = repository.resolve()
    if selection is None:
        return repository / "book.toml"

    explicit_mapping = mapping is not None
    mapping = mapping or repository / "docs-books.toml"
    if not mapping.is_absolute():
        mapping = repository / mapping
    if explicit_mapping and not mapping.is_file():
        raise ValueError(f"Book mapping not found: {mapping}")
    if mapping.exists():
        if tomllib is None:
            raise RuntimeError("Reading book mappings requires Python 3.11+ or tomli")
        config = tomllib.loads(mapping.read_text(encoding="utf-8"))
        books = config.get("books", {})
        if not isinstance(books, dict):
            raise ValueError(f"[books] in {mapping} must be a table")
        if selection in books:
            target = books[selection]
            if not isinstance(target, str) or not target.strip():
                raise ValueError(f"Book alias {selection!r} must map to a non-empty path")
            selection = target
            base = mapping.parent
        else:
            base = repository
    else:
        base = repository

    target = (base / selection).resolve()
    if target.is_dir():
        target /= "book.toml"
    if not target.is_file():
        raise ValueError(f"Unknown book or missing configuration: {selection!r} ({target})")
    if target.name != "book.toml":
        raise ValueError("mdBook requires a config named book.toml; use a separate directory for each book")
    if not target.is_relative_to(repository):
        raise ValueError("Book configurations must be inside the repository")
    return target
