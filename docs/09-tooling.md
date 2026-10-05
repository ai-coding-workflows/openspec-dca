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

Install the chosen output as the project's `openspec/schemas/openspec-ddd/` and review
and merge its generated config, AGENTS/agent instructions, and README starters into
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
schemas; `docs` builds the handbook, `check` runs tests and source/rendered link
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
valid subset once. File collisions remain errors. The 22 hooks occupy 22 insertion points:
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
in fenced `bob` blocks. Enable `[preprocessor.svgbob]` in `book.toml`; otherwise no
svgbob tooling is prepared. The runner uses a native executable on PATH or builds
the pinned source in a temporary Rust Docker container and caches the executable
under the configured output root. It removes the builder container and image even
when compilation fails. Linux and Windows host builds are supported; native macOS
requires a locally installed binary, while Docker documentation mode uses Linux
on every supported host. The repository's root `README.md` describes configuration,
platform limits, and cache details.

## Select a documentation book

The shared `scripts/docs.sh` and `scripts\docs.cmd` runners discover root
`book.toml` plus root-level `*.book.toml` by default, without recursing. Builds
process every discovered book; previews serve all books on separate ports and stop
them together with Ctrl-C. `--port` sets the first port; others use available ports.
Pass `--book` to select just one repository-relative book directory or configuration
file (`-b` is the short alias), or define a root `docs-books.toml` mapping:

```toml
[books]
ar42 = "architecture"
user = "user-guide/book.toml"
```

These are illustrative destinations for an adopting project. Directory selections
use `book.toml`; explicit files and aliases can also select `*.book.toml`.
Alternate configurations use temporary symlinked mdBook roots without replacing
original files; the host must allow symlink creation (Windows may require Developer
Mode or elevated privileges). Batch commands require non-overlapping build paths,
such as `build/book` and `build/user`.
Alias paths resolve relative to the mapping file; direct paths resolve relative to
the repository root. Use `--map` to choose another mapping file. Selected books must
remain inside the repository.

```sh
./scripts/docs.sh --book ar42 build
./scripts/docs.sh --book user serve
./scripts/docs.sh --docker --book ar42 build
python3 scripts/md-book/check.py --book ar42 --rendered
```

Both native and Docker builds, previews, optional svgbob preparation, and exports
use the selected configuration. These options also pass through `build.py docs`.
The rendered checker remains single-book: it defaults to root `book.toml`; select
each additional book explicitly with `--book`.

## Optional catalog and helper

Copy the helper and start a catalog only when the ownership graph is useful:

```sh
cp -R src/helpers/ddd /path/to/project/openspec/
```

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
python3 openspec/ddd/ddd.py check
python3 openspec/ddd/ddd.py context lending.return
python3 openspec/ddd/ddd.py impact lending.domain
```

All three commands are read-only and return JSON. Python 3.10+ is sufficient, without
extra packages. Use `--root /path/to/project` before the subcommand when running from
elsewhere. `context` lists prerequisites first and includes explicit architecture/ADR
references. `impact` lists transitive consumers for review, not an edit instruction.

`check` rejects invalid references, duplicate IDs/paths, and dependency cycles, and
reports main specs missing from the catalog. It does not validate actual architecture,
discover external callers, or evaluate proposed deltas. OpenSpec handles change and
spec validation; the helper supplies only the additional DDD graph.

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
python3 openspec/ddd/ddd.py context openspec/specs/contexts/lending/features/return-equipment/spec.md
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
