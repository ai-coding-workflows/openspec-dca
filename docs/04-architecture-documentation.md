# Combining specifications with arc42

The editable system handbook lives in `openspec/system-architecture/`. The reading
order follows [arc42’s twelve sections](https://docs.arc42.org/). Its
`README.md` gives readers the scope and arc42 reading order. The handbook explains
why the system exists, what surrounds and constrains it, and how the present design
fits together. Detailed views stay near the responsible scope, whether or not that
scope already owns a native spec. A published site may assemble or link those
sources, but it is not another editable handbook.

| Handbook topic | Purpose and authority |
| --- | --- |
| `goals-and-stakeholders.md` | Summarize outcomes, scope, quality goals, stakeholders, and the source responsible for each goal |
| `constraints.md` | Record binding restrictions, sources, scope, implications, and suitable review checks |
| `system-context.md` | Describe the system boundary, external actors and systems, and interactions across that boundary |
| `solution-strategy.md`, `building-blocks.md`, `runtime.md`, `deployment.md`, `crosscutting-concepts.md` | Explain the current system-wide design and reference owned details |
| `architectural-decisions.md` | Index scoped ADRs by title, scope, status, and link |
| `quality-requirements.md` | Explain system-wide priorities and scenarios; link measurable obligations and checks at their owners |
| `risks-and-technical-debt.md` | Describe architectural risks and debt with owners and follow-up references |
| `glossary.md` | Define shared terms and link context-specific meanings without replacing local domain models |

Create only useful sections. The README can map them to arc42's twelve topics; file
names need no chapter numbers. A product documentation area may have its own audience
and lifecycle; reference it from the handbook when present. Folder placement does not
assign ownership of business goals to architects: record the responsible stakeholder
or source. `system-context.md` concerns the external system boundary. Internal
bounded-context relationships belong in the building-block view or a referenced
context map. `specs/system/` is reserved for genuine system-owned responsibilities,
such as composition or a shared application boundary, with their own local views.
Create a `spec.md` there only for an independently meaningful contract; documenting
wiring or a shared integration does not by itself require one.

The handbook brings information together without creating competing definitions.
An owned spec states a behavioral or measurable obligation. A local architecture view
explains its implementation. An ADR preserves the choice and alternatives. A binding
external restriction belongs in `constraints.md` with its source; a choice made by the
team belongs in an ADR. Link owned quality thresholds from the handbook instead of
copying them. Refer to local domain models where a term has different meanings in
different contexts.

```text
Local feature architecture/runtime.md ──→ handbook runtime overview
Local adapter architecture/mapping.md ──→ handbook building-block explanation
Scoped architectural-decisions/ ADRs   ──→ handbook decision index
```

An include assembles existing text; it does not create a second editable source.
Select only detail useful to the system-wide question. A feature need not become a
separate architectural building block merely because it has a specification.

## Architecture views and diagrams

These are the guide's documentation and review rules, not extra native OpenSpec
artifacts or a requirement to populate every arc42 chapter. Maintain a **context
overview and a high-level structural diagram** for the declared system scope. A
concise table may replace a simple context diagram. Reuse suitable existing views;
a short text-based structural diagram is sufficient when it answers the question.
No particular diagram language, renderer, or class-level notation is required.

When establishing a baseline, make these views explicit before calling that scope
complete. In an existing project, record missing baseline views as scoped work
rather than turning an unrelated small change into a whole-system rewrite. A
partial or evidence-limited baseline must identify its coverage and remaining gaps.
One page may contain several useful views; separate files and empty chapter stubs
are not required.

### Select views by the question and risk

| View | Question it answers | Authoritative location | When it is needed |
| --- | --- | --- | --- |
| System context | What is inside the system, who interacts with it, and which external systems matter? | `openspec/system-architecture/system-context.md`, or the referenced existing source | Baseline overview; review when boundaries or external relationships change |
| Structure and dependencies | Which responsibilities, ports, and adapters exist, and how do they relate? | Handbook building-block view; detailed views at the responsible scope | Baseline structural diagram; further detail for significant boundaries or dependencies |
| Runtime or sequence | How do participants collaborate, including important failure and consistency boundaries? | Feature- or owner-local `architecture/runtime.md`, or a shared-scope view | Representative architecturally significant interactions, especially asynchronous work, retries, transactions, or uncertain outcomes |
| Domain model or state | What do concepts, relationships, and states mean? | `domain/model.md` or its referenced single source | Where the meaning would otherwise remain ambiguous; reference normative rules rather than duplicating them |
| Deployment | Where do software elements execute, and which operational boundaries matter? | Handbook deployment view and relevant owned detail | Where distribution, environment differences, or changed execution boundaries need explanation |

Require focused additional diagrams when a changed boundary, dependency, important
interaction, or deployment arrangement would otherwise remain ambiguous. Select
representative runtime scenarios, including relevant failure paths; do not require
a diagram for every feature, use case, requirement, or class. Record whether a view
is created, updated, or reused. For an architecture-relevant change with no new or
changed diagram, explain briefly why existing views or text adequately answer the
question. Minor editorial changes need no artificial justification exercise.

### Make each view interpretable and maintainable

Identify the **question, scope, status, and relationship semantics** of each view.
Label important relationships and add a legend where needed. Distinguish contract
consumption, source-code dependencies, runtime calls, data flow, and deployment;
one unqualified arrow must not stand for all of them. A composite view is acceptable
when the relationship types remain explicit. State the core or boundary relative
to which a port or adapter is inbound or outbound.

For cross-context or shared integrations, identify responsible scopes, provided and
consumed contracts, translations, and relevant failure or consistency boundaries.
Do not make contexts, code packages, spec owners, and deployment units appear
one-to-one unless that relationship is actually established. Reference existing
contracts and ADRs without introducing competing rules in diagram labels.

Maintain one editable source for each view. Inline diagram source is acceptable;
rendered images and published includes are derived representations. Keep domain
meaning with the model and technical implementation with architecture. A current
view describes the implemented or observed design at its stated revision; an
accepted but unimplemented target remains identified as such. A fictional teaching
view must say that it is illustrative, not verified against application code.

Use evidence appropriate to the claim. In a reconstructed baseline, distinguish
observed implementation, documented intent, inference, and unknown information.
Reading a test does not establish that it passed; configuration alone does not
establish a live deployment. Preserve material discrepancies for review instead of
silently changing a contract or inventing a historical decision.

## Describing the present and preserving the reasoning

An architecture description explains the current design. An **Architecture Decision
Record**, or ADR, preserves the context, choice, alternatives, and consequences of
a significant decision. Keep records in `architectural-decisions/` under the
responsible context, technical capability, system scope, or other owner. Use
`architectural-decision.md` as the template name and a stable ADR identifier in
record filenames.

`openspec/system-architecture/architectural-decisions.md` is the shared index.
For example, it can link records under `openspec/specs/contexts/lending/architectural-decisions/`,
`openspec/specs/technical-capabilities/document-rendering/architectural-decisions/`,
and `openspec/specs/system/architectural-decisions/`. It is not a second record store
and does not make every indexed decision system-owned. Keep status and scope visible;
label any links to proposed change-local records accordingly.

Accepted rationale should remain available. When a choice changes, record the new
reasoning and explicitly supersede the old decision. Update the current architecture
description as well, so readers do not need to reconstruct today's design from a
sequence of historical decisions.

Separate the **decision status** from delivery progress. An ADR may be accepted
while implementation is still pending. Record actual decision authority or a link
to the acceptance record; neither an agent's proposal nor existing code establishes
that approval. Link migration tasks and verification rather than adding another
backlog to the ADR. In brownfield reconstruction, preserve evidenced historical
rationale and identify unknown reasoning instead of fabricating considered alternatives.

## Updating architecture during an OpenSpec change

Use the existing change artifacts rather than introducing `diagrams.md`, a separate
architecture backlog, or another mandatory approval stage:

| Artifact | Architecture responsibility |
| --- | --- |
| `impact.md` | Identify affected handbook sections, local views, models, and ADRs; record create, update, or reuse with a reason |
| `design.md` | Explain relevant proposed views, assumptions, open decisions, and durable destinations; reference the impact inventory rather than copying it |
| `tasks.md` | Track actual model, diagram-source, architecture, decision-index, and record updates in the one delivery backlog |
| `verification.md` | Record the check against the implemented design and reviewed revision, including reused views, remaining discrepancies, and actual results |

Put proposed implementation choices in `design.md` and, where useful, change-local
`architectural-decisions/` records. Keep proposed and current states explicit; a
proposed view near an owner must say so. Resolve material questions for the next
slice before dependent implementation; detailed diagrams can evolve as the design
is tested. Do not leave the only maintained current view in an archived change.
When an accepted record is promoted from a change's `architectural-decisions/`,
update the handbook index and any catalog path references to its durable location.
Preserve its identity and rationale; do not leave two independently maintained records.

OpenSpec's requirement delta merge handles `spec.md` files. It does not promote an
ADR, update a handbook page or runtime fragment, or maintain the catalog. Check
these separate tasks before closure. Published includes and diagrams are derived
views; preserve one editable source for each.

The architecture-only brownfield route uses its approved runtime plan and review
evidence for these responsibilities; it does not create native change artifacts
merely to document an existing system. See [adoption](07-adoption.md).

### Review content separately from rendering

Before closure, check that the relevant views explain the actual participants,
boundaries, important behavior, and current decision status. Review reused views
without forcing cosmetic edits. Link material discrepancies to corrective work or
an explicit authorized limitation; a newly rendered diagram does not close them.

Project automation may check source existence, rendering, links, and references.
Those checks do not establish that a diagram is true or that an implementation
satisfies its contracts. Missing renderers or unexecuted checks remain missing
evidence, not successful results. No diagram-file count or parser check replaces
semantic review.

## Publication is a separate concern

A tool such as mdBook can publish the Markdown handbook and reference local
fragments. Keep `openspec/system-architecture/README.md` as the handbook overview;
when using mdBook, place its publication navigation in
`openspec/system-architecture/SUMMARY.md`. Configure publication to read this
handbook and its referenced local sources, not another editable architecture tree.
Build output is derived content, not a replacement for those sources.

This guide's own `SUMMARY.md` navigates the numbered guide chapters; it is not the
adopting project's handbook navigation. The [worked example](06-example.md)
keeps its own book and owner-local views. The optional catalog does not automatically index ADRs,
discover handbook files, or check architectural truth. Any generated navigation
must identify its editable source.
