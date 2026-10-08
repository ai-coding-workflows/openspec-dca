"""Capture the processed mdBook through a caller-managed renderer invocation."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory
from typing import Callable, Iterator

from book_paths import BookPaths

RENDERER_NAME = 'book-export'


class BookCaptureError(RuntimeError):
    """The mdBook pipeline could not provide a valid render context."""


def capture_output(command: list[str]) -> str:
    """Return the whole MDBOOK_OUTPUT override, selecting only our backend."""
    return json.dumps({RENDERER_NAME: {'command': shlex.join(command)}})


def _launch_capture(launch: Callable[[Path], int], destination: Path) -> None:
    try:
        status = launch(destination)
    except Exception as exc:
        raise BookCaptureError(f'Cannot launch mdBook capture: {exc}') from exc
    if status != 0:
        raise BookCaptureError(f'mdBook capture failed with exit status {status}')


def _validate_context(context_file: Path) -> None:
    if not context_file.is_file():
        raise BookCaptureError(f'mdBook capture context is missing: {context_file}')
    try:
        context = json.loads(context_file.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as exc:
        raise BookCaptureError(f'Cannot read mdBook capture context: {exc}') from exc
    if not isinstance(context, dict):
        raise BookCaptureError('mdBook capture context must be a JSON object')
    book = context.get('book')
    if not isinstance(book, dict) or not isinstance(book.get('items'), list):
        raise BookCaptureError('mdBook capture context must contain a book.items list')


@contextmanager
def capture_book(paths: BookPaths, launch: Callable[[Path], int]) -> Iterator[Path]:
    """Keep processed content alive until all exports finish; never use sources.

    The caller owns native/Docker orchestration and must invoke mdBook with the
    supplied destination and the capture backend as its only output renderer.
    Capture lives outside the configured HTML destination, which mdBook clears.
    """
    parent = (paths.output_root if paths.output_root != paths.build_dir
              else paths.build_dir.parent)
    try:
        parent.mkdir(parents=True, exist_ok=True)
        temporary = TemporaryDirectory(prefix='mdbook-capture-', dir=parent)
    except OSError as exc:
        raise BookCaptureError(f'Cannot start mdBook capture: {exc}') from exc
    with temporary as root:
        destination = Path(root) / 'output'
        _launch_capture(launch, destination)
        context_file = destination / 'render-context.json'
        _validate_context(context_file)
        yield context_file
