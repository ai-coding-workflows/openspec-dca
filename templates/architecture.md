# {Owner or shared scope}: {view title}

Status: Proposed
Scope: {system, context, module, or owner}
Question: {the architecture question this view answers}

<!-- Choose Current or Proposed explicitly. A Current view describes the actual
implementation at its stated scope, not merely an accepted target. Identify a relevant
release, branch, or change when needed to distinguish coexisting designs. Reuse this
template for one useful view, not for a mandatory file per owner. Remove unused
optional sections. -->

## Responsibilities and Boundaries

<!-- Explain the relevant responsibilities, external participants, and boundaries.
Reference feature, domain, port, and adapter owners instead of redefining their rules.
A feature need not be a separate runtime or deployment building block. 

For cross-context or shared components, identify the responsible owner,
participating contexts/modules, consumed and provided contracts, and the
reference boundary for each inbound/outbound role. Distinguish shared
infrastructure from shared behavioral ownership.
-->

## View and Diagrams

<!-- Include a diagram or link its single editable source when required by the
project's architecture-view rules. Reuse an adequate view rather than copying it.
For simple detail that needs no diagram, explain it in text and reference the broader
view where useful. Do not embed an invented placeholder architecture.

Identify the view type, scope, important assumptions, and deliberate omissions.
Label relationships and give a legend where necessary. Distinguish source-code
imports, runtime calls, data flow, contract consumption, and deployment relationships.
Use project-supported diagram tooling. Inline source is acceptable; generated images
and published includes are not independently editable sources.

Keep proposed diagrams tied to their change and name the maintained destination in
design/tasks. The only current view must not be left in an archived change. -->

## Important Behavior and Failure Paths

<!-- Explain significant ordering, consistency, transaction boundaries, timeouts,
retries, or partial/unknown outcomes where relevant. Separate confirmed failure from
an indeterminate outcome when the integration can distinguish neither commit nor
rollback. Reference the governing contract; do not weaken it inside this explanation.
Keep domain-model diagrams with the domain model and link them here when useful. -->

## Decisions and Constraints

<!-- Link relevant ADRs, contract obligations, and quality constraints. Explain how
they affect this view. Keep accepted rationale in ADRs and actual conformance evidence
in verification or linked review/test runs; do not create a second acceptance record. -->

## Code Entry Points (optional)

| Responsibility | Code path or symbol | Related owner / contract |
| --- | --- | --- |

<!-- Keep only useful, verified navigation links. Avoid manual line-number mappings.
One owner can map to several code locations and vice versa. These links help readers
find implementation; they do not prove compliance or identify every affected file. -->
