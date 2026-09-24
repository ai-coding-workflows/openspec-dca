# Adoption and migration

Start with one real change in one context. Establish a small trusted baseline from
existing behavior, add the schema, and use one proposal, impact review, design, and
task list. Add owners only where separate contracts help; a small project does not
need a large directory tree or dependency catalog.

## Adopting from ordinary OpenSpec

Install the schema and choose it for new changes. Existing `spec-driven` changes
retain their own schema metadata; changing the project default does not migrate
their artifacts. Finish them with their existing workflow or explicitly adapt one
after reviewing what the added impact artifact requires.

Keep existing capability paths whenever possible. The catalog can assign meaningful
DDD aliases to a flat tree. Move paths only as a separate reviewed migration, with
all references updated and overlapping active changes accounted for.

## Moving from the Living Specs / Spec Kit guide

| Previous artifact or operation | OpenSpec DDD equivalent |
| --- | --- |
| `specs/**/spec.md` | Baseline under `openspec/specs/**/spec.md`, using OpenSpec requirement/scenario headings |
| Change `spec.md` | `proposal.md` for intent/acceptance plus delta specs for contract changes |
| `change.json` scope | Capability paths in proposal and owner dispositions in `impact.md` |
| `plan.md` | One `design.md` per change |
| `tasks.md` | One native tracked `tasks.md` per change |
| `l-specify → l-plan → l-tasks` | `propose`, or optional stepwise artifact creation |
| `l-update → l-diff → l-propagate` | Read-only impact review as needed, then `update` and creation of missing deltas |
| `l-implement`, review, convergence | `apply`, acceptance review, task reconciliation, repeat |
| Custom active-change pointer | Explicit OpenSpec change name and native selection behavior |
| Direct early edits to main contract requirements | Change-local deltas, later deliberate sync |

Migrate the baseline carefully. If the old guide's canonical specs already contain
unimplemented target behavior, do not label that text as the implemented baseline
and then apply the same change again. Reconstruct a supported baseline plus deltas,
or document an intentionally early-synced state with its remaining work.

Retain valid completed task history, archived efforts, architecture fragments, and
accepted ADR rationale. Keep legacy archives in a clearly documented historical
location; they do not become valid native OpenSpec changes just by moving folders.
Finish or deliberately convert active efforts before retiring the old pointers and
prompts. Do not let two tools independently update the same contract lifecycle.

## Maintain trust

Link requirements to meaningful tests or review evidence. Investigate drift against
actual code; neither timestamps nor the catalog establish conformance. Treat impact
results as review suggestions, and keep dispositions for unchanged consumers.

When independent changes modify the same named requirement, review them together.
A MODIFIED delta contains a complete replacement: blindly applying two versions
can discard the first change's additions. Reconcile the second delta against the
new baseline before sync. The catalog helps find overlaps but does not merge them.

Upgrade deliberately. The supplied compatibility tests target OpenSpec 1.13.1;
custom schemas are an upstream experimental interface. Test the installed version,
review changes to generated workflows, and refresh native integrations with
`openspec update`. Diff and update the DDD schema separately; native integration
updates do not distribute a newer copy of this bundle.
