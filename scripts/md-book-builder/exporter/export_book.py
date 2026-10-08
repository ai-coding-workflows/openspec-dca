"""Command line interface for exporting a single-file mdBook."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

# Bootstrap the package for direct ``python path/to/export_book.py`` invocation.
if not __package__:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "exporter"

from .markdown_to_typst import FENCE_CLOSE_RE, MarkdownToTypst, typst_string, prose_transform
from .render_context import load_chapters, rewrite

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 requires the optional tomli backport.
    import tomli as tomllib


INCLUDE_RE = re.compile(r"\{\{#include\s+([^}\s]+)\s*\}\}")
SUMMARY_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
IMAGE_LINK_RE = re.compile(
    r"!\[([^\]]*)\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[\"'][^\"']*[\"'])?\)"
)
INLINE_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\((<[^>]+>|[^)]+)\)")
H1_RE = re.compile(r"^\s{0,3}#\s+(.+?)\s*#*\s*$", re.MULTILINE)
FENCE_START_RE = re.compile(r"^ {0,3}(" + chr(96) + r"{3,}|~{3,})")


class ExportError(Exception):
    """An input book cannot be exported."""


@dataclass(frozen=True)
class Chapter:
    path: Path
    title: str
    anchor: str


@dataclass(frozen=True)
class BookConfig:
    source_dir: Path
    build_dir: Path
    title: str


def load_config(book_toml: Path) -> BookConfig:
    book_toml = book_toml.resolve()
    if not book_toml.is_file():
        raise ExportError(f"book configuration not found: {book_toml}")

    try:
        config = tomllib.loads(book_toml.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ExportError(f"cannot read {book_toml}: {exc}") from exc

    book = config.get("book", {})
    build = config.get("build", {})
    title = book.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ExportError(f"{book_toml} must define a non-empty [book].title")

    root = book_toml.parent
    source_dir = _config_path(root, book.get("src", "src"))
    build_dir = _config_path(root, build.get("build-dir", "book"))
    return BookConfig(source_dir=source_dir, build_dir=build_dir, title=title.strip())


def _config_path(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ExportError("book.toml paths must be non-empty strings")
    path = Path(value)
    return (path if path.is_absolute() else root / path).resolve()


def _filename(title: str, suffix: str = ".md") -> str:
    # Keep readable spaces and Unicode, but prevent title text becoming a path.
    value = re.sub(r"[\\/]+", "-", title)
    value = re.sub(r"[<>:\"|?*\x00-\x1f]", "", value).strip(" .")
    value = re.sub(r"\s+", " ", value)
    if not value or value in {".", ".."}:
        raise ExportError("book title cannot be used as an output filename")
    return f"{value}{suffix}"


def _slug(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text).lower()
    text = re.sub(r"[^\w -]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text).strip("-")


def _summary_chapters(summary: Path, source_dir: Path) -> list[Chapter]:
    if not summary.is_file():
        raise ExportError(f"book summary not found: {summary}")

    chapters: list[Chapter] = []
    try:
        summary_text = summary.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ExportError(f"cannot read book summary {summary}: {exc}") from exc

    for line in summary_text.splitlines():
        for match in SUMMARY_LINK_RE.finditer(line):
            label, destination = match.groups()
            destination = destination.strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(destination)
            if (
                parsed.scheme
                or parsed.netloc
                or not parsed.path.lower().endswith(".md")
            ):
                continue
            chapter_path = (source_dir / unquote(parsed.path)).resolve()
            if not chapter_path.is_file():
                raise ExportError(
                    f"chapter listed in {summary} does not exist: {destination}"
                )
            chapters.append(Chapter(chapter_path, label, ""))

    if not chapters:
        raise ExportError(f"no Markdown chapters found in {summary}")

    resolved: list[Chapter] = []
    for chapter in chapters:
        try:
            text = chapter.path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ExportError(f"cannot read chapter {chapter.path}: {exc}") from exc
        match = H1_RE.search(text)
        anchor = _slug(match.group(1) if match else chapter.title)
        resolved.append(Chapter(chapter.path, chapter.title, anchor))
    return resolved


def _rewrite_chapter_links(
    text: str,
    source: Path,
    chapter_anchors: dict[Path, str],
    *,
    typst_labels: bool = False,
) -> str:
    def replace(match: re.Match[str]) -> str:
        label, destination = match.groups()
        raw = destination.strip()
        wrapped = raw.startswith("<") and raw.endswith(">")
        target_text = raw[1:-1] if wrapped else raw
        parsed = urlsplit(target_text)
        if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"):
            return match.group(0)
        target = (source.parent / unquote(parsed.path)).resolve()
        if target not in chapter_anchors:
            return match.group(0)
        fragment = (
            unquote(parsed.fragment) if parsed.fragment else chapter_anchors[target]
        )
        if typst_labels:
            fragment = _slug(fragment) or chapter_anchors[target]
            target_label = f"chapter-{chapter_anchors[target]}--{fragment}"
            return f"[{match.group(1)}](#{target_label})"
        return f"[{label}](#{fragment})"

    return INLINE_LINK_RE.sub(replace, text)


def _rewrite_images(text: str, source: Path, assets_dir: Path) -> str:
    """Copy local images and rewrite references to paths beside the Typst output."""
    output: list[str] = []
    fence_marker: str | None = None
    fence_length = 0
    for line in text.splitlines(keepends=True):
        fence_match = FENCE_START_RE.match(line)
        if fence_marker:
            output.append(line)
            if (
                (closing_match := FENCE_CLOSE_RE.match(line))
                and closing_match.group(1)[0] == fence_marker
                and len(closing_match.group(1)) >= fence_length
            ):
                fence_marker = None
            continue
        if fence_match:
            fence_marker = fence_match.group(1)[0]
            fence_length = len(fence_match.group(1))
            output.append(line)
            continue

        def replace(match: re.Match[str]) -> str:
            alt, angle_path, plain_path = match.groups()
            destination = angle_path or plain_path
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc:
                raise ExportError(
                    f"remote image cannot be included in a Typst build ({source}: {destination})"
                )
            image_path = (source.parent / unquote(parsed.path)).resolve()
            if not image_path.is_file():
                raise ExportError(
                    f"image referenced by {source} does not exist: {destination}"
                )
            suffix = image_path.suffix.lower()
            if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
                suffix = ".img"
            digest = hashlib.sha256(str(image_path).encode("utf-8")).hexdigest()[:20]
            asset_name = f"{digest}{suffix}"
            assets_dir.mkdir(parents=True, exist_ok=True)
            asset_path = assets_dir / asset_name
            if not asset_path.exists():
                try:
                    shutil.copy2(image_path, asset_path)
                except OSError as exc:
                    raise ExportError(f"cannot copy image {image_path}: {exc}") from exc
            destination = quote(f"{assets_dir.name}/{asset_name}", safe="/")
            return f"![{alt}]({destination})"

        output.append(IMAGE_LINK_RE.sub(replace, line))
    return "".join(output)


def _without_images(text: str) -> str:
    return IMAGE_LINK_RE.sub(lambda match: match.group(1), text)


def _expand_file(
    path: Path,
    chapter_anchors: dict[Path, str],
    stack: tuple[Path, ...] = (),
    *,
    typst_labels: bool = False,
    assets_dir: Path | None = None,
) -> str:
    path = path.resolve()
    if path in stack:
        cycle = " -> ".join(str(item) for item in (*stack, path))
        raise ExportError(f"include cycle detected: {cycle}")
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ExportError(f"cannot read Markdown source {path}: {exc}") from exc

    source = _rewrite_chapter_links(
        source, path, chapter_anchors, typst_labels=typst_labels
    )
    if assets_dir is not None:
        source = _rewrite_images(source, path, assets_dir)

    def replace(match: re.Match[str]) -> str:
        include_name = match.group(1)
        include_path = (path.parent / include_name).resolve()
        if not include_path.is_file():
            raise ExportError(f"include in {path} does not exist: {include_name}")
        return _expand_file(
            include_path,
            chapter_anchors,
            (*stack, path),
            typst_labels=typst_labels,
            assets_dir=assets_dir,
        ).rstrip("\n")

    expanded = INCLUDE_RE.sub(replace, source)
    return expanded if assets_dir is not None else _without_images(expanded)


def _write_text(output: Path, content: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(output)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise ExportError(f"cannot write {output}: {exc}") from exc


def export_markdown(book_toml: Path, *, render_context: Path | None = None) -> Path:
    config = load_config(book_toml)
    if render_context is not None:
        processed = load_chapters(render_context, config.source_dir, ExportError)
        sections = [prose_transform(
            rewrite(chapter, processed, markdown=True), _without_images,
        ).strip() for chapter in processed]
    else:
        chapters = _summary_chapters(config.source_dir / "SUMMARY.md", config.source_dir)
        anchors = {chapter.path: chapter.anchor for chapter in chapters}
        sections = [_expand_file(chapter.path, anchors).strip() for chapter in chapters]
    content = "\n\n".join(section for section in sections if section).rstrip() + "\n"

    output = config.build_dir / _filename(config.title)
    _write_text(output, content)
    return output


def _load_template(book_root: Path, template: Path | None) -> str:
    template_path = template or Path(__file__).parent / "templates" / "default.typ"
    if not template_path.is_absolute():
        template_path = book_root / template_path
    try:
        return template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ExportError(f"cannot read Typst template {template_path}: {exc}") from exc


def export_typst(book_toml: Path, template: Path | None = None, *,
                 render_context: Path | None = None) -> Path:
    config = load_config(book_toml)
    processed = (load_chapters(render_context, config.source_dir, ExportError)
                 if render_context is not None else None)
    chapters = ([] if processed is not None else
                _summary_chapters(config.source_dir / "SUMMARY.md", config.source_dir))
    anchors = {chapter.path: chapter.anchor for chapter in chapters}
    output = config.build_dir / _filename(config.title, ".typ")
    assets_dir = config.build_dir / (output.stem + "_assets")
    sections = []
    for chapter in chapters:
        markdown = _expand_file(
            chapter.path,
            anchors,
            typst_labels=True,
            assets_dir=assets_dir,
        ).strip()
        if markdown:
            sections.append(MarkdownToTypst(chapter.anchor).convert(markdown).rstrip())
    if processed is not None:
        for chapter in processed:
            markdown = prose_transform(
                rewrite(chapter, processed, markdown=False),
                lambda line: _rewrite_images(line, chapter.source, assets_dir),
            ).strip()
            converted = MarkdownToTypst(
                chapter.prefix, heading_labels=chapter.headings,
                anchor_ids=chapter.custom,
            ).convert(markdown).rstrip()
            sections.append(f"#box(width: 0pt, height: 0pt)[] <{chapter.start}>\n\n" + converted)
    body = "\n\n".join(sections)
    template_text = _load_template(book_toml.resolve().parent, template)
    if "{{title}}" not in template_text or "{{content}}" not in template_text:
        raise ExportError(
            "Typst template must contain both {{title}} and {{content}} placeholders"
        )
    content = template_text.replace("{{title}}", typst_string(config.title))
    content = content.replace("{{content}}", body)
    _write_text(output, content)
    return output


def export_pdf(book_toml: Path, template: Path | None = None, *,
               render_context: Path | None = None) -> Path:
    typst_path = export_typst(book_toml, template, render_context=render_context)
    output = typst_path.with_suffix(".pdf")
    temporary = output.with_name(output.stem + ".tmp.pdf")
    try:
        import typst
    except ImportError as exc:
        raise ExportError(
            "PDF output requires the optional typst Python binding. "
            "Create and activate a virtual environment (python3 -m venv .venv), "
            "then run: python -m pip install -r "
            "scripts/md-book-builder/exporter/requirements-pdf.txt. "
            "Rerun the export using that environment's Python; "
            "packages are not installed automatically."
        ) from exc
    try:
        typst.compile(str(typst_path), output=str(temporary), format="pdf")
        temporary.replace(output)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        raise ExportError(f"Typst PDF compilation failed: {exc}") from exc
    return output


def export_book(
    book_toml: Path,
    output_format: str = "markdown",
    template: Path | None = None,
    *, render_context: Path | None = None,
) -> Path:
    if output_format == "markdown":
        return export_markdown(book_toml, render_context=render_context)
    if output_format == "typst":
        return export_typst(book_toml, template, render_context=render_context)
    if output_format == "pdf":
        return export_pdf(book_toml, template, render_context=render_context)
    raise ExportError(f"unsupported output format: {output_format}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export an mdBook as Markdown, Typst, or PDF"
    )
    parser.add_argument(
        "book_toml",
        nargs="?",
        type=Path,
        default=Path("book.toml"),
        help="path to the mdBook configuration (default: ./book.toml)",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "typst", "pdf"),
        default="markdown",
        help="output format (default: markdown)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="custom Typst template; paths are relative to the book.toml directory",
    )
    parser.add_argument("--render-context", type=Path,
                        help="JSON RenderContext captured after mdBook preprocessing")
    args = parser.parse_args()
    try:
        output = export_book(args.book_toml, args.format, args.template,
                             render_context=args.render_context)
    except ExportError as exc:
        parser.exit(2, f"book-exporter: error: {exc}\n")
    print(output)


if __name__ == "__main__":
    main()
