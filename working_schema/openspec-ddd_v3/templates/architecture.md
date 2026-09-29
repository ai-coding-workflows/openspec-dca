# {Responsible scope}: {view title}

Status: {Current or Proposed; choose explicitly}
Scope: {context, technical capability, system responsibility, or shared scope}
Question: {the architecture question this view answers}
Basis: {implemented/observed revision or proposed change reference}

<!-- Optional technical-view support template, not another native artifact. During
native planning/Apply, instantiate inside this change's architecture/ and map its
maintained destination in design.md. The eventual destination is the responsible
scope under openspec/specs or a focused handbook view. Do not write it during Apply.
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

Impact identifies scope, design maps technical draft sources to maintained targets,
and tasks.md links them in a non-checkbox Integration handoff. Publish only in the
separately authorized integration, after comparing with the current baseline. For
reconstruction use its approved runtime plan. Before archive, ensure the integrated
view has a maintained source; do not archive the only current published view. -->

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
