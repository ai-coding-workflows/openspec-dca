### arc42 documentation

Use `docs-check.py` for the configured architecture book and local source links.
It does not require a fixed arc42 directory and does not assess architectural
quality or completion of arc42 sections. Preserve the distinction between
source/rendering checks and semantic architecture review.

## Optional mdBook ADR view

Compositions selecting arc42 distribute `adr-preprocessor.py`. It is inactive until
you explicitly add the following to the selected native `book.toml`, substituting
the installed schema directory and Python executable as needed:

```toml
[preprocessor.adr]
command = "python3 openspec/schemas/openspec-ddd/helpers/adr-preprocessor.py"
```

In one book chapter registered in `SUMMARY.md`, add this visible marker exactly
once, outside code examples and HTML comments:

```markdown
# ADR view

{{#adr-index}}
```

Use a dedicated book-view chapter, not a replacement for the maintained architecture
index. The preprocessor reads canonical maintained ADRs using the DDD model's default
scoped discovery, then explicitly runs generic ADR validation from the adjacent DDD
checker. No catalog is required; this view does not add catalog-only selections or
scan changes and archives.

It replaces the marker with a title/status/scope index and adds virtual decision
pages and directory-based navigation beneath the chapter. Grouping follows the
project-relative source directory, not catalog ownership or a project's label map.
Generated page paths start with `adr/` beside the marker chapter; no generated
Markdown is written to the source tree. Existing chapter children are retained.
An empty selection produces an empty-state message. Without the marker the book
passes through unchanged, without an ADR scan.

Explicit ADR anchors derive deterministically from the ID. The same ID may occur
on different pages; collisions within one generated page, duplicate markers, and
collisions with existing chapter paths are errors. An anchor remains stable while
the ID remains unchanged; the full URL also depends on the source directory and
marker chapter location. Stable anchors identify ADRs, not every internal section:
merged section headings still use the renderer's ordinary heading anchors.

Rendered ADR headings and local Markdown links are adjusted for the generated
page while original files and `AdrRecord.text` stay unchanged. Links between
selected ADRs target the generated pages. Other local links/images must point to
existing files within the book source tree; unsupported outside-book resources
fail rather than being silently copied or rendered as broken links. Keep code
examples fenced. Raw HTML resource links and mdBook include directives are not a
substitute for supported Markdown links in this view.

The preprocessor supports native `html` and `book-export` renderers, including the
builder's native-preprocessed exports. It does not generate records, infer approval,
change statuses, or replace the durable architecture index. The generic builder
contains no ADR-generation logic. Custom renderers and stricter project checks
remain possible through the DDD shared reading API.
