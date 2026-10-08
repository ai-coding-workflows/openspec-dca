"""Select repository-local mdBook configurations and their builder metadata."""

from dataclasses import dataclass
from pathlib import Path

from book_paths import tomllib


BOOK_CONFIG_NAME = "book.toml"
BUILDER_CONFIG_NAME = "book-builder.toml"
EXPORT_FORMATS = ("markdown", "typst", "pdf")


@dataclass(frozen=True)
class BookDefinition:
    config_file: Path
    export_formats: tuple[str, ...] = ("markdown",)
    serve: bool = True
    mermaid: bool | None = None
    svgbob: bool | None = None


def read_book_mapping(mapping: Path) -> dict:
    if tomllib is None:
        raise RuntimeError("Reading book mappings requires Python 3.11+ or tomli")
    config = tomllib.loads(mapping.read_text(encoding="utf-8"))
    books = config.get("books")
    if not isinstance(books, dict) or not books:
        raise ValueError(f"[books] in {mapping} must be a non-empty table")
    return books


def _mapping_path(repository: Path, mapping: Path | None,
                  *, legacy: bool = False) -> Path | None:
    if mapping is not None:
        target = (repository / mapping).resolve()
        if not target.is_file():
            raise ValueError(f"Book mapping not found: {target}")
        return target
    target = repository / BUILDER_CONFIG_NAME
    if target.exists():
        return target
    target = repository / "docs-books.toml"
    return target if legacy and target.exists() else None


def _config_path(repository: Path, base: Path, selection: str) -> Path:
    target = (base / selection).resolve()
    if target.is_dir():
        target = (target / BOOK_CONFIG_NAME).resolve()
    if not target.is_relative_to(repository):
        raise ValueError("Book configurations must be inside the repository")
    if not target.is_file():
        raise ValueError(f"Unknown book or missing configuration: {selection!r} ({target})")
    if target.name != BOOK_CONFIG_NAME and not (
            target.name.startswith("book.") and target.name.endswith(".toml")):
        raise ValueError("Book configuration must be named book.toml or book.*.toml; "
                         "rename alternate.toml to book.alternate.toml for runtime staging")
    return target


def _export_formats(alias: str, value: dict) -> tuple[str, ...]:
    if "export-format" in value and "export-formats" in value:
        raise ValueError(f"Book alias {alias!r} cannot set both export-format and export-formats")
    formats = value.get("export-formats", [value.get("export-format", "markdown")])
    if not isinstance(formats, list) or not formats:
        raise ValueError(f"Book alias {alias!r} export-formats must be a non-empty list")
    if any(not isinstance(item, str) or item not in EXPORT_FORMATS for item in formats):
        raise ValueError(f"Book alias {alias!r} export-formats must contain only markdown, typst, or pdf")
    return tuple(dict.fromkeys(formats))


def _definition(repository: Path, mapping: Path, alias: str, value) -> BookDefinition:
    if isinstance(value, str):
        value = {"config": value}
    if not isinstance(value, dict):
        raise ValueError(f"Book alias {alias!r} must be a table or path string")
    selection = value.get("config")
    if not isinstance(selection, str) or not selection.strip():
        raise ValueError(f"Book alias {alias!r} requires a non-empty config path")
    export_formats = _export_formats(alias, value)
    serve = value.get("serve", True)
    if not isinstance(serve, bool):
        raise ValueError(f"Book alias {alias!r} serve must be a boolean")
    for feature in ('mermaid', 'svgbob'):
        if feature in value and not isinstance(value[feature], bool):
            raise ValueError(f"Book alias {alias!r} {feature} must be a boolean")
    return BookDefinition(_config_path(repository, mapping.parent, selection), export_formats, serve,
                          value.get('mermaid'), value.get('svgbob'))


def _definitions(repository: Path, mapping: Path | None,
                 legacy_selection: str | None = None) -> dict[str, BookDefinition]:
    if mapping is None:
        return {}
    books = read_book_mapping(mapping)
    if legacy_selection is not None:
        books = {key: value for key, value in books.items() if key == legacy_selection}
    return {alias: _definition(repository, mapping, alias, value)
            for alias, value in books.items()}


def _selected_definition(repository: Path, selection: str,
                         definitions: dict[str, BookDefinition]) -> BookDefinition:
    if selection in definitions:
        return definitions[selection]
    target = _config_path(repository, repository, selection)
    return next((book for book in definitions.values() if book.config_file == target),
                BookDefinition(target))


def _discovered_definitions(repository: Path) -> list[BookDefinition]:
    candidates = [repository / BOOK_CONFIG_NAME, *sorted(repository.glob("book.*.toml"))]
    books = [BookDefinition(_config_path(repository, repository, str(path)))
             for path in candidates if path.is_file()]
    if not books:
        raise ValueError(f"No book.toml or book.*.toml found in {repository}")
    return books


def select_books(repository: Path, selection: str | None = None,
                 mapping: Path | None = None, *, action: str = "build") -> list[BookDefinition]:
    """Use the authoritative builder config, or discover root books when absent."""
    repository = repository.resolve()
    config = _mapping_path(repository, mapping, legacy=selection is not None)
    legacy = (mapping is None and config == repository / "docs-books.toml")
    definitions = _definitions(repository, config, selection if legacy else None)
    if selection is not None:
        return [_selected_definition(repository, selection, definitions)]
    books = list(definitions.values()) if config is not None else _discovered_definitions(repository)
    return [book for book in books if book.serve] if action == "serve" else books


def select_book(repository: Path, selection: str | None = None,
                mapping: Path | None = None) -> Path:
    """Keep the checker single-book default independent of builder configuration."""
    repository = repository.resolve()
    if selection is None:
        return repository / BOOK_CONFIG_NAME
    return select_books(repository, selection, mapping)[0].config_file
