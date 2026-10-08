"""Surgical, durable additions to native mdBook configuration (no reformatting)."""
import copy
import json
import os
import re
import tempfile
from pathlib import Path

from book_features import managed_feature
from book_paths import tomllib

# Mask strings/comments before finding structural syntax. Triple strings are
# understood by the scanner even though only simple string arrays are edited.
_LEX = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\[\s\S]|[^"\\])*"|\'[^\']*\'|#[^\r\n]*')
_HEADER = re.compile(r'^[ \t]*\[([A-Za-z0-9_.-]+)\][ \t]*\r?$', re.M)


def _mask(text: str) -> str:
    return _LEX.sub(lambda match: re.sub(r'[^\r\n]', ' ', match.group()), text)


def _tables(text: str) -> dict[str, tuple[int, int]]:
    matches = list(_HEADER.finditer(_mask(text)))
    return {match.group(1): (match.end(), matches[index + 1].start()
                            if index + 1 < len(matches) else len(text))
            for index, match in enumerate(matches)}


def _require_explicit(config: dict, tables: dict, name: str) -> None:
    value = config
    for part in name.split('.'):
        if not isinstance(value, dict) or part not in value:
            return
        value = value[part]
    if name not in tables:
        raise ValueError(f'Cannot safely update {name}: use an explicit [{name}] table, not inline/dotted syntax')


def _relative(config_file: Path, assets: tuple[Path, ...]) -> list[str]:
    try:
        return [Path(os.path.relpath(path.resolve(), config_file.parent.resolve())).as_posix()
                for path in assets]
    except ValueError as error:
        raise ValueError('Mermaid scripts must be on the same drive as book.toml') from error


def _script_role(reference: str) -> str:
    name = Path(reference).name
    return {'mermaid.js': 'mermaid.min.js', 'mermaid.init.js': 'mermaid-init.js'}.get(name, name)


def _owned(reference: str, config_file: Path, references=()) -> bool:
    path = Path(reference)
    # Migrate the earlier unversioned builder cache, not unrelated author files.
    if _script_role(reference) in ('mermaid.min.js', 'mermaid-init.js') and references:
        parent = (config_file.parent / path).resolve().parent
        desired = (config_file.parent / references[0]).resolve()
        cache = desired.parents[2] if len(desired.parents) > 2 else None
        if parent == cache and parent.name == 'scripts' and parent.parent.name == '.cache':
            return True
    parts = path.parts
    for index in range(len(parts) - 4):
        if parts[index:index + 3] == ('.cache', 'scripts', 'mermaid'):
            if _script_role(reference) in ('mermaid.min.js', 'mermaid-init.js'):
                return True
    return _script_role(reference) in ('mermaid.min.js', 'mermaid-init.js') and not (config_file.parent / path).is_file()


def _script_plan(existing: list[str], references: list[str], config_file: Path) -> list[str]:
    """Retain valid author scripts; replace stale cache and broken standard refs."""
    desired = []
    by_name = {_script_role(ref): ref for ref in references}
    seen = set()
    # A valid author standard script satisfies that asset regardless of order.
    author_names = {_script_role(ref) for ref in existing
                    if not _owned(ref, config_file, references) and (config_file.parent / ref).is_file()}
    for ref in existing:
        name = _script_role(ref)
        if _owned(ref, config_file, references) and name in by_name:
            if name in seen or name in author_names:
                continue
            ref = by_name[name]
        desired.append(ref)
        seen.add(name)
    for ref in references:
        if _script_role(ref) not in seen:
            desired.append(ref)
            seen.add(_script_role(ref))
    return desired


def _array_span(text: str, start: int, end: int) -> tuple[int, int]:
    masked = _mask(text)
    assignment = re.search(r'^[ \t]*additional-js[ \t]*=[ \t]*\[', masked[start:end], re.M)
    if assignment is None:
        raise ValueError('Cannot safely edit additional-js: use a simple string array in [output.html]')
    left = start + assignment.end() - 1
    right = masked.find(']', left, end)
    if right < 0 or '[' in masked[left + 1:right]:
        raise ValueError('Unsupported additional-js array structure')
    return left, right


def _array_edit(text: str, span: tuple[int, int], old: list[str], new: list[str]) -> str:
    """Replace/remove only string tokens and commas; keep every author comment."""
    left, right = span
    inside = text[left + 1:right]
    tokens = [match for match in _LEX.finditer(inside) if not match.group().startswith('#')]
    values = [tomllib.loads('value = ' + match.group())['value'] for match in tokens]
    if values != old:
        raise ValueError('Unsupported additional-js string array syntax')
    remaining = list(new)
    edits = []
    for match, value in zip(tokens, old):
        if value in remaining:
            remaining.remove(value)
            continue
        # Replacements go in the original position; retain script order.
        replacement = next((ref for ref in remaining if Path(ref).name == Path(value).name), None)
        if replacement is not None:
            remaining.remove(replacement)
            edits.append((match.start(), match.end(), json.dumps(replacement)))
        else:
            edits.append((match.start(), match.end(), ''))
    for start, end, value in reversed(edits):
        inside = inside[:start] + value + inside[end:]
    # Remove commas whose preceding value was removed, keeping comment bytes.
    inside = _clean_commas(inside)
    if remaining:
        masked = _mask(inside).rstrip()
        has_values = any(not m.group().startswith('#') for m in _LEX.finditer(inside))
        separator = ',' if has_values and not masked.endswith(',') else ''
        newline = '\r\n' if '\r\n' in text else '\n'
        # A new line avoids appending into a trailing author comment.
        inside += separator + newline + '  ' + ', '.join(json.dumps(ref) for ref in remaining) + newline
    return text[:left + 1] + inside + text[right:]


def _clean_commas(inside: str) -> str:
    # Tokens provide positions while comments remain untouched. A comma with no
    # string since the previous comma is redundant after a managed deletion.
    events = sorted([(m.start(), m.end(), 'string') for m in _LEX.finditer(inside)
                     if not m.group().startswith('#')] +
                    [(m.start(), m.end(), 'comma') for m in re.finditer(',', _mask(inside))])
    have_value = False
    removals = []
    for start, end, kind in events:
        if kind == 'string':
            have_value = True
        elif have_value:
            have_value = False
        else:
            removals.append((start, end))
    for start, end in reversed(removals):
        inside = inside[:start] + inside[end:]
    return inside


def _add_scripts(text: str, config: dict, expected: dict, references: list[str],
                 config_file: Path, newline: str) -> str:
    tables = _tables(text)
    output = config.get('output', {})
    if not isinstance(output, dict):
        raise ValueError('[output] must be a table')
    html = output.get('html', {})
    if not isinstance(html, dict):
        raise ValueError('[output.html] must be a table')
    old = html.get('additional-js', [])
    if not isinstance(old, list) or any(not isinstance(ref, str) for ref in old):
        raise ValueError('additional-js must be a string array')
    new = _script_plan(old, references, config_file)
    if new == old:
        return text
    _require_explicit(config, tables, 'output.html')
    expected.setdefault('output', {}).setdefault('html', {})['additional-js'] = new
    if 'additional-js' in html:
        return _array_edit(text, _array_span(text, *tables['output.html']), old, new)
    line = 'additional-js = [' + ', '.join(json.dumps(ref) for ref in new) + ']' + newline
    if 'output.html' in tables:
        position = tables['output.html'][0]
        return text[:position] + newline + line + text[position:]
    return text + newline + '[output.html]' + newline + line


def _atomic_replace(config_file: Path, original: bytes, result: bytes) -> None:
    """Write next to the config, then detect concurrent edits before replacing."""
    descriptor, temporary = tempfile.mkstemp(prefix='.' + config_file.name + '.', dir=config_file.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, config_file.stat().st_mode)
        if config_file.read_bytes() != original:
            raise RuntimeError(f'{config_file} changed concurrently; configuration was not replaced')
        os.replace(temporary, config_file)
        if os.name != 'nt':
            directory = os.open(config_file.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update_book_config(config_file: Path, *, mermaid: bool = False,
                       svgbob: bool = False, assets: tuple[Path, ...] = ()) -> bool:
    """Add managed native setup permanently; never delete/override author setup.

    Unsupported affected inline/dotted structures fail before any config write.
    The returned boolean says whether maintained bytes changed.
    """
    if tomllib is None:
        raise RuntimeError('Reading book.toml requires Python 3.11+ or tomli')
    original = config_file.read_bytes()
    text = original.decode('utf-8')
    config = tomllib.loads(text)
    expected = copy.deepcopy(config)
    newline = '\r\n' if '\r\n' in text else '\n'
    active = {name: managed_feature(config, name, flag)
              for name, flag in (('mermaid', mermaid), ('svgbob', svgbob))}
    tables = _tables(text)
    for name, enabled in active.items():
        if enabled:
            _require_explicit(config, tables, 'preprocessor.' + name)
            if name not in config.get('preprocessor', {}):
                expected.setdefault('preprocessor', {})[name] = {}
                text += newline + f'[preprocessor.{name}]' + newline
    if active['mermaid'] and assets:
        text = _add_scripts(text, config, expected, _relative(config_file, assets), config_file, newline)
    if tomllib.loads(text) != expected:
        raise ValueError('Configuration update would alter unrelated TOML semantics')
    result = text.encode('utf-8')
    if result == original:
        return False
    _atomic_replace(config_file, original, result)
    return True
