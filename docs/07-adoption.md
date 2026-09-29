# Adoption and migration

For contract work, start with one real change in one context. Establish a small baseline from
existing behavior, add the schema, and use one proposal, impact review, design, and
task list. Add owners only where separate contracts help; a small project does not
need a large directory tree or dependency catalog.

## Naming a new baseline

Use `openspec/system-architecture/` for the editable system handbook,
`openspec/specs/technical-capabilities/` for independently owned technical contracts,
and `architectural-decisions/` for scoped ADR records. These are the guide's baseline
names, not optional renames deferred to a later change. The handbook's
`architectural-decisions.md` is an index. Do not create parallel legacy trees in a
new setup. Generated publication output may remain outside `openspec/`.

### Architecture-only brownfield reconstruction

The separate internal brownfield workflow can establish an evidence-backed
architecture baseline before any new contracts are authored. Use the same handbook
and local-scope paths, without creating `spec.md`, `needs.md`, or a native OpenSpec
change merely to host the documentation. Keep the runtime plan and review evidence
separate from the published baseline; its approved checklist is the sole task source.
Document observed behavior, distinguish it from documented intent and inference,
and preserve existing specifications and ADRs. Architecture-only scopes belong in
handbook navigation, not in the spec-owner catalog unless a main spec exists.

Use the same [view policy](04-architecture-documentation.md#architecture-views-and-diagrams)
for the declared reconstruction scope: a context overview and structural diagram,
plus only the additional views needed to explain significant evidence. Existing
views can satisfy it. Record gaps instead of inventing boundaries or reorganizing
the implementation into an idealized DDD structure.

Give each runtime task an evidence starting point, focus, approved destination,
and observable completion check (`Start`, `Focus`, `Target`, and `Check`). Keep
architecture reconstruction and review separate from catalog/book publication;
publication can navigate architecture-only areas without creating spec owners.
Preserve existing product code, tests, needs, specifications, and manual reasoning.
Record safe checks actually executed, missing prerequisites, and the reviewed
revision. Test source is evidence of a test's intent, not a passing run.

In that internal workflow, `blocked` waits for user input and normally resumes at
the same stage. Reviews keep their existing `success` and `issues` outcomes. A
publication-stage architecture problem requires explicit upstream recovery rather
than treating every blocker as an architecture correction. These are internal
orchestration responsibilities, not new native OpenSpec commands or changes to
the contract-delivery lifecycle.

## Adopting from ordinary OpenSpec

Install the schema and choose it for new changes. Existing `spec-driven` changes
retain their own schema metadata; changing the project default does not migrate
their artifacts. Finish them with their existing workflow or explicitly adapt one
after reviewing what the added impact artifact requires.

An existing adopting repository may already have stable capability paths and manual
documentation. The catalog can assign meaningful DDD aliases to a flat tree. Preserve
those sources unless a separate migration is explicitly approved; the new naming
baseline does not authorize a brownfield documentation pass to relocate them.

For an approved migration from legacy `docs/architecture/`, `modules/`, or
`decisions/` locations, update links, includes, publication source paths, catalog
references, and overlapping active changes. Preserve ADR identifiers and accepted
rationale. Keep catalog field names such as `decisions` and `depends_on` unchanged;
a directory rename is not a catalog-schema change. Do not make capability-path
moves incidental to a behavioral change.

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
