"""Standalone, standard-library project-root discovery for optional helpers."""
from pathlib import Path


def resolve_project_root(explicit=None, *, helper_file=None, cwd=None) -> Path:
    """Resolve explicit roots, installed OpenSpec roots, then local book markers.

    Installed helpers take precedence over CWD discovery. Canonical source helpers
    fall back to their nearest book-marked ancestor only after searching CWD.
    """
    current = Path.cwd() if cwd is None else Path(cwd).resolve()
    if explicit is not None:
        root = Path(explicit)
        root = (current / root).resolve()
        if not root.is_dir():
            raise ValueError(f"Missing project directory: {root}")
        return root

    helper = None if helper_file is None else Path(helper_file).absolute()
    ancestors = () if helper is None else helper.parents
    for ancestor in ancestors:
        if ancestor.name != "openspec":
            continue
        branch = helper.relative_to(ancestor).parts[0]
        if branch in {"schemas", "ddd"} or (ancestor / "config.yaml").is_file():
            return ancestor.parent  # A schema named 'openspec' is not the project boundary.

    for ancestor in (current, *current.parents):
        if ((ancestor / "openspec").is_dir()
                or any((ancestor / name).is_file() for name in ("book-builder.toml", "book.toml"))):
            return ancestor
    for ancestor in ancestors:
        if any((ancestor / name).is_file() for name in ("book-builder.toml", "book.toml")):
            return ancestor
    return current
