# mdBook exporter

Export an mdBook as one Markdown file, a Typst document, or a PDF. The exporter
reads the title, source directory, and build directory from native book config.
Standalone mode defaults to raw `SUMMARY.md` chapter order, source files, and mdBook
include expansion. Common CLI exports instead consume mdBook's captured RenderContext.

Markdown and Typst rendering uses only the Python 3.11+ standard library. Python
3.10 is also supported when `tomli` is installed. These formats use the host
interpreter without creating virtual environments. The common runner manages PDF
dependencies automatically; the standalone exporter does not.

## Invocation

From the repository root, use the common documentation runner:

```sh
python3 scripts/md-book-builder/book.py export
python3 scripts/md-book-builder/book.py --book book.toml export --format markdown --format pdf
python3 scripts/md-book-builder/book.py --config book-builder.toml --book handbook build --format markdown --format typst
```

The reusable builder may live anywhere inside the project, for example:

```sh
python3 /project/tools/documentation/md-book-builder/book.py --root /project export
```

Without `--root`, it searches for the nearest CWD ancestor containing
`book-builder.toml` or `book.toml`, then its own ancestors. Resources, caches, and
the managed PDF environment resolve beside the actual `book.py`, not a fixed
`scripts/` path. Starters accept `BOOK_BUILDER` as that file's path; the project
checker accepts `docs-check.py --builder PATH`.

The runner uses root `book-builder.toml` as the authoritative books list when
present; otherwise it discovers root `book.toml` and root-level `book.*.toml`.
Each `[books.alias]` can configure `export-formats = ['markdown', 'typst', 'pdf']`;
the default is only `['markdown']`. Duplicates are removed while retaining order.
The legacy `export-format = 'markdown'` remains supported, but specifying both
fields together or an empty list is invalid.

`build` captures preprocessing separately, builds HTML once per selected book,
and runs its configured formats in order. `export` captures preprocessing and runs
only those exports, without building or replacing HTML. Both accept repeated
`--format` options to replace, not append to, the configured list; duplicates are
removed in order. If one format fails, remaining formats still run and the command
exits nonzero. `--template PATH` supplies the same template argument to every
selected book and format. `--book` selects an alias or path.
`--config PATH` selects a builder configuration; `--map` remains its compatibility
alias. Configured paths resolve relative to that file; explicit unlisted book paths
use defaults, while matching configured paths inherit options. Templates are CLI-only,
not a builder configuration option. mdBook receives only its native book configuration.

### Preprocessed input from the common CLI

All common CLI build/export outputs use mdBook's actual preprocessing pipeline,
without an `export = true` opt-in. The runner temporarily selects a `book-export`
backend via `MDBOOK_OUTPUT` and captures the full JSON RenderContext in an isolated
temporary destination. One capture per selected book is reused across formats;
capture files are normally cleaned up. Maintained Markdown and existing HTML
outputs are never replaced by export. Managed diagram setup can permanently update
the native configuration before capture: per-book `mermaid`/`svgbob` omitted means
native-table autodetection, `true` provisions missing standard preprocessors, and
`false` disables managed setup without erasing author configuration. Custom commands
and valid author assets remain author-managed and preserved.

Managed Mermaid extracts browser assets from the chosen binary only in a scratch
mini-book, caches them beside the builder, and durably adds relative `additional-js`
references. Docker uses its pinned image binary rather than a host binary. See the
[builder guide](../../book.md#managed-diagram-configuration-and-assets) for cache
identity, safe TOML editing, and staged path handling. This is separate from the
standalone exporter, which does not provision mdBook tools or browser assets.

mdBook applies native ordering and renderer gating (`supports book-export` and
configured `renderers` lists). Custom preprocessors must support `book-export`;
`export = true` is neither a universal mdBook option nor an export filter. Because
of renderer-specific gating, this is not a promise of exactly HTML-processed
Markdown. The HTML-only Mermaid preprocessor is skipped, so raw Mermaid fences
reach the Typst converter. Nested generated chapters are included even without
source files. Generator/source-specific logic remains in user preprocessors; the
reusable exporter has no built-in ADR logic.

Common exports require mdBook, downloaded/cached when missing in native mode.
`--docker export` is also supported: the pinned container captures preprocessing,
then host exporters render the formats, with PDF in the host managed environment.
Only the Markdown/Typst rendering stage is standard-library-only.

`scripts/book.sh` and `scripts/book.cmd` forward these options. See the
[book builder guide](../../book.md) for selection and serve settings. Direct
single-book invocation remains available. Unlike integrated `book.py`, standalone
`export_book.py` accepts only one `--format` (`markdown`, `typst`, or `pdf`) per
invocation and defaults to Markdown:

```sh
python3 scripts/md-book-builder/exporter/export_book.py book.toml
python3 scripts/md-book-builder/exporter/export_book.py book.toml --format typst
# Consume a retained mdBook capture instead of raw sources:
python3 scripts/md-book-builder/exporter/export_book.py book.toml --render-context /path/to/render-context.json --format typst
```

Optional `--render-context PATH` reads a captured full JSON RenderContext, including
its generated chapter tree. It does not run mdBook itself; common CLI temporary
captures are normally removed. Without it, standalone mode remains the raw
SUMMARY/source/includes path.

Outputs are `<build-dir>/<title>.md`, `.typ`, or `.pdf`. PDF export also writes
the Typst source beside the PDF. Selecting both Typst and PDF in the integrated
runner still runs both exports. Implementation and templates live in
`scripts/md-book-builder/exporter/`.

## Automatic PDF dependencies in the common runner

Recommended commands:

```sh
./scripts/book.sh export --format pdf
./scripts/book.sh export --format pdf --no-install
```

The common `book.py` CLI and `book.sh`/`book.cmd` exclusively use a
builder-managed PDF environment beneath
`<builder>/.venv/` beside the actual `book.py`, partitioned by Python interpreter, runtime, and
requirements. Standard-library `venv` and pip install pinned `typst==0.15.0`, plus
`tomli==2.2.1` on Python <3.11, only on demand. A validated, complete environment
is reused. No global Python or existing project virtual environment is modified,
and global `typst` is never used for PDF. No `uv` is needed.

`--no-install` prevents creation and installation but allows reuse of a valid
managed environment. If none is ready, PDF fails while remaining formats are still
attempted. This is not a general offline switch: mdBook downloads and Typst
registry network access are not disabled. Offline use needs an available toolchain,
cached dependencies, and cached Typst registry packages. The first installation needs network access and Python's
`venv`/`ensurepip` support. Missing OS packages such as `python3-venv` are never
installed automatically; install that support yourself or use standalone manual
setup as a fallback. The bundle-local `scripts/md-book-builder/.gitignore` excludes
`__pycache__/`, `*.py[cod]`, and `.venv/`, keeping the reusable cache ignored;
this repository's root ignore rules also cover the cache directories.

## Standalone PDF dependencies

Standalone `export_book.py` remains a low-level tool using the invoking interpreter.
It never creates an environment or installs dependencies. Create and activate your
own virtual environment, then explicitly install the pinned requirements:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/md-book-builder/exporter/requirements-pdf.txt
python scripts/md-book-builder/exporter/export_book.py book.toml --format pdf
```

On Windows, use `python -m venv .venv` and activate with
`.venv\Scripts\activate.bat` instead. The requirements
file pins `typst==0.15.0` and `tomli==2.2.1` on Python <3.11. A missing binding in
standalone mode produces an installation hint, not an automatic installation.
The first PDF build through either entry point needs access to the Typst package
registry for the Merman and Cheq packages used by the included templates;
Typst's package cache is reused later.

## Templates

The default template is `scripts/md-book-builder/exporter/templates/default.typ`.
`templates/modern-guide.typ` adds a designed cover, styled contents page,
chapter hierarchy, running headers, and page numbers. Both support Mermaid
and checklists.

Select a custom template using `--template PATH`:

```sh
python3 scripts/md-book-builder/book.py export --format typst --template scripts/md-book-builder/exporter/templates/modern-guide.typ
python3 scripts/md-book-builder/exporter/export_book.py book.toml --format typst --template templates/print.typ
```

For both the runner and direct invocation, relative template paths resolve against
the selected configuration's directory. Templates must contain both `{{title}}` and `{{content}}`
placeholders. Custom templates rendering Mermaid or task lists must configure
Merman or Cheq themselves.

## Supported Markdown

The converter handles headings, paragraphs, inline emphasis and code, links,
local images, lists and task lists, blockquotes, fenced code blocks, horizontal
rules, simple pipe tables, and dollar-delimited math. Mermaid fences become
Typst raw blocks rendered by Merman. This supported subset applies to captured
preprocessor output too; arbitrary generated HTML is not fully convertible to Typst.

Typst copies local images into a title-specific asset directory, resolving paths
from the chapter's host source provenance. Relative image origins lost during
native include expansion cannot be reconstructed; an unresolvable image produces
an error. Remote image URLs are rejected for Typst/PDF. Both source and captured-tree
Markdown exports remain text-only, replacing image embeds with their alt text.

Captured chapter paths must stay within the configured source tree. Part titles
and separators are omitted from the combined export. Empty HTML anchors are
supported for chapter links; arbitrary HTML remains outside the Typst subset.
