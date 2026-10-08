"""Adapt an mdBook RenderContext without consulting its temporary configuration."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit

from .markdown_to_typst import HEADING_RE, EMPTY_ANCHOR_RE, slugify, prose_transform


LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\((<[^>]+>|[^)]+)\)")


@dataclass
class ProcessedChapter:
    path: Path
    source: Path
    content: str
    prefix: str
    headings: list[str] = field(default_factory=list)
    fragments: dict[str, str] = field(default_factory=dict)
    custom: dict[str, str] = field(default_factory=dict)

    @property
    def start(self) -> str:
        return self.prefix + "--start"


def _read_items(context: Path, error: type[Exception]) -> object:
    try:
        data = json.loads(context.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise error(f"cannot read render context {context}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("book"), dict):
        raise error("render context must contain a book object")
    return data["book"].get("items")


def _chapter_item(item: object, error: type[Exception]) -> dict | None:
    """Validate the tagged book item, ignoring native navigation-only items."""
    if item == "Separator":
        return None
    if not isinstance(item, dict) or len(item) != 1:
        raise error("invalid render context book item")
    if "PartTitle" in item and isinstance(item["PartTitle"], str):
        return None
    if "Separator" in item and item["Separator"] is None:
        return None
    chapter = item.get("Chapter")
    if not isinstance(chapter, dict):
        raise error("invalid render context Chapter")
    _validate_chapter(chapter, error)
    return chapter


def _validate_chapter(chapter: dict, error: type[Exception]) -> None:
    for key in ("name", "content"):
        if not isinstance(chapter.get(key), str):
            raise error(f"Chapter.{key} must be a string")
    for key in ("path", "source_path"):
        if chapter.get(key) is not None and not isinstance(chapter[key], str):
            raise error(f"Chapter.{key} must be a string or null")
    if not chapter["name"].strip():
        raise error("Chapter.name must be non-empty")


def _logical_path(value: str, source_dir: Path, error: type[Exception]) -> Path:
    normalized = value.replace("\\", "/")
    if not value or "\x00" in value or Path(normalized).is_absolute() or PureWindowsPath(value).drive:
        raise error(f"invalid chapter path: {value!r}")
    result = (source_dir / normalized).resolve()
    if not result.is_relative_to(source_dir):
        raise error(f"chapter path escapes source directory: {value}")
    return result


def _source_path(provenance: str | None, path: Path, source_dir: Path) -> Path:
    if not provenance:
        return path
    candidate = Path(provenance.replace("\\", "/"))
    if PureWindowsPath(provenance).drive and not candidate.is_absolute():
        return path  # A captured Windows drive is not a relative host path.
    if not candidate.is_absolute():
        return (source_dir / candidate).resolve()
    # Absolute container paths are not host provenance. Only existing paths
    # within the host source tree are accepted as absolute paths.
    if candidate.is_relative_to(source_dir) and candidate.is_file():
        return candidate
    return path


class _ChapterTree:
    """Validate and flatten chapters in depth-first, parent-first order."""

    def __init__(self, source_dir: Path, error: type[Exception]) -> None:
        self.source_dir = source_dir
        self.error = error
        self.chapters: list[ProcessedChapter] = []
        self.paths: set[Path] = set()

    def walk(self, items: object) -> None:
        if not isinstance(items, list):
            raise self.error("render context chapter items/sub_items must be arrays")
        for item in items:
            chapter = _chapter_item(item, self.error)
            if chapter is not None:
                self.append(chapter)
                self.walk(chapter.get("sub_items", []))

    def append(self, chapter: dict) -> None:
        identity = len(self.chapters) + 1
        if chapter.get("path") is not None:
            path = _logical_path(chapter["path"], self.source_dir, self.error)
        else:
            path = self.source_dir / f".export-chapter-{identity}.md"
        if path in self.paths:
            raise self.error(f"duplicate chapter path: {path}")
        self.paths.add(path)
        source = _source_path(chapter.get("source_path"), path, self.source_dir)
        self.chapters.append(
            ProcessedChapter(path, source, chapter["content"], f"chapter-{identity}")
        )


class _AnchorCollector:
    """Allocate collision-free labels and chapter-local fragment aliases."""

    def __init__(self, chapter: ProcessedChapter, error: type[Exception]) -> None:
        self.chapter = chapter
        self.error = error
        self.used = {chapter.start}
        self.counts: dict[str, int] = {}
        self.heading_slugs: list[str] = []
        self.heading_counts: dict[str, int] = {}

    def collect(self) -> None:
        prose_transform(self.chapter.content, self.collect_heading, protect_inline=False)
        prose_transform(self.chapter.content, self.collect_line)

    def collect_heading(self, line: str) -> str:
        match = HEADING_RE.match(line)
        if match:
            text = EMPTY_ANCHOR_RE.sub("", match.group(2))
            self.heading_slugs.append(slugify(text) or "section")
        return line

    def allocate(self, raw: str) -> str:
        base = slugify(raw) or "section"
        count = self.counts.get(base, 0)
        label = self.chapter.prefix + "--" + base + (f"-{count}" if count else "")
        while label in self.used:
            count += 1
            label = self.chapter.prefix + "--" + base + f"-{count}"
        self.counts[base] = count + 1
        self.used.add(label)
        self.chapter.fragments.setdefault(raw, label)
        return label

    def add_heading(self) -> None:
        raw = self.heading_slugs[len(self.chapter.headings)]
        label = self.allocate(raw)
        self.chapter.headings.append(label)
        # mdBook's duplicate heading aliases are chapter-local.
        occurrence = self.heading_counts.get(raw, 0)
        self.heading_counts[raw] = occurrence + 1
        alias = raw + (f"-{occurrence}" if occurrence else "")
        self.chapter.fragments.setdefault(alias, label)

    def add_custom(self, raw: str) -> None:
        if raw in self.chapter.custom:
            raise self.error(f"duplicate explicit anchor {raw!r} in {self.chapter.path}")
        label = self.allocate(raw)
        self.chapter.custom[raw] = label
        # Explicit ids take precedence over automatically generated ids.
        self.chapter.fragments[raw] = label

    def collect_line(self, line: str) -> str:
        if HEADING_RE.match(line):
            self.add_heading()
        for match in EMPTY_ANCHOR_RE.finditer(line):
            self.add_custom(match.group(2))
        return line


def load_chapters(context: Path, source_dir: Path, error: type[Exception]) -> list[ProcessedChapter]:
    tree = _ChapterTree(source_dir, error)
    tree.walk(_read_items(context, error))
    if not any(chapter.content.strip() for chapter in tree.chapters):
        raise error("render context has no useful chapters")
    for chapter in tree.chapters:
        _AnchorCollector(chapter, error).collect()
    return tree.chapters


def _chapter_lookup(chapters: list[ProcessedChapter]) -> dict[Path, ProcessedChapter]:
    lookup: dict[Path, ProcessedChapter] = {}
    for target in chapters:
        for path in (target.path, target.source):
            lookup.setdefault(path, target)
            if path.suffix.lower() == ".md":
                lookup.setdefault(path.with_suffix(".html"), target)
    return lookup


class _ChapterRewriter:
    """Rewrite prose links and Markdown anchors using the complete chapter tree."""

    def __init__(self, chapter: ProcessedChapter,
                 lookup: dict[Path, ProcessedChapter], markdown: bool) -> None:
        self.chapter = chapter
        self.lookup = lookup
        self.markdown = markdown
        self.heading_index = 0

    def link(self, match: re.Match[str]) -> str:
        destination = match.group(2).strip().strip("<>")
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc:
            return match.group(0)
        if parsed.path:
            path = (self.chapter.path.parent / unquote(parsed.path)).resolve()
            target = self.lookup.get(path)
        else:
            target = self.chapter
        if target is None:
            return match.group(0)
        label = target.fragments.get(unquote(parsed.fragment)) if parsed.fragment else target.start
        return f"[{match.group(1)}](#{label})" if label else match.group(0)

    def custom_anchor(self, match: re.Match[str]) -> str:
        return f'<a id="{self.chapter.custom[match.group(2)]}"></a>'

    def transform(self, line: str) -> str:
        heading = HEADING_RE.match(line)
        line = LINK_RE.sub(self.link, line)
        if self.markdown:
            line = EMPTY_ANCHOR_RE.sub(self.custom_anchor, line)
        if heading:
            label = self.chapter.headings[self.heading_index]
            self.heading_index += 1
            if self.markdown:
                line = f'<a id="{label}"></a>\n' + line
        return line


def rewrite(chapter: ProcessedChapter, chapters: list[ProcessedChapter], *, markdown: bool) -> str:
    rewriter = _ChapterRewriter(chapter, _chapter_lookup(chapters), markdown)
    body = prose_transform(chapter.content, rewriter.transform)
    return (f'<a id="{chapter.start}"></a>\n\n' + body) if markdown else body
