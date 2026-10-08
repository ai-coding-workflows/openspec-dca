# Schema builder concept

The builder composes a DDD foundation with optional components into one native
OpenSpec schema. Components add guidance and support templates for concerns such
as architecture or user documentation. The foundation exposes general extension
points so each new concern can participate in the existing workflow.

## Foundation, components, and output

- `ddd/files/` owns the seven native artifacts, their dependencies, DDD conventions,
  and the boundaries between planning, implementation, verification, and publication.
- `components/<name>/component.json` declares a component's description, required
  components, and contributions. `fragments/` holds guidance blocks; `files/` holds
  additional output files such as support templates. Optional `helpers/` holds
  component helpers; optional `helper-packs: ["docs"]` selects the shared provider
  at `src/schemas/helper-packs/docs/`.
- `ddd/helpers/` owns canonical `ddd.py`, `check.py`, and shared standard-library
  `project_root.py`; every composed v3 schema includes them automatically.
- The builder combines these sources into a new directory containing `schema.yaml`,
  `templates/`, and `helpers/`. Installing the chosen schema needs no second helper
  copy. Generated output is an installation artifact; edits belong in
  the sources. Updating a customized installation still requires a reviewed merge of
  generated config, AGENTS/agent instructions, and README into project-owned files,
  preserving customizations. Python 3.10+ and its standard library are sufficient.

The matrix contains four compositions: `ddd`, `ddd+arc42`, `ddd+user-doc`, and
`ddd+arc42+user-doc`, plus unchanged `legacy`. Architecture reconstruction remains
a separate host workflow, not a schema component or builder selection. Legacy is
historical five-artifact output with no automatically added helpers; optionally
copy the canonical DDD helper directory separately for a legacy installation.

## Shared, additive hooks

A hook is a marker on its own line, such as `{{hook:instructions.impact}}`.
Components use the existing manifest `contributions` field through five hook families,
with 22 named hooks and 22 insertion points: 8 instructions (seven artifacts plus
Apply), 8 templates (seven artifacts plus verification), 3 project destinations,
2 operation destinations, and 1 support index.

| Hook family | Purpose |
| --- | --- |
| `instructions.*` | Extend native artifact and Apply instructions |
| `template.*` | Extend artifact templates and the verification support template |
| `project.context` | Concise component project facts, locations, and conventions in config context |
| `project.agent-instructions` | Component execution and ownership obligations in agent guidance |
| `project.readme` | Reader-friendly role and lifecycle in the project README starter |
| `operation.apply`, `operation.archive` | Scoped config operation guidance, one safe prose item per fragment |
| `support-index` | Describe and link component-owned support templates |

Several components may use the same hook. Their blocks append in the selected
component order, preserving the base guidance and each other's contributions. The
matrix uses stable dependency order. The ordinary prose renderer handles spacing and
embedding indentation; unused hooks disappear. Operation hooks instead quote each
nonempty plain prose fragment as one YAML string item and supply its list marker.
Fragments may be multiline; YAML-looking text is always literal string content,
not a list, mapping, tag, or new OpenSpec field. Do not author YAML structure or
nested hook markers. No arbitrary YAML insertion is supported.
This avoids architecture-specific word substitutions and lets components own
complete, readable explanations. Split project content by destination rather than
copying full policy into all three. Generic lifecycle and protected-publication
contracts stay in the base; components add scoped reminders. The old `project-guidance`
hook has no compatibility alias. Repository-owned manifests migrate atomically;
unknown-hook failures direct custom authors to `project.context`,
`project.agent-instructions`, and `project.readme`. Add operation items separately
and retain native instruction, template, and support-index contributions.

For example, arc42 can contribute handbook impact guidance. A user-documentation
component could use the same impact hook to identify affected audiences and
procedures, then contribute drafting tasks and verification guidance. Its guide
templates would live in its own `files/` directory. Adding this concern needs no
new architecture slots or changes to the base artifact graph.

## Composition boundaries

Dependencies must be explicitly selected before their consumers. Shared hooks are
allowed; overlapping output files, unknown hooks, and invalid source paths are
errors, even when distinct providers supply identical file bytes. A shared helper
pack is copied once per provider, including when arc42 and user-doc both select
`docs`. The sole collision exception is `helpers/README.md`: the base README stays
first, followed by deterministic `Helper pack: docs` and selected `Component: arc42`
and `Component: user-doc` sections. Selection order determines presentation, not
which conflicting policy wins; combined guidance still needs review.

Both documentation components distribute generic `docs-check.py`, not an
arc42-conformance checker. This single thin orchestrator lives in
`src/schemas/helper-packs/docs/docs-check.py`, installed as
`openspec/schemas/openspec-ddd/helpers/docs-check.py`.
It uses adjacent `check.py` for optional DDD metadata; `--ddd-helper`
selects an alternate checker if multiple installed schemas are ambiguous. Generic
source/include/HTML validation and book building remain in the separately installed
`md-book-builder`, selected via `--builder` or `BOOK_BUILDER`; conventional
`<root>/scripts/md-book-builder/book.py` is only convenience discovery. The builder
may live in arbitrary folders and contains no DDD validation.

Installed DDD helpers resolve the project through the nearest `openspec` ancestor
and its parent using shared `project_root.py`, rather than fixed directory depth.
Commands and explicit `--root` remain unchanged; the primary installed path is
`openspec/schemas/openspec-ddd/helpers/`, with `openspec/ddd/` supported as fallback.

Hooks extend prose and templates. They do not add native artifacts, alter their
dependencies, or replace OpenSpec's generated agent integrations. New artifact
types would require a separate, explicit composition design.

Planning remains change-local, optionally with descriptive drafts. Apply updates actual
mapped descriptive targets outside `openspec/specs/**` (the arc42 handbook at
`openspec/system-architecture/`, project-root user docs, approved navigation/assets),
reconciling current sources, preserving unrelated work, and checking maintained results.
The entire `openspec/specs/**` tree is read-only during planning and Apply, including specs,
local architecture, diagrams/assets, models, and indexes: no create/edit/remove/rename or
indirect/generated writes. Prepare/check local-view proposals and source-to-maintained-target
mappings inside the change using the one Apply checklist. Actual protected publication and
dependent links stay in the non-checkbox Integration handoff for separately authorized
sync/archive-stage integration. Companion publication is explicit work, not automatic native
sync; sync merges only requirement deltas, never local architecture or other non-spec documents.
Staged views are not delivered/maintained-current; do not conceal pending publication or
link maintained navigation to drafts/nonexistent targets. Model-companion, ADR record/status,
catalog, shared-store, acceptance, and deployment protections remain in force outside the tree.
Apply reminders concern scoped delivery and preparation/checks; archive reminders confirm
actual maintained targets, links, checks, and explicit deferrals/status.

Artifact readiness, task completion, verified delivery, acceptance, and publication remain
distinct. Support templates do not become mandatory artifacts, and native spec sync
does not publish architecture or other documentation. Validate composed variants
with the real OpenSpec CLI as well as builder tests.

See the [builder README](README.md) for commands, manifest
examples, and migration details.
