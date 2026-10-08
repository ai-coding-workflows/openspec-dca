#!/usr/bin/env python3
"""Optional, read-only catalog and individual ADR structural checks (Python 3.10+)."""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def _sibling(name):
    """Load installed helpers without creating bytecode or importing a foreign model."""
    key = f"_ddd_{name}"
    spec = importlib.util.spec_from_file_location(key, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(key)
    bytecode = sys.dont_write_bytecode
    try:
        sys.modules[key] = module
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = bytecode
        if previous is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = previous
    return module


_catalog = _sibling('ddd')
Catalog = _catalog.Catalog
resolve_project_root = _catalog.resolve_project_root
model = _sibling('model')

NOTE = ("Structural check only; this does not establish decision authority, approval, "
        "architecture correctness, code conformance, or delivery acceptance.")


def _supersession_references(root, path, targets):
    references = []
    for target in targets:
        parsed = urlsplit(target)
        if (parsed.scheme and parsed.scheme.lower() != 'file') or parsed.netloc:
            continue  # External references are outside this local structural check.
        if not parsed.path and not parsed.scheme:
            continue
        local = unquote(parsed.path)
        if parsed.scheme or Path(local).is_absolute():
            raise ValueError(f'Supersession links must be relative local-file paths: {target} in {path}')
        destination = model.contained(root, path.parent / local)
        if not destination.is_file():
            raise ValueError(f'Missing supersession file: {target} in {path.relative_to(root)}')
        value = destination.relative_to(root).as_posix()
        if value not in references:
            references.append(value)
    return references


def _validated_record(root, record, statuses):
    path = model.project_path(root, record.path)
    if not path.is_file():
        raise ValueError(f'Individual ADR must be a file: {record.path}')
    if (not record.id or not record.id.startswith('ADR-') or not record.title
            or not record.title.strip() or not any(char.isalnum() for char in record.id[4:])):
        raise ValueError(f"Individual ADR needs a nonempty '# ADR-id: title': {record.path}")
    result = {'path': path.relative_to(root).as_posix(), 'id': record.id, 'title': record.title}
    for field in ('Status', 'Date', 'Scope'):
        values = record.field_values(field.lower())
        if len(values) != 1 or not values[0].strip():
            raise ValueError(f"ADR needs one nonempty {field}: field: {record.path}")
        result[field.lower()] = values[0].strip()
    if statuses and result['status'] not in statuses:
        raise ValueError(f"ADR Status {result['status']!r} is not in configured statuses: {record.path}")
    result['references'] = _supersession_references(root, path, record.supersession_targets)
    return result


def _statuses(values):
    if isinstance(values, str):
        raise ValueError('statuses must be a sequence, not a single string')
    values = tuple(values)
    if any(not isinstance(status, str) or not status.strip() for status in values):
        raise ValueError('Configured statuses must be nonempty strings')
    return values


def validate_decisions(root, records, *, statuses=()):
    """Validate a parsed snapshot without rediscovering/reparsing ADRs or a catalog.

    Return the CLI-compatible metadata dictionaries, not rendering text. Generic
    policy retains scoped IDs and prose dates/scopes; projects add stricter rules.
    Local supersession targets must still exist in the supplied project root.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f'Missing project directory: {root}')
    statuses = _statuses(statuses)
    result, identities = [], {}
    for data in sorted(records, key=lambda record: record.path):
        record = _validated_record(root, data, statuses)
        identity = ((root / record['path']).parent, record['scope'], record['id'])
        if identity in identities:
            raise ValueError(f"Duplicate ADR id {record['id']} in directory/scope: "
                             f"{identities[identity]} and {record['path']}")
        identities[identity] = record['path']
        result.append(record)
    return result


def _catalog_input(root, catalog):
    detected = root / 'openspec/catalog.json'
    if catalog is None and (detected.exists() or detected.is_symlink()):
        catalog = 'openspec/catalog.json'
    if catalog is None:
        return {'status': 'skipped', 'reason': 'No catalog configured or discovered.'}, []
    inventory = Catalog(root, os.fspath(catalog))
    references = [name for entry in inventory.entries.values() for name in entry.get('decisions', [])]
    return {'status': 'checked', 'path': os.fspath(catalog), **inventory.check()}, references


def check_project(root, *, catalog=None, decision_paths=(), statuses=()):
    """Preserve the optional CLI report; share ADR data parsing with renderers.

    Catalog references are additional selections. Explicit decision paths replace
    default maintained-directory discovery. No model read requires a catalog, date
    format, global ID uniqueness, status vocabulary, or catalog-owned scope.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f'Missing project directory: {root}')
    if isinstance(decision_paths, (str, os.PathLike)) or isinstance(statuses, str):
        raise ValueError('decision_paths and statuses must be sequences, not a single string/path')
    statuses = _statuses(statuses)
    catalog_result, references = _catalog_input(root, catalog)
    data = model.decisions(root, decision_paths=tuple(decision_paths), references=references)
    records = validate_decisions(root, data, statuses=statuses)
    decision_result = {'status': 'checked' if records else 'skipped', 'count': len(records), 'records': records}
    if not records:
        decision_result['reason'] = 'No individual ADR records selected or discovered.'
    return {'status': 'ok', 'catalog': catalog_result, 'decisions': decision_result, 'note': NOTE}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=None, help='Project root (default: discover from helper or current directory)')
    parser.add_argument('--catalog', help='Required project-relative catalog path (default: auto-detect)')
    parser.add_argument('--decisions', action='append', default=[], help='ADR file/directory; repeat to select more')
    parser.add_argument('--status', action='append', default=[], help='Allowed project status; repeat (default: any)')
    args = parser.parse_args(argv)
    try:
        report = check_project(resolve_project_root(args.root, helper_file=__file__), catalog=args.catalog,
                               decision_paths=args.decisions, statuses=args.status)
    except (OSError, ValueError, RecursionError) as error:
        print(json.dumps({'status': 'error', 'error': str(error), 'note': NOTE}, indent=2))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
