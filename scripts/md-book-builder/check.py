#!/usr/bin/env python3
"""Check configured book source references and optionally existing local HTML."""
from __future__ import annotations

import argparse
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from book_paths import read_book_paths, tomllib
from book_selection import select_book
from book_root import resolve_project_root

SKIP_DIRS = {".git", ".venv", "venv", ".cache", "__pycache__"}
INCLUDE = re.compile(r"\{\{#include\s+([^}]+?)\s*\}\}")
MARKER = re.compile(r"\b(ANCHOR|ANCHOR_END):[^\S\n]*([^\s]+)")


def source_directory(paths) -> Path:
    """Read native [book].src relative to the selected configuration."""
    if tomllib is None:
        raise RuntimeError("Reading book.toml requires Python 3.11+ or tomli")
    config = tomllib.loads(paths.config_file.read_text(encoding="utf-8"))
    book = config.get("book", {})
    if not isinstance(book, dict):
        raise ValueError("[book] must be a table")
    source = book.get("src", "src")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("[book].src must be a non-empty path")
    return (paths.config_file.parent / source).resolve()


def without_code(text: str) -> str:
    """Mask fenced and inline code for Markdown link extraction, not includes."""
    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence is not None:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            lines.append("\n")
        elif match:
            fence = match[1]
            lines.append("\n")
        else:
            lines.append(line)
    return re.sub(r"(`+)(?!`)(.*?)\1(?!`)", "", "".join(lines), flags=re.S)


def _local_target(root: Path, page: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc:
        return None
    decoded = unquote(parsed.path)
    target = root / decoded.lstrip("/") if decoded.startswith("/") else page.parent / decoded
    target = target.resolve() if decoded else page
    if not target.is_relative_to(root) or not target.exists():
        raise ValueError(f"Missing or external local reference {reference} in {page}")
    return target


def _destination(text: str, start: int) -> str:
    """Read a Markdown destination, excluding its optional quoted title."""
    tail = text[start:].lstrip()
    if tail.startswith("<"):
        end = tail.find(">")
        return tail[1:end] if end >= 0 else ""
    depth = 0
    result = []
    escaped = False
    for char in tail:
        if escaped:
            result.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char.isspace() or (char == ")" and depth == 0):
            break
        depth += (char == "(") - (char == ")")
        result.append(char)
    return "".join(result)


def _markdown_links(text: str):
    text = without_code(text)
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*", text):
        yield _destination(text, match.end())
    # Reference definitions also hold local links/images (including SUMMARY links).
    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*", text):
        yield _destination(text, match.end())


def _anchor_selection(text: str, name: str, target: Path) -> str:
    stack = []
    sections = []
    for marker in MARKER.finditer(text):
        kind, label = marker.groups()
        if kind == "ANCHOR":
            stack.append((label, marker.end()))
        else:
            if not stack or stack[-1][0] != label:
                raise ValueError(f"Mismatched include anchor {label} in {target}")
            opened, start = stack.pop()
            if opened == name:
                sections.append(text[start:marker.start()])
    if stack or not sections:
        raise ValueError(f"Missing or unclosed include anchor {name} in {target}")
    return "\n".join(sections)


def _select_include(text: str, selector: str, target: Path) -> str:
    if not selector:
        return text
    if re.fullmatch(r"[^\s:]+", selector) and not selector.isdecimal():
        return _anchor_selection(text, selector, target)
    if not re.fullmatch(r"\d+|\d*:\d*", selector):
        raise ValueError(f"Invalid include selector {selector} in {target}")
    lines = text.splitlines(keepends=True)
    bounds = selector.split(":")
    start = int(bounds[0]) if bounds[0] else 1
    end = int(bounds[-1]) if bounds[-1] else len(lines)
    if not 1 <= start <= end <= len(lines):
        raise ValueError(f"Invalid include line selection {selector} in {target}")
    return "".join(lines[start - 1:end])


def _include_target(root: Path, page: Path, reference: str):
    filename, separator, selector = reference.strip().partition(":")
    target = _local_target(root, page, filename)
    if target is None or not target.is_file():
        raise ValueError(f"Include must reference a local file: {reference} in {page}")
    text = target.read_text(encoding="utf-8")
    if separator and not selector:
        raise ValueError(f"Empty include selector in {reference}")
    return target, _select_include(text, selector, target)


def _validate_content(root: Path, page: Path, text: str, active: tuple[Path, ...], *, markdown=True):
    if page in active:
        chain = " -> ".join(str(item) for item in (*active, page))
        raise ValueError(f"Include cycle: {chain}")
    for match in INCLUDE.finditer(text):
        target, selected = _include_target(root, page, match[1])
        _validate_content(root, target, selected, (*active, page), markdown=target.suffix.lower() == ".md")
    if markdown:
        for reference in _markdown_links(text):
            if reference:
                _local_target(root, page, reference)


def _excluded(path: Path, root: Path, excludes: tuple[Path, ...]) -> bool:
    resolved = path.resolve()
    return (not resolved.is_relative_to(root)
            or any(part in SKIP_DIRS for part in path.relative_to(root).parts)
            or any(resolved.is_relative_to(folder) for folder in excludes))


def _source_pages(source: Path, root: Path, excludes: tuple[Path, ...]):
    for directory, folders, files in os.walk(source, followlinks=False):
        parent = Path(directory)
        folders[:] = [name for name in folders if not _excluded(parent / name, root, excludes)]
        for name in files:
            page = parent / name
            if page.suffix.lower() == ".md" and not _excluded(page, root, excludes):
                yield page.resolve()


def validate_sources(root: Path, source_dirs, *, exclude_dirs=()) -> None:
    """Check only configured Markdown sources; references may use all of root.

    Exclusions affect discovery, not explicit references. Escaped symlinks are
    never scanned, and explicitly referenced escaped targets are rejected.
    """
    root = root.resolve()
    excludes = tuple((root / folder).resolve() for folder in exclude_dirs)
    seen = set()
    for folder in source_dirs:
        source = (root / folder).resolve()
        if not source.is_relative_to(root):
            raise ValueError(f"Source directory escapes project root: {source}")
        if not source.is_dir():
            raise ValueError(f"Source directory missing: {source}")
        if _excluded(source, root, excludes):
            continue
        for page in _source_pages(source, root, excludes):
            if page not in seen:
                _validate_content(root, page, page.read_text(encoding="utf-8"), ())
                seen.add(page)


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def _html_target(output: Path, page: Path, link: str) -> Path | None:
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc:
        return None
    decoded = unquote(parsed.path)
    if decoded.startswith("/"):
        target = output / decoded.lstrip("/")
    else:
        target = page.parent / decoded if decoded else page
    if target.is_dir():
        target = target / "index.html"
    target = target.resolve()
    if not target.is_relative_to(output) or not target.exists():
        raise ValueError(f"Broken rendered link {link} in {page.name}")
    return target


def _validate_html_page(output: Path, path: Path, page: Page, pages: dict) -> None:
    for link in page.links:
        target = _html_target(output, path, link)
        if target is None:
            continue
        fragment = unquote(urlsplit(link).fragment)
        if fragment and target in pages and fragment not in pages[target].ids:
            raise ValueError(f"Missing rendered anchor {link} in {path.name}")


def validate_html(output: Path) -> None:
    output = output.resolve()
    pages = {}
    for path in output.rglob("*.html"):
        resolved = path.resolve()
        if resolved.is_relative_to(output) and resolved.is_file():
            pages[resolved] = Page(path.read_text(encoding="utf-8"))
    if not pages:
        raise ValueError("Documentation build produced no HTML pages")
    for path, page in pages.items():
        _validate_html_page(output, path, page, pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", "--book", help="book alias, directory, or book.toml path")
    parser.add_argument("--config", "--map", dest="map", type=Path,
                        help="builder configuration TOML (default: root book-builder.toml)")
    parser.add_argument("--root", type=Path,
                        help="project root (default: nearest cwd or builder ancestor with a book marker)")
    parser.add_argument("--rendered", action="store_true", help="also check existing HTML; never build")
    args = parser.parse_args()
    try:
        root = resolve_project_root(args.root, builder_dir=Path(__file__).resolve().parent)
    except ValueError as error:
        parser.error(str(error))
    paths = read_book_paths(select_book(root, args.book, args.map))
    validate_sources(root, [source_directory(paths)], exclude_dirs=[paths.build_dir])
    if args.rendered:
        validate_html(paths.build_dir)
    print("Handbook references verified" + (" (source and rendered)" if args.rendered else " (source)"))


if __name__ == "__main__":
    main()
