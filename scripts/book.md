# Book builder

The reusable builder builds mdBook sites, serves live previews, exports single-file
books, and checks links. Maintained Markdown stays unchanged; managed diagram
setup can permanently update native book configurations. Implementation lives in
`md-book-builder/`, which can be placed anywhere inside the project.

## Requirements

- Python 3.11+ and the standard library, or Python 3.10 with `tomli`; no `uv`.
- PDF only: the common CLI automatically prepares an isolated environment with
  `typst==0.15.0` and, on Python <3.11, `tomli==2.2.1`.
- Native mode uses `mdbook` from `PATH` or verified downloads. Managed Mermaid and
  svgbob use standard preprocessors; custom commands remain author-managed.
  svgbob builds require Docker unless a native binary exists.
- Tool downloads/builds share `<builder>/.cache/native-tools/`, relative to the
  actual `book.py` directory, independent of `[build].build-dir`.
- Docker mode needs Docker Compose and a running daemon; its pinned toolchain is
  in `md-book-builder/docker/`.
- Alternate configurations and cached browser-asset staging require permission
  to create symbolic links (Windows may require Developer Mode).

## Build and preview

Run from the repository root:

```sh
./scripts/book.sh build
./scripts/book.sh serve --port 3002 --no-open
./scripts/book.sh --docker build
python3 scripts/md-book-builder/book.py build
python3 build.py docs
```

On Windows, use `scripts\book.cmd` with the same options. `build.py docs` forwards
arguments to the canonical builder.

No fixed `scripts/` layout is required when reusing the bundle. All resources,
caches, and the PDF environment resolve relative to the actual `book.py` directory.
Use `--root` to select the project explicitly; otherwise the builder searches for
the nearest CWD ancestor containing `book-builder.toml` or `book.toml`, then searches
its own ancestors. For example:

```sh
python3 /project/tools/documentation/md-book-builder/book.py --root /project build
BOOK_BUILDER=/project/tools/documentation/md-book-builder/book.py ./scripts/book.sh build
```

`BOOK_BUILDER` names the actual `book.py` file for shell/Windows starters, not a
required installation directory.

`build` builds HTML once per selected book, then runs its configured export formats
in order, writing output to `[build].build-dir`. `serve` watches sources and opens a browser unless
`--no-open` is set. Multiple previews use separate available localhost ports;
`--port` sets the first port. Ctrl-C stops them together. Build directories must
not overlap.

## Select books and configure defaults

When root `book-builder.toml` exists, its books list is authoritative. This
repository's handbook entry is:

```toml
[books.handbook]
config = 'book.toml'
export-formats = ['markdown']
serve = true
```

Without a builder configuration, discovery selects root `book.toml` and root-level
`book.*.toml`, without recursing. An adopting project's fictional two-book setup
could instead use the following (create its book configurations first):

```toml
[books.ar42]
config = 'architecture/book.toml'
export-formats = ['markdown']
serve = true

[books.user]
config = 'book.user.toml'
export-formats = ['markdown', 'typst', 'pdf']
serve = false
```

Each `[books.alias]` accepts `export-formats`, a nonempty list of `markdown`,
`typst`, or `pdf`, defaulting to `['markdown']`. Duplicates are removed while
retaining order. The legacy singular `export-format = 'markdown'` remains
supported; specifying both fields together or an empty list is invalid.
`serve` defaults to `true`. Optional `mermaid` and `svgbob` booleans control managed
diagram setup independently for each book: omitted means autodetect the native
preprocessor table; `true` provisions a missing standard preprocessor; `false`
disables managed setup without removing author configuration. For example, add
`mermaid = true` to `[books.ar42]` to enable Mermaid without editing its native
configuration first. Existing custom commands are preserved, never replaced or
shadowed by a competing standard binary; their tools and assets remain the author's
responsibility even with `true`.

Builds and exports process all selected books; automatic
previews include only entries with `serve = true`. Explicit `--book` (or `-b`)
selects an alias or path and bypasses the serve flag:

```sh
./scripts/book.sh --book handbook build
# Fictional adopting-project selections:
./scripts/book.sh --book ar42 serve
./scripts/book.sh --book book.user.toml build
```

Use `--config PATH` to select another builder configuration; `--map` remains a
compatibility alias. Configured book paths resolve relative to that file. Direct
`--book` paths resolve relative to the repository root and must stay inside it;
directories select `book.toml`. An unlisted explicit path is allowed and uses the
default options; a path matching a configured book inherits its options.
Custom root tables and per-book metadata may be ignored. There is no builder
configuration template option in this version. mdBook never receives the builder
configuration: `book.toml` and alternate book configurations remain native mdBook TOML.

Alternate configurations use temporary symlinked book roots. Docker mounts sources
read-only and the selected output directory writable. The wrapper passes an
absolute `MDBOOK_BUILD__BUILD_DIR` through Compose so output never lands inside the
temporary root. Keep that environment forwarding when copying these scripts.

### Managed diagram configuration and assets

Managed setup permanently adds missing standard preprocessor tables to the selected
native `book.toml` (or alternate configuration). Mermaid also adds relative
`[output.html].additional-js` cache references. These are durable configuration
changes, not runtime-only overrides: review and commit them as appropriate.
Valid author scripts, custom commands, and comments are preserved. Impacted inline
or dotted TOML forms outside the supported table/array syntax fail safely before
configuration writes; convert those forms explicitly rather than expecting a rewrite.

Mermaid browser scripts come from the chosen executable's `install` command, run
only in a scratch mini-book. They are hash-checked and cached under
`<builder>/.cache/scripts/mermaid/<identity>/`; Docker extracts scripts using the
actual binary from its pinned image, not a host executable. Recognized builder-owned
cache references refresh when binary identity changes. Missing references to the
standard Mermaid filenames can be repaired; existing author assets are untouched.
No JavaScript is vendored in the addon or installed into maintained Markdown sources.
Native and Docker staging give cached scripts safe temporary asset aliases, so
mdBook copies them into HTML even when the builder is outside a nested book root.
Maintained cache references are not replaced by those aliases; temporary roots
are removed when the command exits.

## Check and export

```sh
python3 scripts/md-book-builder/check.py             # Source links
python3 scripts/md-book-builder/check.py --rendered  # Source and built HTML links
python3 scripts/md-book-builder/check.py --config book-builder.toml --book handbook --rendered
```

The checker remains single-book and defaults to root `book.toml`; explicitly select
additional books after building them. It supports `--config` and the compatibility
`--map` alias. It checks
configured book sources, local includes (selectors and cycles), and local references.
`--rendered` checks already built HTML; it does not start a build. Neither mode
checks external URLs, DDD metadata, or content/code conformance.

### Project documentation check

The single thin `docs-check.py` orchestrator lives in
`src/schemas/helper-packs/docs/docs-check.py`. Both arc42 and user-doc include this generic
helper pack once in their composed schema, not an arc42-conformance checker.
Installing the chosen schema includes helpers automatically. The historical
five-artifact legacy schema adds none; its optional DDD helpers may be copied
separately.

From an adopting project's root, with the generic builder installed separately:

```sh
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --source-only --source openspec/specs --builder tools/documentation/md-book-builder/book.py
```

In this repository, invoke the canonical source directly:

```sh
python3 src/schemas/helper-packs/docs/docs-check.py
python3 src/schemas/helper-packs/docs/docs-check.py --docker --book handbook
python3 src/schemas/helper-packs/docs/docs-check.py --openspec
```

It checks optional DDD metadata first, then source references, builds selected books
once, and checks local links and anchors in every configured HTML output. Source
folders come from each native `[book].src`; repeated `--source` adds project-relative
folders without imposing arc42 or user-documentation paths. Selection uses the
builder's authoritative list and `--book`/`--config`. `--builder PATH` selects the
actual `book.py` when installed elsewhere; `BOOK_BUILDER` selects the same file.
The generic builder is required separately and may live in arbitrary folders;
`<root>/scripts/md-book-builder/book.py` is only convenience discovery. Generic
source/include/HTML validation and builds stay in `md-book-builder/`, with no
DDD validation inside that builder. Native mode is the default;
`--source-only` does not build or check HTML. Verification builds request Markdown
only, avoiding PDF dependency/registry setup. Without books, rendering is explicitly
skipped; optional DDD checks and explicitly selected sources still work.

The installed orchestrator uses adjacent `check.py` for DDD checks. Use
`--ddd-helper PATH` for an alternate metadata checker, including ambiguous
multi-schema installations. Legacy `openspec/ddd/check.py` remains a supported
fallback, not the primary install recommendation. Canonical DDD sources are in
`src/schemas/ddd/helpers/`, including the shared canonical ADR reader `model.py`
and standard-library `project_root.py`;
default root discovery follows the helpers' nearest `openspec` ancestor to its
project parent, not a fixed depth. Explicit `--root` is supported. From the project
root, use `python3 openspec/schemas/openspec-ddd/helpers/check.py --root .` for
metadata alone. Missing optional metadata is reported as skipped. If
metadata exists or is explicitly selected but the helper is missing, install the
helper or explicitly pass `--skip-ddd`. `--catalog`, repeated `--decisions`, and
repeated `--status` configure the optional DDD checks. Human/system ADR scopes need
not be catalog owners. See [the DDD helper](../src/schemas/ddd/helpers/README.md).

Project-owned ADR preprocessors/renderers can read once with `model.decisions(root)`,
explicitly preflight the records with `check.validate_decisions(root, records)`,
then render their exact original `record.text`. Parsing alone does not validate
metadata or supersession targets. Grouping, navigation, and stricter project rules
remain project-owned; the generic builder gains no ADR generation. A general
optional renderer is distributed as `helpers/adr-preprocessor.py`: explicitly
configure `[preprocessor.adr]` in the selected native book and put `{{#adr-index}}`
once in a dedicated book chapter. It generates a virtual directory-grouped ADR
view with stable anchors for HTML and `book-export`, without writing source pages
or replacing the maintained architecture index. See the
[shared reading API](../src/schemas/ddd/helpers/README.md#shared-adr-reading-api).
The orchestrator continues using `check.check_project` for optional DDD metadata,
not a new manifest or rendering lifecycle. Helpers are read-only; source-format
migration is explicit project work, never an automatic renderer rewrite.

`--openspec` explicitly invokes native `openspec validate --all --strict
--no-interactive`, using PATH or `OPENSPEC_BIN`; no extra change manifest or status
model is introduced. No check establishes approval, architecture correctness, code
conformance, delivery acceptance, or external URL availability.

Use `scripts/book.sh`, `scripts\book.cmd`, or
`scripts/md-book-builder/book.py` for ordinary DDD-independent book operations.

`export` runs only exports for all selected books using their configured formats,
without building or replacing HTML. Both `build` and `export` accept repeated
`--format markdown|typst|pdf` options to replace (not append to) each book's
configured list. Duplicates are removed in order. If one format fails, remaining
formats still run and the command exits nonzero. PDF also emits `.typ` source;
selecting Typst and PDF still runs both exports. `--template PATH` supplies the
same template argument for every selected book and format:

```sh
./scripts/book.sh export
./scripts/book.sh build --format markdown --format pdf --template templates/custom.typ
python3 scripts/md-book-builder/book.py export --format markdown --format pdf
python3 scripts/md-book-builder/exporter/export_book.py book.toml --format markdown
```

### Native preprocessing for common CLI exports

Every common CLI build/export uses mdBook's actual preprocessing pipeline; no
preprocessor opt-in is needed. `build` performs a separate capture pass, then builds
HTML once and runs the exports. `export` performs only that capture pass, never an
HTML build. The runner temporarily selects the `book-export` backend through `MDBOOK_OUTPUT`,
captures the full JSON RenderContext in an isolated temporary destination, and
reuses one capture per selected book for all requested formats. Temporary capture
files are normally cleaned up; existing HTML output and maintained Markdown
are not replaced. Managed diagram setup may durably update the native configuration
before capture. Output destinations containing the book root or source directory
are rejected to prevent native HTML cleanup from deleting maintained inputs.
Capture refuses missing SUMMARY source files instead of creating
placeholders. Configured preprocessors execute normally and should be read-only.
Source and final output paths still come from native book config.

mdBook controls preprocessor ordering and normal renderer gating, including
`supports book-export` and configured `renderers` lists. Custom preprocessors must
support this backend. `export = true` is unnecessary, is not a universal mdBook
configuration option, and is not an export filter. Renderer-specific gating means
the captured Markdown need not exactly match HTML-processed Markdown: the
HTML-only Mermaid preprocessor is skipped, leaving raw Mermaid fences for the
Typst converter. Generated nested chapters are included even when their source
files do not exist. Source/generator-specific behavior belongs in the user's
preprocessor, not in the reusable exporter; there is no built-in ADR generation.
The converter's supported Markdown subset still applies, not arbitrary HTML-to-Typst
conversion.

`--docker export` is supported: capture runs inside the pinned container, then host
Python renders the formats. PDF uses the host's own managed environment. Common
exports therefore need the native/downloaded mdBook toolchain or Docker; they are
not entirely mdBook-independent standard-library operations.

Unlike integrated `book.py`, standalone `exporter/export_book.py` accepts one
`--format` per invocation and defaults to Markdown. Its default mode reads raw
`SUMMARY.md`, source files, and includes without running mdBook. Optional
`--render-context PATH` consumes a previously captured JSON RenderContext instead.

Relative CLI template paths resolve against each selected book configuration's
directory, not the builder configuration directory. Markdown/Typst exports use
the invoking Python interpreter and standard library (plus `tomli` on Python 3.10),
without creating a virtual environment.

### Automatic PDF dependencies

Use the common CLI or shell/Windows starters:

```sh
./scripts/book.sh export --format pdf
./scripts/book.sh export --format pdf --no-install
```

PDF exclusively uses a builder-managed environment beneath
`<builder>/.venv/` beside the actual `book.py`, partitioned by Python interpreter, runtime, and
requirements. On demand, the builder uses standard-library `venv` and pip to install
`requirements-pdf.txt`: `typst==0.15.0`, plus `tomli==2.2.1` on Python <3.11.
It reuses a validated, complete environment; it never changes global Python or
existing project virtual environments and never uses global `typst` for PDF.
No `uv` is required.

`--no-install` disables environment creation and dependency installation, but allows
reuse of a valid managed environment. If none is ready, PDF fails while remaining
formats are still attempted. This is not a general offline switch: it does not
prevent mdBook toolchain downloads or Typst registry network access. Cached/offline
exports also need the toolchain and registry packages already available.

The first installation needs network access and Python's `venv`/`ensurepip` support.
Missing OS packages (such as a distribution's `python3-venv`) are never installed
automatically; install that support yourself or use the manual standalone exporter
below as a fallback. First PDF compilation may also need Typst registry network
access for Merman and Cheq.

The standalone `exporter/export_book.py` remains a low-level tool using the invoking
interpreter, without automatic installation. For its manual virtual-environment
setup, see the [exporter guide](md-book-builder/exporter/README.md#standalone-pdf-dependencies).

## Directory roles

- `md-book-builder/`: canonical CLI, selection, toolchain, checker, and Docker setup.
- `md-book-builder/exporter/`: standalone exporter, templates, and optional PDF
  requirements; see the [exporter guide](md-book-builder/exporter/README.md).

Optional fenced `bob` diagrams are enabled by `[preprocessor.svgbob]` or the
per-book `svgbob = true` setting; see
[toolchain details](../README.md#read-and-build) for setup and platform limits.
Generated output and tool caches should remain ignored by version control.
The bundle-local `md-book-builder/.gitignore` excludes `__pycache__/`, `*.py[cod]`,
`.venv/`, and `.cache/`, so managed dependencies and compiled/downloaded tools stay
ignored when reused elsewhere.
This repository's root `.gitignore` also covers `.venv/` and `__pycache__/`.
