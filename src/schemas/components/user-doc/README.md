# Optional user-documentation component

This component follows the existing component manifest and additive-hook model.
Select `user-doc` when composing the DDD schema with the project's builder.
It has no required component: DDD alone, DDD + arc42, DDD + user-doc, and
DDD + both are valid intended selections. The seven artifacts and their dependencies
stay in the DDD foundation. Disabling arc42 does not disable user-documentation.

The directory's presence makes it available, not enabled. Only explicit builder
selection injects its guidance and copies its support templates. No native `enabled`
flag, project-config extension key, or component runtime is introduced. Follow the
existing builder's CLI rather than an invented command in this package.

## What it contributes

| Contribution | Responsibility |
| --- | --- |
| Project context | Selected documentation root and component-specific locations/conventions |
| Project agent instructions | Reader-oriented execution, ownership, safe checks, and pending durable links |
| Project README | Reader-friendly component role and planning/delivery lifecycle |
| Apply/archive operation guidance | Scoped delivery/check reminders and maintained-target/link closure review |
| Proposal instructions | Reader groups and likely visible effects |
| Impact instructions/template | User task and page coverage; a reasoned no-impact result is valid |
| Specs instructions | Preserve actual documentation obligations without creating one per page |
| Design instructions/template | Reader-oriented structure, exact page/asset mapping, proposed checks |
| Tasks instructions/template | Maintained edits/checks in one checklist; separate work only in handoff |
| Apply instructions | Update mapped maintained pages in development; preserve unrelated edits |
| Verification template | Actual maintained results, examples, navigation/procedure checks and gaps |
| Support index and files | Six optional page-writing starters under templates/user-documentation/ |

The domain-model and architectural-decisions artifacts remain the sources of model
meaning and significant decision rationale. They do not need another user-doc assessment
or repeated definitions. The component uses the existing scopes and generic hooks only.

## Files versus content

Builder output places starters at:
`openspec/schemas/openspec-ddd/templates/user-documentation/`.
That is the template library, not the handover of a complete handbook.

Real maintained pages belong at `user-documentation/` in the project root unless project
instructions/design explicitly select an existing root; that choice wins without migration.
Planning remains change-local and read-only at maintained destinations. Optional drafts may
live at `openspec/changes/<change>/user-documentation/`; no second editable copy is required.
Apply updates explicitly mapped descriptive pages, navigation, assets, and approved reference
sources in the repo-local development checkout alongside code. Read current destinations,
reconcile concurrent edits, preserve dirty/unrelated content, and check actual results,
including additions, deletions, and renames. A draft alone does not complete a task.

The entire `openspec/specs/**` tree is read-only during planning and Apply, including local
architecture, diagrams/assets, models, and indexes: no direct or generated create/edit/remove/
rename. Prepare/check protected proposals and source-to-maintained-target mappings inside the
change in the one Apply checklist; actual publication and dependent links are non-checkbox
handoff work at separately authorized sync/archive-stage integration. Native sync merges only
requirement deltas, never local architecture or other non-spec documents automatically.
Maintained model companions, ADR records/status/supersession and `openspec/catalog.json`
remain protected/separate even outside the tree. References requiring absent protected
targets go to the non-checkbox Integration Handoff, not placeholders or maintained links to
transient drafts. Handoff covers protected-tree publication/dependent links and remaining
separate contract/model/ADR/catalog/release work; do not invent Pending publication for
ordinary completed docs outside the tree, or claim none while publication remains pending.
Staged local views are not delivered or maintained-current. Task completion is not
acceptance, release, or site deployment. Direct shared canonical store writes and deployment
remain outside Apply permission. Generated references use only existing approved generator/
source/output mappings with incidental outputs inspected; forbid generators/incidental
outputs that write into `openspec/specs/**`. Introduce no tools or services to
pass checks.

All new public pages must answer a reader question. A change with no documentation
impact can use a short reason in impact and omit empty downstream tables. User pages
are not native spec owners, and their references are not contract dependency edges.
Accepted documentation requirements remain binding whether or not this optional
component is selected; component selection is not a waiver mechanism.

## Scope of this update

This addition handles the DDD process and optional writing support first. It does
not change arc42, architecture reconstruction, the native artifact graph, existing
review outcomes, or the builder. It installs no publisher, linter, automatic splitter,
CI workflow, reference generator, new handbook baseline, or user-doc reconstruction
process. Selecting a component is not permission to rewrite installed project guidance.
Review and merge generated config, agent-instruction, and README starters into active
project-owned files deliberately, preserving customizations.

See [the template guide](files/templates/user-documentation/README.md) for writing and
verification rules. See the [builder README](../../../../scripts/schema-builder/README.md) for composition,
destination-specific hooks, custom component migration, and integration checks.
