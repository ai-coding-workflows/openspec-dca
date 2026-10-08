# Install and use the OpenSpec DDD bundle

This bundle targets ordinary repository-local OpenSpec projects. It is independent
of application language and framework. OpenSpec stores and worksets are outside this
guide's tested scope; the optional helper resolves files relative to one project root.

## Install the native integration

Install the tested OpenSpec release with Node.js 20.19.0 or newer, then initialize
your application project:

```sh
npm install --global @fission-ai/openspec@1.13.1
cd /path/to/project
openspec init --tools pi --profile core
```

For another agent, choose its native integration. OpenSpec generates Pi commands
under `.pi/prompts/opsx-*.md` and skills under `.pi/skills/openspec-*/`. The core
profile includes explore, propose, update, apply, sync, and archive. Follow the
setup output and reload your agent session if needed.

This guide uses Pi's spelling, such as `/opsx-propose`. Upstream documentation often
uses `/opsx:propose`. Always use the spelling printed for your chosen integration.
Do not copy the Pi prompt files to another agent and assume registration works.
See [upstream supported tools](https://openspec.dev/docs/supported-tools).

For optional `new`, `continue`, `ff`, and `verify` workflows, run
`openspec config profile`, select the desired workflows, then `openspec update`.
The profile preference is global to OpenSpec; it is separate from the project-local
DDD schema. Core commands are sufficient for the default workflow in this guide.

## Add the DDD schema

The handbook workflow and worked example use the retained five-artifact legacy
schema. Build the schemas, then copy that variant into the initialized project.
For the composable seven-artifact workflow, select a variant described below. Run these
commands from this guide's root, replacing the target path:

```sh
python3 build.py schemas
mkdir -p /path/to/project/openspec/schemas
cp -R build/schemas/legacy /path/to/project/openspec/schemas/openspec-ddd
```

Review and merge `templates/config.yaml` into the existing `openspec/config.yaml`.
Use `templates/openspec-README.md` for `openspec/README.md` and selected files from
`templates/system-architecture/` for `openspec/system-architecture/`; create only
useful sections. Local architecture stays with its responsible scope, including
`openspec/specs/technical-capabilities/` when applicable. Use
`templates/architectural-decision.md` for records under scoped
`architectural-decisions/` directories; the handbook's `architectural-decisions.md`
is their shared index. See the [template destination map](08-templates.md).
At minimum set `schema: openspec-ddd`. Keep existing context, rules, operation
guidance, and agent settings. Add the relevant project checks and architecture
entry points. Merge `templates/agent-instructions.md` into the project's agent
instructions so the ownership rules also apply to ordinary review/refinement requests.

Read the [architecture-view policy](04-architecture-documentation.md#architecture-views-and-diagrams)
and [template responsibilities](08-templates.md) when merging instructions. Keep
configuration rules, project agent guidance, native artifact templates, and support
templates aligned. Adopt `templates/domain-model.md` only where the model needs an
explicit companion. A new policy does not silently install a renderer, a helper
extension, a test framework, or an acceptance gate.

From the application root, verify the installation:

```sh
openspec schema which openspec-ddd
openspec schema validate openspec-ddd
openspec templates --schema openspec-ddd
```

The schema defines `proposal → impact → specs → design → tasks`. For a
contract-changing effort, Apply tracks `tasks.md` and requires all five planning
artifacts; the existing no-spec route below handles changes without behavioral
deltas. OpenSpec decides readiness from artifact existence. The prose instructions require meaningful content and review;
they are not enforced semantic gates.

For updates, diff the installed schema against this bundle and merge changes with
local customizations. Do not blindly repeat a directory copy over a customized
installation. `openspec update` refreshes native agent integrations, not this schema.

## Compose the v3 schema with optional documentation

The repository also provides a Python builder for a seven-artifact v3 schema. Its
DDD base includes explicit domain-model and architectural-decision assessments.
Optional components contribute documentation guidance and support templates:

```sh
python3 build.py schemas
python3 build.py schemas --base --output build/schema-ddd/openspec-ddd
python3 build.py schemas --component arc42 --component user-doc --output build/schema-docs/openspec-ddd
```

The default command builds four compositions (`ddd`, `ddd+arc42`, `ddd+user-doc`,
and `ddd+arc42+user-doc`) into `build/schemas/<variant>/`, with a generated index
and a separate unchanged `legacy` variant. Repeated builds replace only verified builder-owned output.
Single selections with `--base` or `--component` require a new output directory.
DDD alone keeps models, local
architecture, and ADR guidance. `arc42` adds a system handbook; `user-doc` adds
guides, tutorials, troubleshooting, and audience-specific delivery checks. Select
either component alone or both together. Components share additive instruction and
template hooks, so user documentation can extend impact, design, tasks, and evidence
without changing the DDD base or displacing architecture guidance.

Install the chosen output as the project's `openspec/schemas/openspec-ddd/`; every
composed v3 variant includes `helpers/` automatically, with no second helper copy.
Legacy remains unchanged historical five-artifact output and adds no helpers.
Review and merge its generated config, AGENTS/agent instructions, and README starters into
project-owned files, preserving customizations. This does not update an existing installation or change the
five-artifact handbook workflow described above. In the v3 schema, planning leaves maintained
sources unchanged and may prepare optional descriptive drafts inside the change. Design maps
the affected architecture/user pages, navigation, and assets to maintained destinations and
checks. Apply updates mapped descriptive sources outside `openspec/specs/**` alongside
code: the arc42 handbook at `openspec/system-architecture/`, project-root user docs, and
approved navigation/assets. Check actual maintained targets, reconcile current sources,
and preserve unrelated work; a handbook/user-doc draft alone is not delivery.

The entire `openspec/specs/**` tree remains read-only during planning and v3 Apply, whether
content is a spec, descriptive local architecture, diagram/asset, model, or index. This covers
create/edit/remove/rename and indirect/generated writes, including reference-generator or
incidental outputs. Prepare and check local-architecture proposals and source-to-maintained-target
mappings inside the change using the one Apply checklist. Actual publication and dependent
links stay in the non-checkbox Integration handoff for separately authorized sync/archive-stage
integration. Companion publication is explicit work, not automatic native sync; native sync
merges only requirement deltas, never local architecture or other non-spec documents.
Authorization for native requirement sync alone does not authorize companion publication.
Do not describe staged views as delivered/maintained-current, claim no pending publication
while it remains, or link maintained navigation to drafts/nonexistent protected targets.
Maintained model-companion, ADR-record/status/supersession, catalog, shared-store, acceptance,
and deployment protections remain in force even outside the tree. Descriptive source edits
are not acceptance or site deployment. Installing a rebuilt variant does not automatically revise an existing
project's configuration, agent instructions, or previously completed change tasks.

Architecture reconstruction remains the separate host workflow described in adoption,
not a schema component or builder selection. Selecting arc42 supplies handbook guidance,
not a reconstruction runtime.

The root `build.py` dispatches to the existing tools. With no command it builds
schemas; `docs` invokes `scripts/md-book-builder/book.py` to build selected books,
`check` runs tests and source/rendered link
checks, and `all` builds schemas and the handbook before checking. `check` requires
a built handbook and OpenSpec 1.13.1 on PATH or through `OPENSPEC_BIN`. Arguments
after `schemas` or `docs` are forwarded, including `docs --docker`. Relative paths
are resolved from the repository root.

Composition sources live under `src/schemas/`. The builder uses
Python 3.10+ and its standard library without extra packages. Components use the existing
manifest `contributions` field for whole blocks through artifact instruction hooks,
template hooks, destination-specific project guidance, operation guidance, and a support
index, plus component-owned files and explicit dependencies. Single selections append
contributions in selected order; the matrix uses stable dependency order and builds each
valid subset once. Components' optional `helpers/` directories are copied into
schema `helpers/`. Optional `helper-packs: ["docs"]` references
`src/schemas/helper-packs/docs/`, copied once per provider even when both arc42 and
user-doc select it. Distinct-provider file collisions remain errors, including
identical bytes. Only `helpers/README.md` is composed: the base README stays first,
then deterministic `Helper pack: docs`, `Component: arc42`, and `Component: user-doc`
sections for selected providers. The 22 hooks occupy 22 insertion points:
seven artifact instructions plus Apply, seven native templates plus verification,
three project destinations, two operations, and one support index.

`project.context` adds concise component facts, locations, and conventions to config
context; `project.agent-instructions` adds execution/ownership obligations to the agent
starter; `project.readme` adds a reader-friendly role/lifecycle explanation. Generic
lifecycle and protected-publication policy stays in the base, not repeated verbatim
in each component destination. `operation.apply` supplies scoped delivery/check reminders;
`operation.archive` confirms maintained targets, durable links, checks, and explicit
remaining deferrals/status. Native sync does not publish documentation.

Ordinary project/artifact hooks render prose with spacing and indentation. Each operation
fragment instead contains one nonempty plain prose item, possibly multiline: the safe
renderer quotes it as a YAML string and supplies indentation and the list marker.
YAML-looking text remains literal prose, not YAML structure. Do not author YAML structure,
nested hook markers, or new OpenSpec fields; hooks cannot inject arbitrary YAML,
introduce native artifacts/dependencies, or edit upstream prompts.

The old inline replacement slots and `project-guidance` hook are retired. Repository-owned
manifests migrate atomically with no compatibility alias. Unknown-hook failures direct
custom component authors to `project.context`, `project.agent-instructions`, and
`project.readme`; split existing guidance by destination and add scoped operation items,
retaining native instruction/template/support-index contributions. See the builder README
for a concrete manifest example. Generated starters still require reviewed installation
merges, not automatic replacement of project-owned customizations.
See the builder README at `scripts/schema-builder/README.md` for authoring and migration instructions. Required
checks validate components alone and in combination with real OpenSpec, including
their contributed instructions and the native lifecycle.

## Optional ASCII diagrams

The handbook runner also supports the optional
[svgbob preprocessor](https://github.com/boozook/mdbook-svgbob) for ASCII diagrams
in fenced `bob` blocks. Enable `[preprocessor.svgbob]` in `book.toml` or set
`svgbob = true` in the selected `[books.alias]`; otherwise absent native tables
need no svgbob tooling. The runner uses a native executable on PATH or builds
the pinned source in a temporary Rust Docker container and caches the executable
under `<builder>/.cache/native-tools/` beside the actual `book.py`. The script-local `.gitignore`
excludes this shared cache, independently of each book's output directory.
It removes the builder container and image even
when compilation fails. Linux and Windows host builds are supported; native macOS
requires a locally installed binary, while Docker documentation mode uses Linux
on every supported host. The repository's root `README.md` describes configuration,
platform limits, and cache details. Each `[books.alias]` accepts optional `mermaid`
and `svgbob` booleans: omitted autodetects native preprocessor tables; `true`
provisions missing standard preprocessors; `false` disables managed setup but never
erases author configuration. Custom commands are preserved and remain author-managed;
no competing standard binary is provisioned.

Managed setup permanently adds missing standard preprocessor tables and Mermaid
`additional-js` cache references to the native configuration. Valid author scripts,
custom commands, and comments survive; unsupported impacted inline/dotted TOML
forms error before writes. Mermaid assets are extracted with the chosen binary's
`install` command only in a scratch mini-book and hash-checked under
`<builder>/.cache/scripts/mermaid/<identity>/`. Docker uses the actual pinned image
binary, not a host binary. Owned references refresh per binary identity; missing
standard-filename references can be repaired, but existing author assets stay untouched.
Staged native/Docker builds preserve original configuration-directory path semantics
with runtime asset overrides. Maintained Markdown stays unchanged; review durable
configuration changes. The addon does not vendor JavaScript: raw `mdbook build`
users must intentionally run `mdbook-mermaid install /path/to/project`, whereas the
reusable builder provisions managed assets automatically.

## Select a documentation book

The canonical runners are `scripts/book.sh`, `scripts\book.cmd`, and
`python3 scripts/md-book-builder/book.py build|serve|export`. See the canonical
builder guide at `scripts/book.md`. An adopting project may place the builder
anywhere inside its root; resources, caches, and the PDF environment stay relative
to the actual `book.py` directory. `--root` explicitly selects the project. Without
it, discovery searches the nearest CWD ancestor containing `book-builder.toml` or
`book.toml`, then the builder's ancestors. For example:

```sh
python3 /project/tools/documentation/md-book-builder/book.py --root /project build
BOOK_BUILDER=/project/tools/documentation/md-book-builder/book.py ./scripts/book.sh build
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
```

Starters use `BOOK_BUILDER` as the actual `book.py` path; `docs-check.py --builder`
selects that file explicitly. No fixed `scripts/` layout is required.
Root `book-builder.toml`, when present, supplies
an authoritative books list. This repository selects its existing handbook:

```toml
[books.handbook]
config = 'book.toml'
export-formats = ['markdown']
serve = true
```

Without a builder configuration, discovery selects root `book.toml` and root-level
`book.*.toml`, without recursing. For a fictional adopting project with separate
architecture and user books, create the configurations before using entries such as:

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

Defaults are `export-formats = ['markdown']` and `serve = true`. Each `[books.alias]`
can list `markdown`, `typst`, or `pdf`; duplicates are removed while retaining order.
The legacy `export-format = 'markdown'` remains supported. Specifying both fields
or an empty list is invalid. Builds and exports process all selected books;
automatic previews include only `serve = true` entries on separate ports and stop
together with Ctrl-C. `--port` sets the first port.

`--book` (or `-b`) explicitly selects an alias or repository-relative directory or
configuration file and bypasses the serve flag. Directories use `book.toml`.
An unlisted explicit path is allowed with defaults; a matching configured path
inherits its options. `--config PATH` selects another builder configuration;
`--map` remains a compatibility alias. Configured book paths resolve relative to
that file; direct paths resolve relative to the repository root and must stay
inside it. Custom root tables and per-book metadata may be ignored. There is no
builder configuration template option in this version. mdBook never sees the
builder configuration; `book.toml` remains native mdBook TOML.

Alternate configurations use temporary symlinked mdBook roots without replacing
original files. Windows may require Developer Mode or elevated privileges. Batch
commands require non-overlapping build paths.

```sh
./scripts/book.sh --book handbook build
./scripts/book.sh --docker --book handbook build
./scripts/book.sh export
python3 scripts/md-book-builder/book.py --book handbook build --format markdown --format pdf --template templates/custom.typ
python3 scripts/md-book-builder/check.py --config book-builder.toml --book handbook --rendered
```

These options pass through `build.py docs`. The checker remains single-book,
defaulting to root `book.toml`; select additional books explicitly with `--book`.
It accepts `--config` and the compatibility `--map` alias.

`build` captures preprocessing separately, builds HTML once per selected book,
and runs its configured formats in order; `export` captures preprocessing and runs
only the exports, without building or replacing HTML. Both accept repeated
`--format markdown|typst|pdf` options to replace, not append to, the configured list.
Duplicates are removed in order. If one format fails, remaining formats still run
and the command exits nonzero. PDF also emits `.typ`; selecting Typst and PDF still
runs both exports. Optional `--template PATH` supplies the same argument to every
selected book and format. Relative CLI template paths resolve against each selected
book configuration's directory, not the builder configuration directory.
Markdown/Typst rendering uses the host Python 3.11+ standard library, or Python
3.10 with `tomli`, without creating virtual environments; no `uv`. Common exports
also require the native mdBook toolchain (downloaded/cached when missing) or Docker.

All common CLI build/export outputs use mdBook's actual preprocessing pipeline,
not an `export = true` opt-in. A temporary `book-export` backend selected via
`MDBOOK_OUTPUT` captures the full JSON RenderContext in an isolated temporary
destination. One capture per selected book is reused across formats and normally
cleaned up. Export leaves existing HTML output and maintained Markdown untouched;
managed diagram setup may permanently update native configuration before capture.
Source/output paths still come from native book config.

Native mdBook ordering and renderer gating apply, including `supports book-export`
and configured `renderers` lists. Custom preprocessors must support this backend.
`export = true` is not a universal mdBook option or export filter. Captured Markdown
need not exactly match HTML-processed Markdown: HTML-only Mermaid preprocessing is
skipped, leaving raw fences for the Typst converter. Generated nested chapters are
included even without source files. Generator-specific behavior remains in user
preprocessors; the reusable tool has no built-in ADR logic. The supported converter
subset still applies, not arbitrary HTML-to-Typst conversion.

`--docker export` is supported: preprocessing capture runs inside the pinned
container, while host exporters render formats and PDF uses its host managed
environment.

For PDF, use automatic dependency setup through the common CLI:

```sh
./scripts/book.sh export --format pdf
./scripts/book.sh export --format pdf --no-install
```

`book.py` and `book.sh`/`book.cmd` exclusively use a
builder-managed PDF environment beneath `<builder>/.venv/` beside the actual `book.py`,
partitioned by Python interpreter, runtime, and requirements. On demand,
standard-library `venv` and pip install pinned `typst==0.15.0`, plus `tomli==2.2.1`
on Python <3.11. Validated, complete environments are reused. Global Python and
existing project virtual environments are never modified, and global `typst` is
never used for PDF.

`--no-install` disables creation/installation, not reuse of a valid managed
environment. If none is ready, PDF fails while other formats are still attempted.
First installation needs network access and `venv`/`ensurepip`; missing OS packages
such as `python3-venv` are never installed automatically. Install that support
yourself or use the manual standalone exporter as a fallback. First PDF compilation
may also need Typst registry access for Merman (Mermaid) and Cheq (task lists);
cached/offline use requires those packages and the toolchain to be available too.
`--no-install` is not a general offline switch: it does not disable mdBook downloads
or Typst registry network access.
The bundle-local `scripts/md-book-builder/.gitignore` excludes `__pycache__/`,
`*.py[cod]`, and `.venv/`; the repository's root ignore rules also cover the cache
directories.

For a standalone book, use the canonical exporter directly. Unlike integrated
`book.py`, `export_book.py` accepts one format per invocation and defaults to
Markdown. Its default mode reads raw SUMMARY/source/includes without running
mdBook; optional `--render-context PATH` consumes a captured full JSON RenderContext
instead (common CLI temporary captures are normally cleaned up). It uses the
invoking interpreter and never installs dependencies:

```sh
python3 scripts/md-book-builder/exporter/export_book.py book.toml --format typst
```

See the exporter guide at `scripts/md-book-builder/exporter/README.md` for manual
standalone PDF setup, templates, and details.

## Optional catalog and helper

Composed v3 schemas already install the canonical DDD helpers under
`openspec/schemas/openspec-ddd/helpers/`. Start a catalog only when the ownership
graph is useful; using the helpers is optional. For the retained legacy schema,
helpers are not automatically added. From this guide's root, optionally copy them
separately after installing legacy:

```sh
cp -R src/schemas/ddd/helpers /path/to/project/openspec/schemas/openspec-ddd/helpers
```

The older `openspec/ddd/` location remains a supported fallback, not the primary
installation recommendation.

Use `templates/catalog.json` as the starting shape for `openspec/catalog.json`, or
adapt the example catalog. Do not replace an existing catalog with the empty template.
An entry has a stable alias, a main spec path, and consumed owner IDs:

```json
{
  "id": "lending.return",
  "kind": "feature",
  "path": "openspec/specs/contexts/lending/features/return-equipment/spec.md",
  "depends_on": ["lending.domain", "lending.loan-store"],
  "architecture": ["openspec/specs/contexts/lending/features/return-equipment/architecture/runtime.md"]
}
```

All referenced owners must exist in the catalog. Paths are project-relative existing
files. Optional `contracts`, `architecture`, and `decisions` arrays identify additional
context explicitly. A `domain/model.md` companion remains documentation owned by its
main spec owner; it does not create another capability or catalog node, and native spec
sync does not update it. New proposed owners remain in `impact.md` until main specs exist.

Keep the catalog schema and field names unchanged. In particular, `decisions` remains
the path-reference field even though record directories are named
`architectural-decisions/`; update path values, not the field name. New technical
capability paths use `openspec/specs/technical-capabilities/`, without introducing
new catalog fields or changing the meaning of `depends_on`.

The catalog is not the handbook's table of contents. Architecture-only scopes can
appear in `openspec/system-architecture/` navigation without a catalog entry. Do not
create dummy specs for them. If no main specs exist and there is no existing catalog
to preserve or reconcile, the empty shape in `templates/catalog.json` is sufficient.

From the application root:

```sh
python3 openspec/schemas/openspec-ddd/helpers/ddd.py check
python3 openspec/schemas/openspec-ddd/helpers/ddd.py context lending.return
python3 openspec/schemas/openspec-ddd/helpers/ddd.py impact lending.domain
```

All three commands are read-only and return JSON. Python 3.10+ is sufficient, without
extra packages. Use `--root /path/to/project` before the subcommand when running from
elsewhere. Shared standard-library `project_root.py` resolves the default root
from the helpers' nearest `openspec` ancestor to its project parent, not a fixed
installation depth. `context` lists prerequisites first and includes explicit architecture/ADR
references. `impact` lists transitive consumers for review, not an edit instruction.

`check` rejects invalid references, duplicate IDs/paths, and dependency cycles, and
reports main specs missing from the catalog. It does not validate actual architecture,
discover external callers, or evaluate proposed deltas. OpenSpec handles change and
spec validation; the helper supplies only the additional DDD graph.

### Optional documentation and ADR checks

The separate `openspec/schemas/openspec-ddd/helpers/check.py` validates optional
catalog and individual ADR metadata without requiring arc42, mdBook, or a catalog owner for every architecture
scope. Missing optional metadata is explicitly reported as skipped. It checks the
bundle's prose ADR ID/title, nonempty Status/Date/Scope fields, scoped duplicate IDs,
and existing local supersession references. Status vocabulary is project-defined;
unknown dates and human/system scopes remain valid. No approval or lifecycle
transition is inferred. See the helper README at `src/schemas/ddd/helpers/README.md`.
Run from the application root:

```sh
python3 openspec/schemas/openspec-ddd/helpers/check.py --root .
python3 openspec/schemas/openspec-ddd/helpers/check.py --decisions architectural-decisions --status Proposed --status Accepted
```

Every composed variant also includes `model.py`, the canonical read-only ADR reader.
Its frozen `AdrRecord` preserves exact original `text` and project-relative `path`,
with optional ID/title and Status/Date/Scope values plus all metadata values through
`field_values(name)`. Recognition uses only `# ADR-id: title` and plain metadata
fields, ignoring comments and fenced/indented code; legacy bold metadata, em-dash
headings, and alternative `decisions/` discovery are not supported. Incomplete fields
are retained for diagnostics. Parsing does not check required fields, supersession
file existence, status vocabulary, date format, scope ownership, uniqueness, or approval.

A project renderer can read once with `model.decisions(root)` and explicitly call
`check.validate_decisions(root, records)` before rendering `record.text`. Validation
returns the existing CLI metadata shape without original text and checks required
fields, scoped duplicate IDs, local supersession files, and a selected status
allowlist. `model.read_adr(path, root)` reads one record. See the API usage example
in `src/schemas/ddd/helpers/README.md`.
Grouping/navigation and stricter checks (global IDs, ISO dates, scope/catalog
ownership, full catalog coverage, and spec-ID comments) remain project-specific.
Catalog/graph logic stays in `ddd.py`; `model.py` has no catalog dependency or copy.
Rendering introduces no second lifecycle, and changing adopted ADR source formats
requires explicit project-owned migration, not automatic helper rewriting.

### Optional generated ADR book view

For a general directory-grouped view, enable the distributed helper explicitly in
one native book configuration (use the actual installed schema name):

```toml
[preprocessor.adr]
command = "python3 openspec/schemas/openspec-ddd/helpers/adr-preprocessor.py"
```

Add `{{#adr-index}}` exactly once to a dedicated chapter listed in `SUMMARY.md`.
The helper reads canonical maintained ADRs, validates the same loaded records, and
adds an index, virtual grouped pages, navigation, and stable ID-derived anchors.
No catalog is required. It does not add catalog-only references or scan proposed
changes and archives. No marker means no ADR scan or book modification.

Grouping follows source directories, without project-specific labels or compulsory
catalog ownership. IDs can repeat on separate pages; anchor collisions on one page,
multiple markers, and generated-path collisions are errors. An anchor is stable for
an unchanged ID; moving the source directory or host chapter changes its page URL.

Original ADRs remain the only maintained records; the view writes no source pages
and is not a substitute for the durable architecture index. Local links between
selected ADRs are rebased to generated pages; other local Markdown links/images must
refer to existing book-source files. Unsupported outside-book resources fail rather
than being silently copied. See `src/schemas/ddd/helpers/README.md` for limitations.
The helper supports HTML and native-preprocessed `book-export` output. It stays in
the schema helpers; the generic builder contains no ADR generator.

Both arc42 and user-doc install generic `helpers/docs-check.py` from the single
canonical thin orchestrator at `src/schemas/helper-packs/docs/docs-check.py`, not an
arc42-conformance checker.
The installed orchestrator uses adjacent `check.py` through the existing
`check_project` API for DDD metadata and delegates
generic source/include/HTML validation and builds to a separately installed
`md-book-builder`. Select its actual `book.py` with `--builder` or `BOOK_BUILDER`;
`<root>/scripts/md-book-builder/book.py` is convenience discovery only. The builder
may live in arbitrary folders and contains no DDD validation. From the project root:

```sh
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
```

Use `--ddd-helper PATH` for an alternate metadata checker, including when several
installed schemas are ambiguous. The orchestrator checks DDD metadata and
configured book sources, builds selected books, then checks local HTML links and
anchors. It uses each native `[book].src`, with repeated `--source` for additional
folders, rather than fixed arc42/user-doc paths. `--source-only` skips rendering;
`--openspec` adds native `openspec validate --all --strict --no-interactive`. No
`change.json` or parallel change-status model is introduced. Books without DDD
metadata and DDD projects without books are supported, with absent stages reported
as skipped. Install the optional helper when metadata is present, or explicitly
choose `--skip-ddd`. Ordinary `book.sh`/`book.cmd` operations remain DDD-independent.
The low-level `scripts/md-book-builder/check.py --rendered` only checks
already built HTML; it does not build or validate DDD metadata. See the
book builder guide at `scripts/book.md` for commands.
These checks do not evaluate external URLs, code conformance, architecture
correctness, decision authority, or delivery acceptance.

The helper does not implement the optional requirement-to-test traceability convention
described in the [workflow guide](05-change-workflow.md). A manifest is not required:
start with useful code-entry-point and evidence links. Any adopted manifest is project-owned
and does not change `depends_on`, catalog validation, or OpenSpec acceptance behavior.

## Pass a spec or a change

For a new effort, give the agent the outcome plus a catalog alias or main spec path:

```text
/opsx-propose record-return-condition: Start from lending.return.
Record the condition of each new return.
```

The same request can use the exact file path:

```text
/opsx-propose record-return-condition: Start from
openspec/specs/contexts/lending/features/return-equipment/spec.md.
Record the condition of each new return.
```

The agent resolves this free text using the catalog and actual specs. Naming the
starting owner is enough; the impact review discovers necessary related work.
You can name several owners if you already know them. An agent's file mention is
also suitable when it makes the actual file available.

Once the change exists, pass its **change name** to follow-up commands:

```text
/opsx-update record-return-condition: Reconcile the compatibility decision.
/opsx-apply record-return-condition
```

Native terminal commands use different arguments:

```sh
# OpenSpec capability path, not the DDD alias or full spec.md path:
openspec show contexts/lending/features/return-equipment --type spec

# Change name, not its directory or a spec ID:
openspec status --change record-return-condition

# The optional DDD helper resolves both aliases and main spec paths:
python3 openspec/schemas/openspec-ddd/helpers/ddd.py context openspec/specs/contexts/lending/features/return-equipment/spec.md
```

There is no additional saved DDD selection. Use explicit change names when several
efforts are active. Archived changes are history; later work starts a new change.

## Find open steps and tasks

Use native commands from the application root:

```sh
openspec list
openspec status --all
openspec status --change record-return-condition --json
openspec instructions apply --change record-return-condition --json
```

`list` shows active changes and task progress. `status --all` shows their artifact
readiness. Per-change apply instructions report `state`, `progress`, individual
`tasks` with a `done` flag, and missing required artifacts. This command only prints
instructions; it does not execute implementation work. JSON is available for an
agent or another reporting tool to aggregate all active changes.

The teaching example has `isPlanningComplete: true` but seven pending tasks. Missing
artifacts, absent/empty tasks, or unfinished tasks require different next actions.
Even `state: all_done` means tracked tasks are checked, not that acceptance is proven.
Native status does not infer stale designs, unresolved prose questions, unrecorded
review findings, missing delta coverage, or test failures. Ask for a consistency
review and inspect `verification.md` for those concerns.

## Validation and closure

```sh
openspec validate --all --strict --no-interactive
```

Run this structural check alongside the adopting project's actual tests and
documentation checks. A docs-only or refactoring change with no behavioral change
sets `skip_specs: true` in its `.openspec.yaml`; the specs artifact is skipped while
impact, design, tasks, and verification still describe the actual work. Never use
this flag to hide a genuine behavior change or leave delta files beside it.

Main specs receive requirement deltas during native sync/archive. The retained legacy
workflow tracks other architecture/decision/catalog/documentation updates explicitly.
In v3, mapped handbook/user pages and approved navigation/assets outside `openspec/specs/**`
are actual maintained-source Apply tasks. Local architecture and all other content inside
that protected tree remain read-only through planning and Apply: prepare/check proposals and
mappings inside the change in the one Apply checklist, then publish explicitly only at
separately authorized sync/archive-stage integration through the non-checkbox handoff.
Protected model/ADR/catalog publication and dependent links also remain in that handoff,
even outside the tree. Native sync merges only requirement deltas; neither workflow's spec
sync automatically publishes companions, local architecture, or other non-spec documents.
Catalog registration of a newly created spec owner requires its actual main spec and must
be included in the closure review.

Documentation checks should distinguish source/link/rendering success from semantic
review of the actual architecture. Record the checked revision and unavailable or
unexecuted checks accurately; publication success does not establish requirement
conformance. Before acceptance, review the relevant maintained views, actual ADR
status, and any evidence affected by later changes. No fixed diagram count or
universal code-coverage percentage follows from this bundle.

The internal architecture-only brownfield route is separate from a native
`skip_specs` change. It uses its approved runtime checklist and review evidence and
does not create `.openspec.yaml`, change artifacts, specs, or needs simply to make
architecture documentation discoverable. See [adoption](07-adoption.md).

The guide's integration tests check the supported CLI version, nested spec discovery
and merge, native Pi generation, artifact readiness, the no-spec route, and the
difference between planning completion and remaining tasks. They do not invoke a
language model or certify the quality of its generated artifacts.
