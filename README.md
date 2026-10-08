# OpenSpec DDD

A (work in progress / experimental guide) practical guide and reusable OpenSpec schema for 
- domain-centered living specifications, 
- change delivery, and 
- modular arc42 documentation. 
 
OpenSpec already maintains living specifications; this project adds explicit contract ownership, useful domain-model companions, test-first delivery guidance, and evidence-aware consumer review across domains, ports, features, adapters, and technical capabilities.

**Remark:**
Due the experimental stage, many texts are AI generated and not properly reviewed. Once the concept has proven useful and stable, text quality will improve.

## Where to start
Start with [the introduction](docs/README.md) or [the workflow guide](docs/05-change-workflow.md).
For more setup options and Pi commands, see [using the bundle](docs/09-tooling.md).

This is an independent companion to [OpenSpec](https://github.com/Fission-AI/OpenSpec),
adapted from the Living Specifications and Modular Architecture guide. It uses
OpenSpec's own lifecycle and generated agent commands. It is not an OpenSpec fork
and does not maintain a second change engine.

## Contents

- `docs/`: handbook, including workflow selection, spec input, adoption, and architecture.
- `src/schemas/ddd/`: canonical DDD base with seven native artifacts.
- `src/schemas/components/`: optional composable guidance and templates.
- `src/schemas/legacy/`: retained five-artifact workflow used by the worked example.
- `src/schemas/ddd/helpers/`: canonical read-only catalog, impact, ADR reading, and metadata helpers.
- `src/schemas/helper-packs/docs/`: shared thin documentation-check orchestrator.
- `src/addons/mdbook/`: optional project architecture publishing stub.
- `scripts/`: schema builder, documentation commands, mdBook bootstrap, and exporter.
- `build/schemas/`: generated schema variants and their index; ignored by Git.
- `examples/equipment-lending/`: baseline contracts and one deliberately unfinished change.
- `tests/`: helper tests and compatibility tests against the real OpenSpec CLI.

The implementation is checked against **OpenSpec 1.13.1** (Node.js >=20.19.0).
Other releases may need adjustments; the handbook distinguishes agent commands from
terminal commands and project conventions from enforced checks.

## Install in an OpenSpec project

Initialize OpenSpec in the target project first. Then, from this repository's root:

```sh
python3 build.py
mkdir -p /path/to/project/openspec/schemas
cp -R build/schemas/ddd /path/to/project/openspec/schemas/openspec-ddd
```

Set `schema: openspec-ddd` in the project's `openspec/config.yaml`, preserving its
existing settings. Choose `ddd+arc42+user-doc` instead of `ddd` to include both documentation components.
The build produces four compositions plus `legacy`; see
[the builder guide](scripts/schema-builder/README.md). The handbook’s worked example
continues to use the five-artifact `legacy` variant.
Every composed v3 schema includes `helpers/` automatically; no second helper copy
is needed. The historical `legacy` schema remains unchanged and includes no added
helpers; optionally copy `src/schemas/ddd/helpers/` separately for it.
See [the source guide](src/README.md) for helper usage
and [the tooling guide](docs/09-tooling.md) for agent setup, optional templates,
and validation.

## Build entry point

Run from the repository root:

```sh
python3 build.py          # All schema variants (default)
python3 build.py schemas  # Explicit schema build
python3 build.py docs     # Build and export the handbook
python3 build.py check    # Tests, source links, and rendered links
python3 build.py all      # Schemas, handbook, then checks
```

On Windows, use `python build.py` or `py -3 build.py`. The dispatcher uses the
same Python interpreter for child tools. It resolves commands and relative paths
from the repository root, including when invoked by absolute path from elsewhere.
Schema builds require Python 3.10+ and the standard library; documentation builds
have the additional requirements described below.

`check` requires an already built handbook and OpenSpec **1.13.1** on `PATH` or
through `OPENSPEC_BIN`. It rejects a missing or different CLI version so native
integration tests cannot silently skip. `all` performs both builds before checking.
The dispatcher stops at the first failing stage and preserves the child tool's
exit code; the book builder still attempts remaining books and export formats.

Arguments after `schemas` or `docs` are forwarded to the existing tool:

```sh
python3 build.py schemas --component arc42 --output build/custom/openspec-ddd
python3 build.py docs --docker
python3 build.py schemas --help
```

The root script only coordinates tools; schema composition and documentation logic
remain under `scripts/`. The existing direct commands are also available.

## Read and build

mdBook publishes this repository's handbook from `docs/`. Edit the Markdown chapters
and `docs/SUMMARY.md` for navigation; `book.toml` controls the build. Run `build`
for static HTML in `build/book/` or `serve` for a live local preview. The OpenSpec
bundle does not install a book in an adopting project. The separate
[mdBook addon](src/addons/mdbook/README.md) starts a project book that publishes its
editable `openspec/system-architecture/` entry point. It includes Mermaid
preprocessor configuration, not vendored JavaScript. The reusable builder prepares
browser assets in its own cache for both the addon and this handbook.

All chapters are ordinary Markdown. The shared Python runner reads the output path
from `[build].build-dir` in `book.toml`. Native mdBook is the default for builds
and common CLI exports: it uses `mdbook` from `PATH`, or downloads its latest stable
release. Managed Mermaid setup autodetects its native preprocessor table unless
an explicit per-book setting enables or disables setup; custom commands stay author-managed. Add `--docker` for pinned mdBook 0.5.4 and, when enabled, mdbook-mermaid 0.17.1:

```sh
./scripts/book.sh build
./scripts/book.sh serve
./scripts/book.sh --docker build
./scripts/book.sh --docker serve
```

On Windows, use the `.cmd` starter with the same options; it does not require enabling
PowerShell scripts:

```cmd
scripts\book.cmd build
scripts\book.cmd serve
scripts\book.cmd --docker build
scripts\book.cmd --docker serve
```

Root `book-builder.toml`, when present, supplies the authoritative books list.
This repository selects its existing handbook:

```toml
[books.handbook]
config = 'book.toml'
export-formats = ['markdown']
serve = true
```

Without that file, discovery selects root `book.toml` and root-level `book.*.toml`,
without recursing. Builds and exports process all selected books. Previews include
only books with `serve = true`, on separate ports, and stop together with Ctrl-C.
`--port` sets the first port. Defaults are `export-formats = ['markdown']` and
`serve = true`; formats may be `markdown`, `typst`, or `pdf`. Each `[books.alias]`
may select multiple formats, for example `export-formats = ['markdown', 'typst', 'pdf']`.
Duplicates are removed in order. The legacy `export-format = 'markdown'` remains
supported, but using both fields together or an empty list is invalid.

Select one alias, repository-relative directory, or configuration file with
`--book` (short alias `-b`). Explicit selection bypasses the serve flag. An unlisted
path is allowed with defaults; a matching configured path inherits its options.
Directories select `book.toml`. Use `--config PATH` for another builder configuration;
`--map` remains a compatibility alias. Configured paths are relative to that file;
direct paths are relative to the repository root. Books must stay inside the repository.
Custom root tables and per-book metadata may be ignored; this version has no builder
configuration template option. mdBook never sees this file: `book.toml` stays native.

Alternate filenames use temporary symlinked mdBook roots, without replacing the
original configuration. Windows may require Developer Mode or suitable privileges.
Batch commands reject overlapping build paths.

```sh
./scripts/book.sh --book handbook build
./scripts/book.sh --docker --book book.toml build
python3 scripts/md-book-builder/check.py --config book-builder.toml --book handbook --rendered
```

The builder can live anywhere inside the project. Use `--root` explicitly, or let
it discover the nearest CWD ancestor with `book-builder.toml`/`book.toml`, then its
own ancestors. Resources and caches resolve beside the actual `book.py`:

```sh
python3 /project/tools/documentation/md-book-builder/book.py --root /project build
BOOK_BUILDER=/project/tools/documentation/md-book-builder/book.py ./scripts/book.sh build
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
```

Starters accept `BOOK_BUILDER` as the actual `book.py` path; no fixed `scripts/`
installation is required. The same options work with `scripts\book.cmd` and
`python3 build.py docs`.
The checker remains single-book, defaulting to root `book.toml`; check additional
books explicitly. See the canonical [book builder guide](scripts/book.md) for
fictional multi-book configurations and full selection details.

When a required tool is unavailable on `PATH`, native mode downloads only the
missing tools' latest stable releases for the current platform. It supports Linux x86-64/ARM64, macOS Intel
(x86-64)/Apple Silicon (ARM64), and Windows x86-64. Windows uses the official `.exe`
packages. Each release asset's GitHub-provided SHA-256 digest is verified before use.

Downloads stay under `<builder>/.cache/native-tools/` beside the actual `book.py`, separated by
tool, release, and platform. This script-owned cache is locally gitignored and
independent of the book's output directory. Windows binaries end in `.exe`. For example,
macOS Apple Silicon uses `aarch64-apple-darwin`, and Windows x64 uses
`x86_64-pc-windows-msvc`. Nothing is installed into a user or system `bin` directory.
Commands already on `PATH` remain in use; cached commands are added only to the child
build's `PATH` so mdBook can discover its preprocessor. The runners need Python 3.11+
or Python 3.10 with `tomli`. The Python runner and Markdown/Typst rendering use the
host standard library (plus that Python 3.10 dependency), without creating a virtual
environment or using `uv`; common exports still require mdBook preprocessing.
PDF uses its own managed environment described below.
See the official
[mdBook releases](https://github.com/rust-lang/mdBook/releases/latest) and
[mdbook-mermaid setup](https://github.com/badboy/mdbook-mermaid#configure-your-mdbook-to-use-mdbook-mermaid).
Each `[books.alias]` optionally accepts `mermaid` and `svgbob`: omitted autodetects
the native table, `true` provisions a missing standard preprocessor, and `false`
disables managed setup without erasing author configuration. Custom commands and
their tools/assets remain author-managed; no competing standard binary is provisioned.

Managed setup permanently updates the native configuration with missing standard
preprocessor tables and Mermaid `additional-js` references relative to its directory.
Valid author scripts, custom commands, and comments are preserved. Unsupported impacted
inline/dotted TOML forms fail before writes. Maintained Markdown stays unchanged.
Mermaid scripts are extracted by the chosen binary's `install` command only in a
scratch mini-book, then hash-checked in `<builder>/.cache/scripts/mermaid/<identity>/`.
Docker uses its actual pinned image binary, not the host binary. Owned cache references
refresh per binary identity; missing standard-filename references can be repaired,
while existing author assets stay untouched. Staged native/Docker builds retain
original configuration-directory asset semantics through runtime overrides.
For raw `mdbook build` without the reusable builder, intentionally run
`mdbook-mermaid install /path/to/project` yourself to supply browser assets.

For optional ASCII diagrams, uncomment this section in `book.toml`:

```toml
[preprocessor.svgbob]
command = "mdbook-svgbob"
```

The [svgbob preprocessor](https://github.com/boozook/mdbook-svgbob) renders fenced
`bob` blocks as inline SVG. With this section absent and no per-book `svgbob = true`,
the runner does no svgbob setup. Native mode uses `mdbook-svgbob` on PATH first. Otherwise Docker compiles the
pinned upstream source and locked dependencies using a Rust builder, then copies
the executable into `<builder>/.cache/native-tools/mdbook-svgbob/`. No local Rust installation is needed. Subsequent runs reuse the cached
binary after checking its SHA-256; changing the source revision or build recipe
creates a separate cache entry. A custom `command` is left to the book author.

Docker builds support Linux x86-64/ARM64 and Windows x86-64 (a MinGW `.exe`).
Native macOS users must supply a locally built `mdbook-svgbob` on PATH, for example
with `cargo install --git https://github.com/boozook/mdbook-svgbob --rev
1d2b053859c509af3dcb5b2dae83eb5ccf214176 --locked`. Linux Docker cannot produce an
Apple executable without additional Apple SDK tooling. `--docker` works on macOS
too: it builds and runs the Linux executable inside the documentation container.
The first build requires network access and a running Docker daemon and may take
several minutes. The runner removes its temporary builder container and image on
success or failure; shared base images and Docker's build cache are retained.

The reusable addon has the same commented configuration. When building an adopting
project directly with mdBook, provide the executable yourself; the reusable builder
manages standard tooling for any selected project book.

`serve` selects an available localhost port, waits for the site to respond, and opens it
in your browser. Pass `--port 3002` to request a specific port or `--no-open` to print
the URL without opening a browser. Stop serving with Ctrl+C. The current output is
`build/book/`; changing `build-dir` to `target/book`, for example, moves HTML and
exported files there without moving the script-owned tool cache. Add any custom
generated output root to `.gitignore`. `build` captures preprocessing separately,
builds HTML once per selected book, and runs its configured export formats in order.
`export` captures preprocessing and runs only those exports, without building
or replacing HTML. Both commands accept repeated `--format` options to replace
(not append to) each book's configured list; duplicates are removed in order.
`--template` supplies the same template argument for every selected book and format.
If an export format fails, the remaining formats still run and the command exits
nonzero. PDF also emits `.typ` source; selecting both Typst and PDF still runs both
exports.

```sh
./scripts/book.sh export
python3 scripts/md-book-builder/book.py --book handbook build --format markdown --format pdf
./scripts/book.sh --book book.toml export --format pdf --template templates/custom.typ
```

Every common CLI build/export uses mdBook's actual preprocessing pipeline; no
`export = true` opt-in is needed. A temporary `book-export` backend selected through
`MDBOOK_OUTPUT` captures the full JSON RenderContext in an isolated temporary
destination. One capture per book feeds all formats, then is normally cleaned up;
export never replaces existing HTML output or maintained Markdown. Managed diagram
setup may permanently update native configuration before capture.

mdBook controls preprocessor order and renderer gating (`supports book-export` and
configured `renderers` lists). Custom preprocessors must support this backend.
`export = true` is not a universal mdBook option or export filter. Renderer-specific
gating means this need not be exactly HTML-processed Markdown: HTML-only Mermaid
preprocessing is skipped and raw fences reach the Typst converter. Generated nested
chapters are included even without source files; generator-specific logic remains
in user preprocessors, not built-in ADR logic. The converter's supported subset
still applies, not arbitrary HTML-to-Typst conversion.

`--docker export` is supported: the pinned container captures preprocessing and
host exporters render the formats (PDF uses the host managed environment). Common
exports need the native/downloaded toolchain or Docker; only Markdown/Typst
rendering is standard-library-only.

The same options work through `scripts\book.cmd` and `python3 build.py docs`.
The canonical CLI is `scripts/md-book-builder/book.py`.
The canonical standalone exporter reads the title, source directory, and output
path from the supplied configuration:

```sh
python3 scripts/md-book-builder/exporter/export_book.py book.toml --format markdown
python3 scripts/md-book-builder/exporter/export_book.py /path/to/book.toml --format typst --template templates/custom.typ
```

Unlike the integrated `book.py` runner, standalone `export_book.py` accepts one
`--format` (`markdown`, `typst`, or `pdf`) and defaults to Markdown. Its default
mode reads raw SUMMARY/source/includes without mdBook; optional `--render-context PATH`
consumes a captured JSON RenderContext instead. Common CLI captures are normally
temporary and cleaned up. A relative
`--template` path resolves against the selected configuration's directory, not the shell's
working directory. Markdown and Typst source export use only the Python 3.11+
standard library (Python 3.10 is supported with `tomli`).
For PDF, the common CLI automatically installs pinned dependencies on demand:

```sh
./scripts/book.sh export --format pdf
./scripts/book.sh export --format pdf --no-install
```

This also applies to `book.py` and `scripts\book.cmd`.
PDF exclusively uses a builder-managed environment beneath
`<builder>/.venv/` beside the actual `book.py`, partitioned by Python interpreter, runtime, and
requirements. Standard-library `venv` and pip install `typst==0.15.0`, plus
`tomli==2.2.1` on Python <3.11. A validated, complete environment is reused;
global Python, existing project virtual environments, and global `typst` are not
used or changed for PDF. The bundle-local `.gitignore` excludes `__pycache__/`,
`*.py[cod]`, and `.venv/`; the root ignore rules already cover these cache directories.

`--no-install` prevents creation/installation but can reuse a valid managed
environment. If it is unavailable, PDF fails while other formats are still attempted.
This is not a general offline switch: it does not disable mdBook downloads or
Typst registry network access. Cached/offline use also requires an available
toolchain and cached Typst registry packages. First installation
needs network access and Python `venv`/`ensurepip`; missing OS packages such as
`python3-venv` are never installed automatically. Install that support yourself or
use the [manual standalone setup](scripts/md-book-builder/exporter/README.md#standalone-pdf-dependencies)
as a fallback. Standalone `export_book.py` uses the invoking interpreter and never
auto-installs dependencies.

The Typst output retains local images, routes Mermaid through Merman, and renders
task lists through Cheq. First PDF compilation may require registry network access
for those packages. See the [exporter guide](scripts/md-book-builder/exporter/README.md)
for templates and supported Markdown details.

```sh
python3 scripts/md-book-builder/check.py --rendered  # Existing HTML; no build
python3 src/schemas/helper-packs/docs/docs-check.py  # Optional DDD + sources + build + HTML
python3 src/schemas/helper-packs/docs/docs-check.py --source-only --source openspec/specs
python3 -m unittest discover -s tests -v
```

The low-level checker checks sources and existing HTML without building or validating
DDD metadata. The docs orchestrator checks optional DDD metadata, sources, builds,
and rendered links; ordinary book operations remain DDD-independent.
DDD metadata checks live beside `ddd.py` in `src/schemas/ddd/helpers/check.py` and
work without arc42, a book, or a mandatory catalog. From an adopting project's root,
run `python3 openspec/schemas/openspec-ddd/helpers/ddd.py check` or
`python3 openspec/schemas/openspec-ddd/helpers/check.py --root .`.
Both documentation components include the same generic `docs-check.py` from
`src/schemas/helper-packs/docs/`, copied once when both are selected. It requires
an independently installed generic book builder, selected through `--builder` or
`BOOK_BUILDER`; `scripts/md-book-builder/book.py` is only a convenience discovery path.
The canonical source is `src/schemas/helper-packs/docs/docs-check.py`; installed
projects use `openspec/schemas/openspec-ddd/helpers/docs-check.py`.
Every composed schema also includes `model.py`, a shared canonical ADR reader
preserving exact original Markdown in frozen records. Project-owned renderers can
read once with `model.decisions(root)` and explicitly preflight the records with
`check.validate_decisions(root, records)`; parsing alone is not validation.
Catalog/graph logic stays in `ddd.py`, and `docs-check.py` continues using the
existing `check_project` API. Stricter project checks and renderer navigation remain
project-owned. Helpers do not migrate source formats or introduce another lifecycle.
For a general directory-grouped book view, explicitly enable the distributed
`helpers/adr-preprocessor.py` in `[preprocessor.adr]` and place `{{#adr-index}}`
once in a dedicated book chapter. It generates a virtual index, grouped pages,
navigation, and stable ID-derived anchors for HTML and native-preprocessed exports.
It never writes ADRs or replaces the maintained architecture index. Activation and
resource limitations are documented in the [helper README](src/schemas/ddd/helpers/README.md#optional-mdbook-adr-view).
No arc42-conformance checker, ADR generation, or DDD validation is installed inside
the generic book builder.
See the [helper guide](src/schemas/ddd/helpers/README.md) and
[project check guide](scripts/book.md#project-documentation-check).
Native OpenSpec validation is explicitly available through `docs-check.py --openspec`;
no extra change-status manifest is used. Checks do not establish code conformance
or decision approval and never probe external URLs.
CLI integration tests run when `openspec` is installed; otherwise they explicitly
skip. Set `OPENSPEC_BIN=/absolute/path/to/openspec` to use an isolated installation.
They operate on temporary copies, never archive the teaching example, and never
change global OpenSpec settings. Structural checks and a rendered book do not
prove that application code implements the example: this repository contains no
equipment-lending implementation.
