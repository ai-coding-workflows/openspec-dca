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

The default command builds every valid component combination into
`build/schemas/<variant>/`, with a generated index and a separate
`legacy` variant. Repeated builds replace only verified builder-owned output.
Single selections with `--base` or `--component` require a new output directory.
DDD alone keeps models, local
architecture, and ADR guidance. `arc42` adds a system handbook; `user-doc` adds
guides, tutorials, troubleshooting, and audience-specific delivery checks. Select
either component alone or both together. Components share additive instruction and
template hooks, so user documentation can extend impact, design, tasks, and evidence
without changing the DDD base or displacing architecture guidance.

Install the chosen output as the project's `openspec/schemas/openspec-ddd/` and merge
its support guidance. This does not update an existing installation or change the
five-artifact handbook workflow described above. User-documentation drafts stay inside
the selected change; design maps them to the project's maintained destinations and
the Integration handoff tracks separate publication. Spec sync does not publish them.

The optional `architecture-reconstruction` component supplies guidance for the separate
host workflow described in adoption. Select it explicitly when that workflow is
available; arc42 alone does not include it. The component does not implement a runtime
or create additional native artifacts.

The root `build.py` dispatches to the existing tools. With no command it builds
schemas; `docs` builds the handbook, `check` runs tests and source/rendered link
checks, and `all` builds schemas and the handbook before checking. `check` requires
a built handbook and OpenSpec 1.13.1 on PATH or through `OPENSPEC_BIN`. Arguments
after `schemas` or `docs` are forwarded, including `docs --docker`. Relative paths
are resolved from the repository root.

Composition sources live under `src/schemas/`. The builder uses
Python 3.10+ without extra packages. Components provide whole blocks through artifact
instruction hooks, template hooks, shared project guidance, and a support index, plus
component-owned files and explicit dependencies. Single selections append contributions in selected order; the matrix uses a stable
dependency order and builds each valid subset once. File collisions remain errors.
The old inline replacement slots are retired.
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

The shared `scripts/docs.sh` and `scripts\docs.cmd` runners use the root
`book.toml` by default. Pass `--book` with a repository-relative book directory or
its `book.toml` (`-b` is the short alias), or define a root `docs-books.toml` mapping:

```toml
[books]
ar42 = "architecture"
user = "user-guide/book.toml"
```

These are illustrative destinations for an adopting project. Each selected book
needs its own configuration named `book.toml` and a distinct output directory.
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

Main specs receive requirement deltas during native sync/archive. The
`openspec/system-architecture/` handbook, local architecture, scoped
`architectural-decisions/` records, their handbook index, catalog changes, and other
non-spec documents remain explicit tasks. Catalog registration of a newly created
spec owner must be included in the closure review.

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
