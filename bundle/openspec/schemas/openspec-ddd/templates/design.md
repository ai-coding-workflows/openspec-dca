## Approach

<!-- One design for the change; read baseline plus deltas, impact, model definitions,
and relevant architecture. Refer to contracts rather than duplicate obligations.
Explain responsibilities, code boundaries, and the selected approach, not a plan
per owner or an obligatory mirror of spec folders in source code. -->

## Decisions and Alternatives

<!-- Why this approach and which meaningful alternatives were considered. Distinguish
assumptions, existing decisions, and proposals. Link significant decisions to scoped
architectural-decisions/ records; do not invent historical rationale or acceptance.
Resolve material choices before dependent work and name blocked slices explicitly. -->

## Delivery Slices and Dependencies

<!-- Plan the next useful cross-owner slices in detail; later work may stay coarser
but actionable. Contract dependencies are not task order. Use small test-first cycles
where appropriate, with justified exceptions and reuse of existing tests. There is
no exhaustive upfront test inventory. Actual work stays in the single tasks.md. -->

## Architecture and ADR Updates

<!-- Reference the inventory in impact.md, adding exact destinations for new artifacts.
Use openspec/system-architecture/ for the system handbook; keep local views/model
companions at their responsible scope under contexts/, technical-capabilities/, or
system/ in openspec/specs. Do not create a competing handbook under specs/system/.

Include or link the proposed diagrams needed to explain significant boundaries,
dependencies, interactions/failures, or deployment. Reuse adequate existing views;
no diagram per feature is required. State question, scope, status, editable source,
relationship semantics, and important assumptions. Distinguish code dependencies,
runtime calls, consumed contracts, and deployment; define in/out relative to a core.

Name affected requirements for model edits. Keep proposed model wording change-local
or explicitly proposed, and coordinate accepted definitions with the main-spec baseline.
Current architecture describes implemented behavior; early-synced targets and accepted-
but-unimplemented decisions remain explicit. Support templates in this schema's
library are optional; they are not new artifact IDs or planning prerequisites.

Preserve accepted ADR rationale and explicit supersession. Proposed records may start
in this change's architectural-decisions/. Track durable record and handbook-index
updates in tasks; spec sync does not perform any of these documentation updates. -->

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
