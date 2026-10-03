<!-- Write a brief reader-oriented explanation before implementation detail. Explain
unfamiliar terms without changing exact identifiers or weakening requirements.
Separate current evidence, proposed design, unknowns, and approved decisions. -->

## Approach

<!-- One design for the change; read baseline plus deltas, impact, model definitions,
and relevant architecture. Read domain-model-changes.md with the baseline model;
reuse its definitions and references rather than rewriting meaning. Refer to
contracts rather than duplicate obligations.
Explain responsibilities, code boundaries, and the selected approach, not a plan
per owner or an obligatory mirror of spec folders in source code. -->

## Design Choices and Alternatives

<!-- For each unresolved material choice, use the structure below only where it helps.
Do not combine all options into one long question or ask the reader to decode jargon.

### {Concrete question the reader must answer}
Current evidence: {what was observed and where; a fake is not the real service}
Why it matters: {a concrete consequence or failure case in ordinary words}

| Option | What this delivers | Work, deferral, and limits |
| --- | --- | --- |
| {A: descriptive name} | {Comparable scope} | {Concise consequence; detail below if needed} |

Recommendation: {option and sourced reasoning, or none; not an approval}
Decision: {Pending, or actual choice and authority/reference}
Still to verify: {exact uncertainty, relevant source/test, and blocked work}

For complex options use short per-option headings instead of crowded table cells.
Preserve all scope, restart, migration, concurrency, and failure qualifications.
If a full ADR exists, link its option discussion instead of copying it here. -->

<!-- Why this approach and which meaningful alternatives were considered. Distinguish
assumptions, existing decisions, and proposals. The subsequent architectural-decisions
artifact assesses whether a significant choice needs an ADR. Keep working rationale
here until a record is written, then replace duplication with its reference. Routine
choices needing no ADR may stay here. No invented historical rationale or acceptance.
Resolve material choices before dependent work and name blocked slices explicitly. -->

## Delivery Slices and Dependencies

<!-- Plan the next useful cross-owner slices in detail; later work may stay coarser
but actionable. Contract dependencies are not task order. Use small test-first cycles
where appropriate, with justified exceptions and reuse of existing tests. There is
no exhaustive upfront test inventory. Actual work stays in the single tasks.md. -->

## Proposed Architecture Views

<!-- Reference impact's affected-scope inventory. Keep precise semantic revisions
in domain-model-changes.md; do not repeat definitions in the technical design.
The architectural-decisions artifact owns ADR dispositions and record mappings.
The architecture.md support template can be used for a substantial technical view.

Include or link diagrams needed for significant boundaries, dependencies, interactions/
failures, or deployment. Reuse adequate current views, not a diagram per feature.
State question, scope, status, editable source, relationship semantics, and important
assumptions. Distinguish calls, code dependencies, consumed contracts, and deployment;
define in/out relative to the considered core and explain cross-context translations.

Put proposed view content here OR in architecture/<scope>/<view>.md inside this change,
not in both. A separate draft is optional. Planning leaves maintained destinations unchanged.
The entire openspec/specs/** tree remains read-only during planning and Apply; prepare and check
local-view proposals change-locally and map their publication to separately authorized sync/archive
integration. Apply updates mapped descriptive views outside that tree in the development checkout.
Keep implemented/observed versus proposed status explicit; a checked proposal is not publication,
and drafts alone do not complete outside-tree maintained delivery. -->

## View Integration Targets

| Existing view / inspected basis | Action / optional planning draft | Maintained destination | Required check / remaining prerequisite |
| --- | --- | --- | --- |

<!-- Sources/destinations are project-relative; drafts are change-relative.
Use the project's maintained architecture locations; owned details stay under
contexts/, technical-capabilities/, or system/ in openspec/specs.
Reference model and ADR mappings in their assessments instead of duplicating them.
Track actual outside-tree updates and change-local proposal preparation/checks in tasks.md's
Apply checklist. Put local architecture publication under openspec/specs/** and dependent links
in its non-checkbox handoff for separately authorized sync/archive integration. Reconcile current
baselines and preserve unrelated content before publishing; do not leave the sole current view
in an archived change. Maintain links only to existing durable sources, deferring references to
unpublished protected targets. Native requirement sync does not merge local views or other non-spec
content; explicitly publish those mapped companions. Model/ADR publication, catalog registration,
and deployment remain separate wherever located. -->

## Compatibility, Migration, and Risks

<!-- Include significant caller/consumer compatibility, old-data behavior, consistency,
failure semantics, deployment and rollback. State evidence and limits. A communications
failure does not by itself establish whether a remote operation committed. Resolve
actual contract/adapter mismatches rather than silently weaken a guarantee in design.
Omit sections without useful content; link existing risks instead of another backlog. -->

## Verification Strategy

| Requirement / affected guarantee / risk | Planned check and level | Dependency or limitation |
| --- | --- | --- |

<!-- Plan representative success, rejection, failure, migration, and compatibility
checks, including affected baseline guarantees. Choose domain, use-case, mapping,
real-adapter conformance, integration, or review as appropriate. A fake alone does not
establish the real adapter's guarantee. Reuse meaningful tests; explain test-first
exceptions. No fixed code-coverage percentage or E2E test per scenario is required.

Reference existing test associations or useful code entry points. Exact paths and
requirement names suffice; a new ID scheme or trace manifest is not mandatory. Test
links are not test results. These are planned checks; actual results, checked revisions,
remaining gaps, and acceptance decisions belong in verification.md or linked evidence. -->

{{hook:template.design}}
