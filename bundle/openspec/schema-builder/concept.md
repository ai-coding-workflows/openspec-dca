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
  additional output files such as support templates.
- The builder combines these sources into a new directory containing `schema.yaml`
  and `templates/`. Generated output is an installation artifact; edits belong in
  the sources. Updating a customized installation still requires a deliberate merge.

## Shared, additive hooks

A hook is a marker on its own line, such as `{{hook:instructions.impact}}`.
Components contribute complete paragraphs or sections through four hook families:

| Hook family | Purpose |
| --- | --- |
| `instructions.*` | Extend native artifact and Apply instructions |
| `template.*` | Extend artifact templates and the verification support template |
| `project-guidance` | Add conventions to project README, agent guidance, and configuration context |
| `support-index` | Describe and link component-owned support templates |

Several components may use the same hook. Their blocks append in the selected
component order, preserving the base guidance and each other's contributions.
The builder handles spacing and embedding indentation; unused hooks disappear.
This avoids architecture-specific word substitutions and lets components own
complete, readable explanations.

For example, arc42 can contribute handbook impact guidance. A user-documentation
component could use the same impact hook to identify affected audiences and
procedures, then contribute drafting tasks and verification guidance. Its guide
templates would live in its own `files/` directory. Adding this concern needs no
new architecture slots or changes to the base artifact graph.

## Composition boundaries

Dependencies must be explicitly selected before their consumers. Shared hooks are
allowed; overlapping output files, unknown hooks, and invalid source paths are
errors. Selection order determines presentation, not which conflicting policy wins;
combined guidance still needs review.

Hooks extend prose and templates. They do not add native artifacts, alter their
dependencies, or replace OpenSpec's generated agent integrations. New artifact
types would require a separate, explicit composition design.

Artifact readiness, task completion, verified delivery, and publication remain
distinct. Support templates do not become mandatory artifacts, and native spec sync
does not publish architecture or other documentation. Validate composed variants
with the real OpenSpec CLI as well as builder tests.

See the [builder README](../../../schema_builder/README.md) for commands, manifest
examples, and migration details.
