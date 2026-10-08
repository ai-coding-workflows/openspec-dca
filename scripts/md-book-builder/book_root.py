"""Discover a project independently of where the reusable builder is installed."""
from pathlib import Path


MARKERS = ('book-builder.toml', 'book.toml')


def resolve_project_root(explicit=None, *, cwd=None, builder_dir=None) -> Path:
    """Prefer an explicit directory, then nearest cwd and builder ancestors.

    Explicit roots need no book marker (source-only projects are supported).
    Discovery is performed when called, never as an import-time side effect.
    """
    if explicit is not None:
        root = Path(explicit).resolve()
        if not root.is_dir():
            raise ValueError(f'Project root is not an existing directory: {root}')
        return root
    starts = (Path.cwd() if cwd is None else Path(cwd),
              Path(__file__).resolve().parent if builder_dir is None else Path(builder_dir))
    for start in starts:
        start = start.resolve()
        for candidate in (start, *start.parents):
            if any((candidate / marker).is_file() for marker in MARKERS):
                return candidate
    raise ValueError('Cannot discover project root: no book-builder.toml or book.toml '
                     'in cwd or builder ancestors; pass --root with an existing directory')
