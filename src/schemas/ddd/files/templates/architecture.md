# {Responsible scope}: {view title}

Status: {Current or Proposed; choose explicitly}
Scope: {context, technical capability, system responsibility, or shared scope}
Question: {the architecture question this view answers}
Basis: {implemented/observed revision or proposed change reference}

<!-- Optional technical-view support template, not another native artifact. During
planning, describe the view in design.md or an optional change-local architecture/ draft.
Map its maintained destination and checks in design.md. The entire openspec/specs/** tree
remains read-only during planning and Apply, including descriptive views, diagrams, and assets.
Prepare and check proposals for those targets change-locally; publish maintained content only
in separately authorized sync/archive integration. Native requirement sync does not publish views.
Apply updates mapped descriptive sources outside that tree in the development checkout, preserving
protected model/spec/ADR/catalog content wherever located.
Remove irrelevant prompts.
Current means implemented/observed at the stated basis, not merely accepted as a target.
Distinguish source evidence, documented intent, inference, and unknowns in reconstruction. -->

## Responsibilities and Boundaries

<!-- Explain relevant responsibilities and what is outside scope. Refer to existing
contracts rather than repeat rules or invent spec owners. For shared/cross-context
components name responsible scopes, provided/consumed contracts, translations, and
in/out reference boundaries. A feature is not automatically a deployment unit. -->

## Views and Diagrams

<!-- Include or link one authoritative editable source for each necessary view.
Identify question, scope, current/proposed status, relationship meaning, and important
assumptions. Label dependencies/calls/data flow precisely; do not use one unqualified
arrow for code dependencies, consumed contracts, runtime calls, and deployment.

Use a context overview and structural diagram for a declared baseline; a simple
context table and existing adequate views count. Add diagrams for material unresolved
architectural questions, not every feature or class. Explain significant omissions.
Domain/state meaning stays with the model, not database/class diagrams presented as
business truth. Published images/includes are derived. Use installed project formats;
a successful render does not prove truth or complete link correctness.

Impact identifies scope; design maps actions, sources, optional drafts, maintained targets,
and checks. tasks.md tracks outside-tree descriptive delivery during Apply, plus change-local
preparation/checks for views under openspec/specs/**. Its handoff covers their actual publication
and dependent links at separately authorized sync/archive integration. Reconcile current targets
and preserve concurrent/unrelated content before authorized publication. Before archive, confirm
required current views have actual maintained sources; a checked proposal is not published content,
and a draft inside the archived change is not the sole editable destination. -->

## Important Behavior and Failure Paths

<!-- Explain selected relevant interactions, transaction/consistency boundaries,
failure paths, concurrency, retries, or migration. Reference owned guarantees instead
of changing them here. A timeout alone does not prove remote rollback; record evidence
and unknown outcomes. Resolve contract/adapter mismatches explicitly, not as a prose edit. -->

## Decisions and Constraints

<!-- Link scoped architectural-decisions/ records and binding constraints with sources.
Separate externally imposed constraints, team decisions, accepted targets, implemented
choices, and open questions. Name work blocked by material unresolved decisions. -->

## Code Entry Points (optional)

| Responsibility | Path / stable symbol | Contract or view reference |
| --- | --- | --- |

<!-- Navigation only. Reference an existing index where useful; do not enumerate every
function or maintain line numbers. Executed code and links do not establish conformance. -->
