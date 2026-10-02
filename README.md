# OpenSpec DDD

A practical guide and reusable OpenSpec schema for domain-centered living
specifications, change delivery, and modular arc42 documentation. OpenSpec already
maintains living specifications; this project adds explicit contract ownership, useful
domain-model companions, test-first delivery guidance, and evidence-aware consumer
review across domains, ports, features, adapters, and technical capabilities.

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
- `src/helpers/ddd/`: optional read-only catalog and impact helper.
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
The build produces all eight combinations plus `legacy`; see
[the builder guide](scripts/schema-builder/README.md). The handbook’s worked example
continues to use the five-artifact `legacy` variant.
See [the source guide](src/README.md) for optional helpers
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
Commands stop at the first failure and preserve the child tool's exit code.

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
editable `openspec/system-architecture/` entry point. It includes the Mermaid
JavaScript assets and preprocessor configuration; this handbook shares those assets
from `src/addons/mdbook/theme/`.

All chapters are ordinary Markdown. The shared Python runner reads the output path
from `[build].build-dir` in `book.toml`. Native mdBook is the default: it uses
`mdbook` and `mdbook-mermaid` from `PATH`, or downloads their latest stable releases
when either command is missing. Add `--docker` to use the pinned mdBook 0.5.4 and
mdbook-mermaid 0.17.1 image instead:

```sh
./scripts/docs.sh build
./scripts/docs.sh serve
./scripts/docs.sh --docker build
./scripts/docs.sh --docker serve
```

On Windows, use the `.cmd` starter with the same options; it does not require enabling
PowerShell scripts:

```cmd
scripts\docs.cmd build
scripts\docs.cmd serve
scripts\docs.cmd --docker build
scripts\docs.cmd --docker serve
```

The root `book.toml` remains the default. To select another book, pass a
repository-relative directory or its `book.toml` path, or define aliases in an
optional root `docs-books.toml`:

```toml
[books]
ar42 = "architecture"
user = "user-guide/book.toml"
```

Each directory contains its own `book.toml`; mdBook requires that filename.
The paths above illustrate adopting-project destinations; create the books before
using these aliases. Mapping values are relative to the mapping file. Direct paths
are relative to the repository root, including when invoked from another directory.
Books must be inside the repository and should use distinct build directories.

```sh
./scripts/docs.sh --book ar42 build
./scripts/docs.sh --book user serve
./scripts/docs.sh --docker --book architecture/book.toml build
python3 scripts/md-book/check.py --book ar42 --rendered
```

`-b` is a short alias for `--book`. The same options work with
`scripts\docs.cmd` and `python3 build.py docs`.
Use `--map path/to/books.toml` to select a different mapping file. Build, preview,
svgbob preparation, and the single-file export use the selected book's configuration
and output paths. The rendered checker accepts the same selection options.

When either tool is unavailable on `PATH`, the native mode downloads the latest stable
mdBook toolchain for the current platform. It supports Linux x86-64/ARM64, macOS Intel
(x86-64)/Apple Silicon (ARM64), and Windows x86-64. Windows uses the official `.exe`
packages. Each release asset's GitHub-provided SHA-256 digest is verified before use.

Downloads stay beneath the configured output root, separated by tool, release, and
platform. The default paths begin with `build/native-tools/mdbook/` and
`build/native-tools/mdbook-mermaid/`; Windows binaries end in `.exe`. For example,
macOS Apple Silicon uses `aarch64-apple-darwin`, and Windows x64 uses
`x86_64-pc-windows-msvc`. Nothing is installed into a user or system `bin` directory.
Commands already on `PATH` remain in use; cached commands are added only to the child
build's `PATH` so mdBook can discover its preprocessor. The runners need Python 3.11+
or Python 3.10 with `tomli`; builds also need `uv`. See the official
[mdBook releases](https://github.com/rust-lang/mdBook/releases/latest) and
[mdbook-mermaid setup](https://github.com/badboy/mdbook-mermaid#configure-your-mdbook-to-use-mdbook-mermaid).
The toolchain makes the preprocessor available. The supplied mdBook addon already
includes its configuration and browser assets. For another book without this
template, add them with `mdbook-mermaid install /path/to/book`.

For optional ASCII diagrams, uncomment this section in `book.toml`:

```toml
[preprocessor.svgbob]
command = "mdbook-svgbob"
```

The [svgbob preprocessor](https://github.com/boozook/mdbook-svgbob) renders fenced
`bob` blocks as inline SVG. With this section absent, the runner does no svgbob
setup. Native mode uses `mdbook-svgbob` on PATH first. Otherwise Docker compiles the
pinned upstream source and locked dependencies using a Rust builder, then copies
the executable into the configured output root's `native-tools/mdbook-svgbob/`
cache. No local Rust installation is needed. Subsequent runs reuse the cached
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
project directly with mdBook, provide the executable yourself; this repository's
docs runner manages the toolchain for the repository handbook.

`serve` selects an available localhost port, waits for the site to respond, and opens it
in your browser. Pass `--port 3002` to request a specific port or `--no-open` to print
the URL without opening a browser. Stop serving with Ctrl+C. The current output is
`build/book/`; changing `build-dir` to `target/book`, for example, moves HTML and
exported files there and moves the native mdBook cache under `target/`. Add any custom
generated output root to `.gitignore`. The exporter in `scripts/book-exporter/` also
reads the title, source directory, and build directory from `book.toml` and requires
Python 3.11 or newer. Markdown export has no required third-party dependencies.
For another mdBook, run it with that book's config:

```sh
uv run --no-cache --project scripts/book-exporter python scripts/book-exporter/export_book.py /path/to/book.toml
```

Use `--format typst` to generate Typst source or `--format pdf` to generate
Typst source and PDF. PDF compilation uses the optional Typst Python binding:

    uv run --extra typst-output --no-cache --project scripts/book-exporter python scripts/book-exporter/export_book.py /path/to/book.toml --format pdf

The Typst output retains local images, routes Mermaid through Merman, and renders
task lists through Cheq. See the [exporter guide](scripts/book-exporter/README.md)
for templates and supported Markdown details.

```sh
python3 scripts/md-book/check.py --rendered
python3 -m unittest discover -s tests -v
```

CLI integration tests run when `openspec` is installed; otherwise they explicitly
skip. Set `OPENSPEC_BIN=/absolute/path/to/openspec` to use an isolated installation.
They operate on temporary copies, never archive the teaching example, and never
change global OpenSpec settings. Structural checks and a rendered book do not
prove that application code implements the example: this repository contains no
equipment-lending implementation.
