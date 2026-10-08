#!/usr/bin/env python3
"""Check optional DDD metadata, local sources, and freshly built mdBook HTML."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

def installed_project_root():
    """Installed schemas may have any name or depth below openspec/."""
    helper = Path(__file__).absolute()
    for parent in helper.parents:
        if parent.name != 'openspec':
            continue
        branch = helper.relative_to(parent).parts[0]
        if branch in {'schemas', 'ddd'} or (parent / 'config.yaml').is_file():
            return parent.parent
    return None


def default_builder():
    # Keep the conventional location as a convenience, not an installation rule.
    roots = [installed_project_root(), *Path(__file__).resolve().parents]
    for root in roots:
        if root is not None and (root / 'scripts/md-book-builder/book.py').is_file():
            return root / 'scripts/md-book-builder'
    root = installed_project_root() or Path.cwd()
    return root / 'scripts/md-book-builder'


ROOT = installed_project_root()
BUILDER = default_builder()
read_book_paths = select_books = validate_outputs = resolve_project_root = references = None


def load_builder_library(builder: Path) -> None:
    """Load the selected bundle without reusing another bundle's cached modules.

    Keep public references patchable while restoring the embedding process's
    module namespace after imports (tests may load multiple relocated bundles).
    """
    global read_book_paths, select_books, validate_outputs, resolve_project_root, references
    names = ('book_paths', 'book_selection', 'book_discovery', 'book_root',
             '_book_reference_checks')
    previous = {name: sys.modules.get(name) for name in names}
    modules = {}
    try:
        for name in names:
            filename = 'check.py' if name == '_book_reference_checks' else name + '.py'
            spec = importlib.util.spec_from_file_location(name, builder / filename)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            modules[name] = module
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
    read_book_paths = modules['book_paths'].read_book_paths
    select_books = modules['book_selection'].select_books
    validate_outputs = modules['book_discovery'].validate_outputs
    resolve_project_root = modules['book_root'].resolve_project_root
    references = modules['_book_reference_checks']


# Preserve public library references for embedding/tests, without requiring a
# sibling bundle when the CLI will explicitly select a relocated installation.
if (BUILDER / 'book_paths.py').is_file():
    load_builder_library(BUILDER)


def run_step(command: list[str], root: Path) -> int:
    return subprocess.run(command, cwd=root, check=False).returncode


def selected_books(args):
    root = args.root
    configured = (root / 'book-builder.toml').exists() or (root / 'book.toml').exists()
    if not (configured or list(root.glob('book.*.toml')) or args.book or args.config):
        return []
    definitions = select_books(root, args.book, args.config, action='build')
    books = [read_book_paths(book.config_file) for book in definitions]
    validate_outputs(books)
    return books


def metadata_present(root):
    catalog = root / 'openspec/catalog.json'
    if catalog.exists() or catalog.is_symlink():
        return True
    return any(path for name in ('openspec/specs', 'openspec/system-architecture')
               for path in (root / name).glob('**/architectural-decisions'))


def metadata_helper(args):
    explicit = getattr(args, 'ddd_helper', None)
    if explicit is not None:
        path = explicit if explicit.is_absolute() else args.root / explicit
        if not path.is_file():
            raise ValueError(f'DDD helper is not installed: {path}')
        return path.resolve()
    candidates = [Path(__file__).with_name('check.py'),
                  args.root / 'src/schemas/ddd/helpers/check.py',
                  args.root / 'openspec/ddd/check.py']
    helper = next((path for path in candidates if path.is_file()), None)
    if helper is not None:
        return helper
    installed = sorted((args.root / 'openspec/schemas').glob('*/helpers/check.py'))
    if len(installed) > 1:
        raise ValueError('Multiple schema DDD helpers installed; choose --ddd-helper explicitly')
    return installed[0] if installed else None


def metadata_command(args):
    if args.skip_ddd:
        print('DDD metadata checks explicitly skipped.', flush=True)
        return None
    helper = metadata_helper(args)
    requested = args.catalog is not None or args.decisions or args.status
    if helper is None:
        if requested or metadata_present(args.root):
            raise ValueError('DDD metadata selected/present, but the optional schema helpers/check.py is not installed; '
                             'install the composed schema or pass --ddd-helper')
        print('DDD helper absent; optional metadata checks skipped.', flush=True)
        return None
    command = [sys.executable, str(helper), '--root', str(args.root)]
    if args.catalog is not None:
        command.extend(['--catalog', args.catalog])
    for value in args.decisions:
        command.extend(['--decisions', value])
    for value in args.status:
        command.extend(['--status', value])
    return command


def native_validation(args) -> int:
    if not args.openspec:
        return 0
    binary = os.environ.get('OPENSPEC_BIN') or shutil.which('openspec')
    if not binary:
        raise ValueError('--openspec requires OpenSpec on PATH or OPENSPEC_BIN')
    return run_step([binary, 'validate', '--all', '--strict', '--no-interactive'], args.root)


def source_checks(args, books):
    sources = [references.source_directory(book) for book in books]
    sources.extend((args.root / value).resolve() for value in args.source)
    if not sources:
        print('No documentation source folders selected; source checks skipped.', flush=True)
        return
    references.validate_sources(args.root, sources, exclude_dirs=[book.build_dir for book in books])
    print('Local documentation sources verified; external URLs and code conformance were not checked.', flush=True)


def build_and_check(args, books) -> int:
    if args.source_only:
        return 0
    if not books:
        print('No books configured; documentation build and HTML checks skipped.', flush=True)
        return 0
    builder = args.builder or BUILDER / 'book.py'
    if not builder.is_file():
        raise ValueError(f'Documentation builder is not installed: {builder}')
    command = [sys.executable, str(builder), '--root', str(args.root)]
    if args.docker:
        command.append('--docker')
    if args.book:
        command.extend(['--book', args.book])
    if args.config:
        command.extend(['--config', str(args.config)])
    # Checking documentation must not provision PDF dependencies or registry packages.
    command.extend(['build', '--format', 'markdown'])
    status = run_step(command, args.root)
    if status:
        return status
    for book in books:
        references.validate_html(book.build_dir)
    print('Freshly built local HTML links and anchors verified.', flush=True)
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=['check'], default='check')
    parser.add_argument('--root', type=Path, default=ROOT,
                        help='Project root (default: nearest cwd or builder ancestor with a book marker)')
    parser.add_argument('--builder', type=Path, default=os.environ.get('BOOK_BUILDER'),
                        help='Builder book.py path (default: BOOK_BUILDER or sibling bundle)')
    parser.add_argument('-b', '--book', help='Select one book alias or native configuration')
    parser.add_argument('--config', '--map', dest='config', type=Path, help='Builder configuration')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--docker', action='store_true', help='Build using the pinned Docker toolchain')
    mode.add_argument('--native', action='store_true', help='Use native tools (the default)')
    parser.add_argument('--source-only', action='store_true', help='Do not build or check HTML')
    parser.add_argument('--source', action='append', default=[], help='Additional project-relative source directory; repeat')
    parser.add_argument('--ddd-helper', type=Path, help='Explicit DDD check.py path; relative to project root')
    parser.add_argument('--catalog', help='Explicit project-relative DDD catalog; otherwise auto-detected')
    parser.add_argument('--decisions', action='append', default=[], help='Explicit DDD ADR path; repeat')
    parser.add_argument('--status', action='append', default=[], help='Allowed DDD ADR status; repeat (default: unrestricted)')
    parser.add_argument('--skip-ddd', action='store_true', help='Explicitly skip optional DDD checks')
    parser.add_argument('--openspec', action='store_true', help='Also run native openspec validate --all --strict --no-interactive')
    args = parser.parse_args(argv)
    if args.skip_ddd and (args.ddd_helper is not None or args.catalog is not None or args.decisions or args.status):
        parser.error('--skip-ddd cannot be combined with explicit DDD metadata options')
    if args.root is not None:
        args.root = args.root.resolve()
    if args.builder is not None:
        args.builder = args.builder.resolve()
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        builder = args.builder or BUILDER / 'book.py'
        if args.builder is not None or references is None:
            if not builder.is_file():
                raise ValueError(f'Documentation builder is not installed: {builder}')
            load_builder_library(builder.parent)
        args.root = resolve_project_root(args.root, builder_dir=builder.parent)
        books = selected_books(args)
        metadata = metadata_command(args)
        if metadata:
            status = run_step(metadata, args.root)
            if status:
                return status
        source_checks(args, books)
        status = native_validation(args)
        return status or build_and_check(args, books)
    except (OSError, ValueError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'docs-check: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
