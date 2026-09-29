# {System name}: system architecture

Status: {Draft, Current, or Proposed; distinguish mixed states explicitly}
Scope: {system boundary and covered repository areas}
Basis: {inspected code/documentation revision, or proposed change reference}
Coverage: {reviewed, sampled, excluded, and still unknown areas}

<!-- Starter for openspec/system-architecture/README.md. This file and its sibling
starters are templates, not verified system documentation. Create only useful pages.
On instantiation keep links only to actual pages or authoritative existing sources;
remove unused rows instead of publishing broken links or empty chapters. -->

## Purpose and authority

Explain the current system and the sources that establish its goals, context,
constraints, and design. Distinguish observed implementation, documented intent,
inference, and unknowns. Do not infer business priorities or deployed guarantees
from code alone. State the covered scope rather than imply exhaustive inspection.

The handbook summarizes system-wide concerns and references owned contracts and
local views. It does not replace domain models, copy normative value lists, duplicate
quality thresholds, or turn every feature into a deployment component. External
constraints name their source; team choices belong in architectural decision records.

## Reading order

| arc42 topic | Page / authoritative source | What the reader should learn |
| --- | --- | --- |
| 1. Introduction and goals | [Goals and stakeholders](goals-and-stakeholders.md) | Purpose, outcomes, priorities, and their responsible sources |
| 2. Constraints | [Constraints](constraints.md) | Binding restrictions, scope, and implications |
| 3. Context and scope | [System context](system-context.md) | External boundary, actors, and neighboring systems |
| 4. Solution strategy | [Solution strategy](solution-strategy.md) | How key choices address goals and constraints |
| 5. Building blocks | [Building blocks](building-blocks.md) | Major responsibilities and their relationships |
| 6. Runtime | [Runtime](runtime.md) | Representative interactions and significant failure behavior |
| 7. Deployment | [Deployment](deployment.md) | Execution arrangements and relevant environment differences |
| 8. Crosscutting concepts | [Crosscutting concepts](crosscutting-concepts.md) | Shared implementation approaches and their owners |
| 9. Decisions | [Architectural decisions](architectural-decisions.md) | Navigation to real scoped records and their actual status |
| 10. Quality requirements | [Quality requirements](quality-requirements.md) | Important quality scenarios and authoritative obligations |
| 11. Risks and debt | [Risks and technical debt](risks-and-technical-debt.md) | Uncertainties, consequences, and tracked follow-up |
| 12. Glossary | [Glossary](glossary.md) | Shared terms and links to context-specific meanings |

## Minimum views and selected detail

Provide a system-context overview and a high-level structural diagram for the
claimed baseline scope. A simple context may use a table; reuse adequate existing
sources. Link them above or explain where they are maintained. Document material
gaps rather than create a stock diagram or call an incomplete baseline complete.

Add focused runtime, state, or deployment views when important architectural questions
would otherwise remain ambiguous. No diagram per feature or full set of pages is
required. Each view states its question, scope, current/proposed status, relationship
semantics, and one editable source. Label important arrows and distinguish calls,
code dependencies, consumed contracts, data flow, and deployment. Use project-supported
notation. Rendering alone is not conformance or evidence of deployed behavior.

## Owned detail and decisions

Reference relevant contexts, technical capabilities, and system-owned responsibilities
under openspec/specs/, including architecture-only areas without a spec when useful.
A domain model explains meaning; a local architecture view explains implementation.
Individual ADRs live in architectural-decisions/ at the responsible scope. The index
links them without copying accepted rationale or inventing retrospective decisions.

## Maintenance and evidence

For native changes, impact identifies create/update/reuse; domain-model-changes.md
owns semantic revisions and model mappings; design owns technical drafts; the change's
architectural-decisions.md assesses record needs and mappings. tasks.md tracks preparation
and carries a non-checkbox Integration handoff; verification records actual results.
Keep handbook and other maintained baseline paths read-only during planning/Apply.
Publish only through separately authorized integration after reconciling the current
baseline, including prior concurrent changes. For architecture-only reconstruction,
use its approved runtime plan and reviews instead. Identify changes invalidating evidence.

Requirement sync does not update this handbook, owned models/diagrams, ADRs, or catalog.
Keep one editable source; generated publications are derived. Add SUMMARY.md only
when configuring a publication, using actual chapter paths. Neither a template copy
nor a successful build proves that these descriptions match the system.
