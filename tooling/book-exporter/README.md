# book-exporter

Export an mdBook as one Markdown file, a Typst document, or a PDF. The tool reads
the book title, source directory, and build directory from book.toml; it uses
SUMMARY.md for chapter order and expands mdBook include directives.

Run the Markdown export from the book's project root:

    uv run --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml

The output is <build-dir>/<title>.md. No exporter configuration beyond the
existing book.toml and mdBook source files is needed.

## Typst and PDF

Generate Typst source with:

    uv run --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml --format typst

Generate Typst source and a PDF with:

    uv run --extra typst-output --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml --format pdf

Typst output is <build-dir>/<title>.typ. PDF output also writes that source file
beside <title>.pdf. PDF compilation uses the typst Python binding. The first PDF
build needs access to the Typst package registry to download the Merman and Cheq
packages used by the default template. Typst's package cache is reused later.

Select a custom Typst template with --template. A relative template path is
resolved against the directory containing book.toml:

    uv run --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml --format typst --template templates/print.typ

The template must contain both <code>{{title}}</code> and
<code>{{content}}</code> placeholders. The default template is
templates/default.typ. A custom template that renders Mermaid or task lists must
configure Merman or Cheq itself.

## Supported Markdown

The converter handles headings, paragraphs, inline emphasis and code, links,
local images, lists and task lists, blockquotes, fenced code blocks, horizontal
rules, simple pipe tables, and dollar-delimited math. Mermaid fences become
Typst raw blocks and are rendered by Merman.

Local images are copied into a title-specific asset directory under the build
directory. Remote image URLs are rejected because Typst cannot fetch them during
compilation. Markdown output continues to replace image embeds with their alt
text.

## Included templates

`templates/default.typ` is the minimal print layout. `templates/modern-guide.typ`
adds a designed cover, styled contents page, clearer chapter hierarchy, and
running headers and page numbers. Both include Mermaid and checklist support.

Select the modern guide design when exporting a PDF:

    uv run --extra typst-output --no-cache --project tooling/book-exporter python tooling/book-exporter/export_book.py book.toml --format pdf --template tooling/book-exporter/templates/modern-guide.typ
