"""Standalone stdlib mdBook renderer retaining the complete RenderContext."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile


def read_context() -> dict:
    """Read a renderer object, not the preprocessor's [context, book] pair."""
    context = json.load(sys.stdin)
    if not isinstance(context, dict):
        raise ValueError('RenderContext must be a JSON object')
    book = context.get('book')
    if not isinstance(book, dict) or not isinstance(book.get('items'), list):
        raise ValueError('RenderContext must contain a book.items list')
    destination = context.get('destination')
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError('RenderContext destination must be a non-empty path string')
    return context


def write_context(context: dict) -> None:
    """Atomically write to the destination supplied by mdBook."""
    destination = Path(context['destination'])
    destination.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination,
                                prefix='.render-context-', suffix='.tmp',
                                delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(context, stream, ensure_ascii=False)
            stream.write('\n')
        os.replace(temporary, destination / 'render-context.json')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    try:
        write_context(read_context())
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        print(f'mdBook capture backend: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
