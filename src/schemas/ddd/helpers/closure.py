#!/usr/bin/env python3
"""Read-only closure receipt checks; Python 3.10+, standard library only.

Checks declared states, complete change-input/delta inventories, fingerprints,
publication targets, explicit durable references and existing catalog/ADR metadata.
Does NOT merge/publish, execute tests, parse Markdown links/anchors, validate code,
prove semantic integration, or establish reviewer authority. See helpers/README.md.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path, PurePosixPath

NOTE = ("Evidence/structure check only: semantic merge, scope completeness, actual test "
        "execution, link anchors/symbols, and authorization require recorded review "
        "and project-specific checks. No files are written and no commands are run.")
REQUIRED = {
    'proposal.md', 'impact.md', 'domain-model-changes.md', 'design.md',
    'architectural-decisions.md', 'tasks.md', 'verification.md',
}


def obj(value, *, required, optional=(), where='value'):
    if not isinstance(value, dict):
        raise ValueError(f'{where} must be an object')
    missing, extra = set(required) - value.keys(), value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f'{where}: missing keys {sorted(missing)}, unknown keys {sorted(extra)}')
    return value


def text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{where} must be a nonempty string')
    return value


def array(value, where):
    if not isinstance(value, list):
        raise ValueError(f'{where} must be an array')
    return value


def local(root: Path, value: str) -> Path:
    """Require a canonical relative POSIX path, also safe on Windows."""
    text(value, 'path')
    p = PurePosixPath(value)
    if (p.is_absolute() or '\\' in value or ':' in value or '..' in p.parts
            or str(p) != value or value == '.'):
        raise ValueError(f'Expected canonical relative file path: {value!r}')
    path = root.joinpath(*p.parts)
    try:
        path.resolve().relative_to(root.resolve())
    except (ValueError, RuntimeError) as exc:
        raise ValueError(f'Path escapes root or has a symlink loop: {value}') from exc
    return path


def digest(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f'Missing regular file: {path}')
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def snapshot(root, value, where='snapshot'):
    obj(value, required=('path', 'sha256'), where=where)
    path = local(root, value['path'])
    if not isinstance(value['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', value['sha256']):
        raise ValueError(f'{where}: expected lowercase SHA-256 for {value["path"]}')
    if digest(path) != value['sha256']:
        raise ValueError(f'Stale fingerprint: {value["path"]}')
    return value['path']


def snapshots(root, values, where):
    names = set()
    for value in array(values, where):
        name = snapshot(root, value, where)
        if name in names:
            raise ValueError(f'{where}: duplicate file {name}')
        names.add(name)
    return names


def inventory(change: Path, receipt_name: str) -> set[str]:
    names = set()
    for path in sorted(change.rglob('*')):
        relative = path.relative_to(change).as_posix()
        local(change, relative)  # Reject escaping symlinks, including directories.
        if path.is_symlink() and path.is_dir():
            raise ValueError(f'Symlink directories in a change cannot be inventoried: {relative}')
        if relative == receipt_name:
            continue
        if path.is_file():
            names.add(relative)
        elif path.is_symlink():
            raise ValueError(f'Dangling symlink in change: {relative}')
    return names


def section(value, name, *, extra=()):
    obj(value, required=('status', 'reason', 'files', *extra), where=name)
    if value['status'] not in ('complete', 'not-needed'):
        raise ValueError(f'{name} is not complete: {value["status"]!r}')
    array(value['files'], name + '.files')
    if not isinstance(value['reason'], str):
        raise ValueError(f'{name}.reason must be a string')
    if value['status'] == 'not-needed':
        text(value['reason'], name + '.reason')
        if value['files']:
            raise ValueError(f'{name}: not-needed cannot contain files')
    elif not value['files'] and not value['reason'].strip():
        raise ValueError(f'{name}: empty complete scope needs an explicit reviewed reason')
    return value['status']


def durable(root, target):
    path = local(root, target)
    if PurePosixPath(target).parts[:2] == ('openspec', 'changes'):
        raise ValueError(f'Maintained targets/references cannot point into changes: {target}')
    return path


def completed_tasks(change):
    source = re.sub(r'<!--.*?-->', '', (change / 'tasks.md').read_text(encoding='utf-8'), flags=re.S)
    count, fence = 0, None
    for line in source.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r'^\s*(?:[-*+]|\d{1,9}[.)])\s+\[([ xX])\]\s+\S', line)
        if match:
            count += 1
            if match.group(1) == ' ':
                raise ValueError(f'Unchecked Apply task: {line.strip()}')
    if count == 0:
        raise ValueError('tasks.md contains no tracked Apply tasks')
    return count


def sibling(name):
    key = '_ddd_closure_' + name
    spec = importlib.util.spec_from_file_location(key, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    previous, bytecode = sys.modules.get(key), sys.dont_write_bytecode
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


def resolve_change(root, change_name):
    relative = change_name if '/' in change_name else 'openspec/changes/' + change_name
    change = local(root, relative)
    changes_root = (root / 'openspec/changes').resolve()
    try:
        change.resolve().relative_to(changes_root)
    except ValueError as exc:
        raise ValueError('Change must live below openspec/changes/') from exc
    if not change.is_dir() or change.resolve() == changes_root:
        raise ValueError(f'Missing change directory: {relative}')
    return change


def check_closure(root, change_name, receipt_name='integration.json'):
    root = Path(root).resolve()
    change = resolve_change(root, change_name)
    relative = change.relative_to(root).as_posix()
    receipt_path = local(change, receipt_name)
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    obj(receipt, required=('version', 'change', 'evidence', 'inputs', 'requirements',
                          'companions', 'reconciliation'), where='receipt')
    if type(receipt['version']) is not int or receipt['version'] != 1:
        raise ValueError('Unsupported closure receipt version')
    name = text(receipt['change'], 'change')
    archived_name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', change.name) if change.parent.name == 'archive' else change.name
    if name != archived_name:
        raise ValueError('Receipt change name does not match its directory')

    actual = inventory(change, receipt_name)
    if not REQUIRED <= actual:
        raise ValueError(f'Missing change artifacts/evidence: {sorted(REQUIRED - actual)}')
    inputs = snapshots(change, receipt['inputs'], 'inputs')
    if inputs != actual:
        raise ValueError(f'Input inventory mismatch: missing {sorted(actual-inputs)}, obsolete {sorted(inputs-actual)}')
    evidence = text(receipt['evidence'], 'evidence')
    if evidence not in inputs or not local(change, evidence).read_text(encoding='utf-8').strip():
        raise ValueError('Evidence must name a nonempty snapshotted change-local file')
    task_count = completed_tasks(change)

    requirements = receipt['requirements']
    req_status = section(requirements, 'requirements')
    deltas = {name for name in actual if name.startswith('specs/') and name.endswith('/spec.md')}
    covered, published = set(), set()
    for row in requirements['files']:
        obj(row, required=('source', 'target', 'sha256'), optional=('action',), where='requirement mapping')
        source = text(row['source'], 'requirement source')
        if source not in deltas or source in covered:
            raise ValueError(f'Unknown or duplicate requirement delta: {source}')
        expected = 'openspec/' + source
        if row['target'] != expected:
            raise ValueError(f'Delta {source} must map to {expected}')
        action = row.get('action', 'merge')
        if action == 'retire':
            path = local(root, row['target'])
            if row['sha256'] is not None or path.exists() or path.is_symlink():
                raise ValueError(f'Retired main spec still exists or has a fingerprint: {row["target"]}')
        elif action == 'merge':
            snapshot(root, {'path': row['target'], 'sha256': row['sha256']}, 'requirement target')
        else:
            raise ValueError(f'Unknown requirement integration action: {action}')
        covered.add(source)
        published.add(row['target'])
    if covered != deltas or (deltas and req_status != 'complete'):
        raise ValueError(f'Unintegrated requirement deltas: {sorted(deltas-covered)}')
    if not deltas and req_status != 'not-needed':
        raise ValueError('With no deltas, requirements must be not-needed with a reviewed reason')

    companions = receipt['companions']
    section(companions, 'companions')
    for row in companions['files']:
        obj(row, required=('action', 'source', 'target', 'sha256'), where='companion mapping')
        action = row['action']
        if action not in ('publish', 'reuse', 'remove'):
            raise ValueError(f'Unfinished or unknown companion action: {action}')
        target = row['target']
        path = durable(root, target)
        if target in published:
            raise ValueError(f'Duplicate publication target: {target}')
        published.add(target)
        if target.startswith('openspec/specs/') and path.name == 'spec.md':
            raise ValueError('Main specs must use requirement integration, not companion publication')
        if action == 'publish':
            if row['source'] not in inputs:
                raise ValueError(f'Published companion needs a snapshotted change-local source: {target}')
        elif row['source'] is not None:
            raise ValueError(f'{action} uses source: null; explain it in the mapped assessment/evidence')
        if action == 'remove':
            if row['sha256'] is not None or path.exists() or path.is_symlink():
                raise ValueError(f'Removal target still exists or has a fingerprint: {target}')
        else:
            snapshot(root, {'path': target, 'sha256': row['sha256']}, 'companion target')

    reconciliation = receipt['reconciliation']
    state = section(reconciliation, 'reconciliation', extra=('references',))
    for row in reconciliation['files']:
        if isinstance(row, dict) and 'path' in row:
            durable(root, row['path'])
    snapshots(root, reconciliation['files'], 'reconciliation.files')
    references = array(reconciliation['references'], 'reconciliation.references')
    seen = set()
    for reference in references:
        path = durable(root, reference)
        if reference in seen:
            raise ValueError(f'Duplicate durable reference: {reference}')
        seen.add(reference)
        if not path.is_file():
            raise ValueError(f'Missing durable reference: {reference}')
    if state == 'not-needed' and references:
        raise ValueError('Reconciliation not-needed cannot contain references')

    metadata = sibling('check').check_project(root)
    unlisted = set(metadata['catalog'].get('unlisted_main_specs', []))
    affected_unlisted = unlisted & {row['target'] for row in requirements['files']}
    if affected_unlisted:
        raise ValueError(f'Affected main specs missing from the enabled catalog: {sorted(affected_unlisted)}')
    return {'status': 'ok', 'change': relative, 'tasks': task_count, 'inputs': len(inputs),
            'requirement_deltas': len(deltas), 'companion_actions': len(companions['files']),
            'reviewed_files': len(reconciliation['files']), 'durable_references': len(references),
            'metadata': metadata, 'note': NOTE}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=None, help='Project root (default: installed helper discovery)')
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check', help='Check a completed closure receipt without writing or publishing')
    check.add_argument('--change', required=True, help='Active change name or project-relative archived path')
    check.add_argument('--receipt', default='integration.json', help='Change-relative receipt path')
    inputs = sub.add_parser('inputs', help='Print all change-input snapshots, excluding the receipt')
    inputs.add_argument('--change', required=True)
    inputs.add_argument('--receipt', default='integration.json')
    fingerprint = sub.add_parser('fingerprint', help='Print project-relative path/SHA-256 pairs')
    fingerprint.add_argument('paths', nargs='+')
    args = parser.parse_args(argv)
    try:
        root = sibling('project_root').resolve_project_root(args.root, helper_file=__file__)
        if args.command == 'fingerprint':
            report = [{'path': value, 'sha256': digest(local(root, value))} for value in args.paths]
        elif args.command == 'inputs':
            change = resolve_change(root, args.change)
            local(change, args.receipt)
            report = [{'path': value, 'sha256': digest(change / value)}
                      for value in sorted(inventory(change, args.receipt))]
        else:
            report = check_closure(root, args.change, args.receipt)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc), 'note': NOTE}, indent=2))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
