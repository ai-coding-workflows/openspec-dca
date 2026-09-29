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
- `bundle/openspec/schemas/openspec-ddd/`: native schema and artifact templates.
- `bundle/openspec/ddd/`: optional read-only catalog and impact helper.
- `bundle/md-book/`: optional project architecture publishing stub.
- `templates/`: project configuration, catalog, architecture, ADR, and evidence templates.
- `scripts/`: Docker/native documentation commands, mdBook bootstrap, and exporter.
- `examples/equipment-lending/`: baseline contracts and one deliberately unfinished change.
- `tests/`: helper tests and compatibility tests against the real OpenSpec CLI.

The implementation is checked against **OpenSpec 1.13.1** (Node.js >=20.19.0).
Other releases may need adjustments; the handbook distinguishes agent commands from
terminal commands and project conventions from enforced checks.

## Install in an OpenSpec project

Initialize OpenSpec in the target project first. Then, from this repository's root:

```sh
mkdir -p /path/to/project/openspec
cp -R bundle/openspec/. /path/to/project/openspec/
```

Set `schema: openspec-ddd` in the project's `openspec/config.yaml`, preserving its
existing settings. See [the bundle README](bundle/README.md) for what was copied
and [the tooling guide](docs/09-tooling.md) for agent setup, optional templates,
and validation.

## Read and build

mdBook publishes this repository's handbook from `docs/`. Edit the Markdown chapters
and `docs/SUMMARY.md` for navigation; `book.toml` controls the build. Run `build`
for static HTML in `build/book/` or `serve` for a live local preview. The OpenSpec
bundle does not install a book in an adopting project. The separate
[mdBook addon](bundle/md-book/README.md) starts a project book that publishes its
editable `openspec/system-architecture/` entry point.

All chapters are ordinary Markdown. The shared Python runner reads the output path
from `[build].build-dir` in `book.toml`. Native mdBook is the default: it uses a command
from `PATH` or downloads the latest stable release when needed. Add `--docker` to use
the pinned mdBook 0.5.4 Docker image instead:

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

When no `mdbook` command is available on `PATH`, the native mode downloads the latest
stable release for the current platform. It supports Linux x86-64/ARM64, macOS Intel
(x86-64)/Apple Silicon (ARM64), and Windows x86-64. Windows uses the official `.exe`
package. The release asset SHA-256 digest is verified before use.

Downloads stay beneath the configured output root, separated by release and platform;
the default paths are `build/native-tools/mdbook/<target>/<version>/mdbook` on Unix-like
systems and `build/native-tools/mdbook/<target>/<version>/mdbook.exe` on Windows. For
example, macOS Apple Silicon uses `aarch64-apple-darwin`, and Windows x64 uses
`x86_64-pc-windows-msvc`. Nothing is installed into a user or system `bin` directory.
If an mdBook command already exists on `PATH`, the runner uses it without modifying it.
The runners need Python 3.11+ or Python 3.10 with `tomli`; builds also need `uv`. See
[mdBook releases](https://github.com/rust-lang/mdBook/releases/latest).

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
