#!/usr/bin/env python3
"""Optional read-only mdBook ADR index and virtual directory chapters (Python 3.10+).

Activate with [preprocessor.adr] and a command pointing to this installed helper.
Only {{#adr-index}} activates discovery. No files or assets are generated on disk.
Local Markdown resources must already exist in book.src or be selected ADRs;
relative HTML resources and mdBook includes are deliberately unsupported.
"""
import hashlib
import html
import importlib.util
import json
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit


def _check():
    """Load the adjacent checker, including dataclasses, without bytecode writes."""
    key = '_ddd_adr_check'
    spec = importlib.util.spec_from_file_location(key, Path(__file__).with_name('check.py'))
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


check = _check()
MARKER = '{{#adr-index}}'
RENDERERS = {'html', 'book-export'}


def _chapters(items):
    for item in items:
        if isinstance(item, dict) and isinstance(item.get('Chapter'), dict):
            chapter = item['Chapter']
            yield chapter
            yield from _chapters(chapter.get('sub_items', []))


def _logical_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or value.startswith('/') or any(p in ('', '.', '..') for p in value.split('/'))):
        raise ValueError(f'Chapter path must be a safe relative source path: {value!r}')
    return PurePosixPath(value)


def _escape(value):
    # Character references avoid table delimiters, links, raw HTML, and code spans.
    value = html.escape(str(value), quote=True)
    for character in '|[]`\\*_':
        value = value.replace(character, f'&#{ord(character)};')
    return value.replace('\r', ' ').replace('\n', ' ')


def _anchor(identity):
    lowered = identity.casefold()
    if re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', lowered, flags=re.ASCII):
        return lowered
    # Do not collapse distinct punctuation/non-ASCII identities into the same slug.
    prefix = re.sub(r'[^a-z0-9]+', '-', lowered, flags=re.ASCII).strip('-') or 'adr'
    return prefix + '-' + hashlib.sha256(lowered.encode('utf-8')).hexdigest()


def _relative(source, target, fragment=None, query=''):
    path = posixpath.relpath(str(target), str(source.parent))
    result = quote(path, safe='/-._~')
    if query:
        result += '?' + query
    if fragment is not None:
        result += '#' + fragment
    return result


def _local(value):
    parsed = urlsplit(html.unescape(value))
    return not parsed.netloc and not parsed.scheme and bool(parsed.path)


def _rebase(value, source, page, root, booksrc, destinations):
    parsed = urlsplit(html.unescape(value))
    if parsed.scheme and parsed.scheme.lower() == 'file':
        raise ValueError(f'Local file URLs are unsupported in ADR {source}: {value}')
    if parsed.netloc or parsed.scheme or not parsed.path:
        return value
    local = unquote(parsed.path)
    if Path(local).is_absolute() or '\\' in local:
        raise ValueError(f'ADR links must be relative project-contained paths: {value} in {source}')
    target = check.model.contained(root, source.parent / local)
    if not target.is_file():
        raise ValueError(f'Missing local ADR link target: {value} in {source.relative_to(root)}')
    fragment = parsed.fragment if '#' in value else None
    if target in destinations:
        target_page, anchor = destinations[target]
        return _relative(page, target_page, anchor if fragment is None else fragment, parsed.query)
    if not target.is_relative_to(booksrc):
        raise ValueError(f'Local ADR resource is outside book source and is not a selected ADR: '
                         f'{value} in {source.relative_to(root)}; publish it in book.src explicitly')
    return _relative(page, PurePosixPath(target.relative_to(booksrc).as_posix()), fragment, parsed.query)


def _destination_span(text, start):
    """A small Markdown destination scanner: angles, escapes, balanced parentheses.

    The returned range excludes angle wrappers and following optional link titles.
    This is intentionally not a general Markdown parser.
    """
    while start < len(text) and text[start] in ' \t':
        start += 1
    if start < len(text) and text[start] == '<':
        end = text.find('>', start + 1)
        if end < 0:
            raise ValueError('Malformed angle-wrapped Markdown destination')
        return start + 1, end
    end, depth = start, 0
    while end < len(text):
        char = text[end]
        if char == '\\' and end + 1 < len(text):
            end += 2
            continue
        if char.isspace() or (char == ')' and depth == 0):
            break
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        end += 1
    if depth:
        raise ValueError('Unbalanced parentheses in Markdown destination')
    return start, end


def _prose_links(text, rewrite):
    if re.search(r'\{\{#(?:include|rustdoc_include|playground)\b', text):
        raise ValueError('ADR mdBook include directives are unsupported; use ordinary Markdown links')
    for tag in re.finditer(r'<[A-Za-z][^>]*>', text):
        for attribute in re.finditer(r'\b(?:href|src)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', tag[0], re.IGNORECASE):
            value = next(v for v in attribute.groups() if v is not None)
            if _local(value):
                raise ValueError(f'Relative HTML href/src in ADR is unsupported: {value}')
    replacements = []
    # Definitions and inline links use the same destination rules; reference uses
    # remain untouched. Images share the inline syntax.
    for match in re.finditer(r'^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*', text, re.MULTILINE):
        replacements.append(_destination_span(text, match.end()))
    for match in re.finditer(r'(?<!\\)!?\[(?:\\.|[^\]\\\n])*\]\([ \t]*', text):
        replacements.append(_destination_span(text, match.end()))
    for start, end in sorted(set(replacements), reverse=True):
        value = text[start:end]
        if value:
            # Markdown backslash escapes are part of syntax, not a physical filename.
            decoded = re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\]^_`{|}~\\])', r'\1', value)
            replacement = rewrite(decoded)
            # Preserve original syntax for external URLs and fragment-only links.
            if replacement == decoded:
                replacement = value
            text = text[:start] + replacement + text[end:]
    return text


def _segments(text):
    """Yield (offset, text, opaque) spans for comments and Markdown examples.

    This shared scanner protects examples both from marker activation and from
    rendering transformations; it is not a complete Markdown parser.
    """
    start = position = 0
    while position < len(text):
        end = None
        line_start = position == 0 or text[position - 1] == '\n'
        if line_start:
            line_end = text.find('\n', position)
            line_end = len(text) if line_end < 0 else line_end + 1
            line = text[position:line_end]
            fence = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
            if fence:
                closing = re.compile(r'^ {0,3}' + re.escape(fence[1][0])
                                     + '{' + str(len(fence[1])) + r',}[ \t]*\r?$', re.MULTILINE)
                match = closing.search(text, line_end)
                end = len(text) if match is None else match.end() + (match.end() < len(text))
            elif line.startswith(('    ', '\t')):
                end = line_end
        if end is None and text.startswith('<!--', position):
            closing = text.find('-->', position + 4)
            end = len(text) if closing < 0 else closing + 3
        if end is None and text[position] == '`' and (not position or text[position - 1] != '\\'):
            run = re.match(r'`+', text[position:])[0]
            closing = re.search(r'(?<!`)' + re.escape(run) + r'(?!`)', text[position + len(run):])
            if closing:
                end = position + len(run) + closing.end()
            else:
                position += len(run)
                continue
        if end is None:
            position += 1
            continue
        if position > start:
            yield start, text[start:position], False
        yield position, text[position:end], True
        start = position = end
    if start < len(text):
        yield start, text[start:], False


def _marker_count(text):
    return sum(segment.count(MARKER) for _, segment, opaque in _segments(text) if not opaque)


def _replace_marker(text, replacement):
    return ''.join(segment if opaque else segment.replace(MARKER, replacement)
                   for _, segment, opaque in _segments(text))


def _render_text(text, rewrite):
    result = []
    for offset, segment, opaque in _segments(text):
        if opaque:
            result.append(segment)
            continue
        prefix = '\x00' if offset and text[offset - 1] != '\n' else ''
        promoted = re.sub(r'^( {0,3})(#{1,5})(?=[ \t]|\r?\n|$)', r'\1#\2',
                          prefix + segment, flags=re.MULTILINE)
        result.append(_prose_links(promoted[len(prefix):], rewrite))
    return ''.join(result)


def preprocess(context: dict, book: dict) -> dict:
    """Transform native chapters in memory, never maintained ADR/book sources."""
    if context.get('renderer') not in RENDERERS:
        return book
    chapters = list(_chapters(book.get('items', book.get('sections', []))))
    hosts = [(chapter, _marker_count(chapter.get('content', ''))) for chapter in chapters]
    count = sum(amount for _, amount in hosts)
    if count == 0:
        return book
    if count != 1:
        raise ValueError(f'ADR index marker {MARKER} must occur exactly once across visible chapter contents')
    host = next(chapter for chapter, amount in hosts if amount)
    hostpath = _logical_path(host.get('path'))
    occupied = {str(_logical_path(c['path'])) for c in chapters if c.get('path') is not None}
    root = Path(check.resolve_project_root(None, helper_file=__file__, cwd=context['root'])).resolve()
    booksrc = (Path(context['root']) / context.get('config', {}).get('book', {}).get('src', 'src')).resolve()
    records = check.model.decisions(root)
    check.validate_decisions(root, records)
    if not records:
        host['content'] = _replace_marker(host['content'], 'No architecture decisions found.')
        return book

    # Tree keys are physical root-relative directory parts, never scope/owner labels.
    tree = {'children': {}, 'records': [], 'path': hostpath}
    destinations = {}
    for record in sorted(records, key=lambda r: r.path):
        source = check.model.project_path(root, record.path)
        parts = source.parent.relative_to(root).parts
        if not parts:
            raise ValueError(f'ADR requires a root-relative directory: {record.path}')
        node, prefix = tree, []
        for part in parts:
            prefix.append(part)
            if part not in node['children']:
                path = _logical_path((hostpath.parent / 'adr' / PurePosixPath(*prefix) / 'index.md').as_posix())
                if str(path) in occupied:
                    raise ValueError(f'Generated ADR chapter path collision: {path}')
                occupied.add(str(path))
                node['children'][part] = {'children': {}, 'records': [], 'path': path}
            node = node['children'][part]
        anchor = _anchor(record.id)
        if any(_anchor(other.id) == anchor for other in node['records']):
            raise ValueError(f'Duplicate generated ADR anchor {anchor!r} within {node["path"]}: {record.path}')
        node['records'].append(record)
        destinations[source] = node['path'], anchor

    rows = ['| ID | Title | Status | Scope |', '| --- | --- | --- | --- |']
    for record in sorted(records, key=lambda r: r.path):
        page, anchor = destinations[check.model.project_path(root, record.path)]
        link = _relative(hostpath, page, anchor)
        rows.append(f'| [{_escape(record.id)}]({link}) | {_escape(record.title)} | '
                    f'{_escape(record.status)} | {_escape(record.scope)} |')

    def build(node, name, parent, parent_names, number):
        path = node['path']
        content = [f'# {_escape(name)}\n', f'[Parent]({_relative(path, parent)})\n']
        children = []
        for index, (part, child) in enumerate(sorted(node['children'].items()), 1):
            childname = part.replace('-', ' ').title()
            content.append(f'- [{_escape(childname)}]({_relative(path, child["path"])})\n')
            children.append(build(child, childname, path, parent_names + [name],
                                  number + [index] if number is not None else None))
        for record in node['records']:
            source = check.model.project_path(root, record.path)
            anchor = destinations[source][1]
            rendered = _render_text(record.text, lambda value: _rebase(value, source, path, root, booksrc, destinations))
            content.extend([f'\n<a id="{anchor}"></a>\n\n', rendered,
                            f'\n\nSource: {_escape(record.path)}\n'])
        return {'Chapter': {'name': name, 'content': '\n'.join(content), 'number': number,
                            'sub_items': children, 'path': str(path), 'source_path': None,
                            'parent_names': parent_names}}

    existing = host.get('sub_items', [])
    offset = sum(isinstance(item, dict) and 'Chapter' in item for item in existing)
    generated = []
    for index, (part, node) in enumerate(sorted(tree['children'].items()), offset + 1):
        number = host.get('number')
        generated.append(build(node, part.replace('-', ' ').title(), hostpath,
                               host.get('parent_names', []) + [host['name']],
                               number + [index] if number is not None else None))
    host['content'] = _replace_marker(host['content'], '\n'.join(rows))
    host['sub_items'] = existing + generated
    return book


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == 'supports':
        return 0 if len(argv) == 2 and argv[1] in RENDERERS else 1
    try:
        if argv:
            raise ValueError('Expected no arguments or supports RENDERER')
        payload = json.load(sys.stdin)
        if not isinstance(payload, list) or len(payload) != 2 or not all(isinstance(x, dict) for x in payload):
            raise ValueError('Expected [context, book] JSON input')
        result = preprocess(*payload)
        output = json.dumps(result, ensure_ascii=False)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        print(f'adr-preprocessor: {error}', file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
