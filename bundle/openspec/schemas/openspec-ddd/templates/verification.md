# Verification: {change}

Status: Pending
Checked code / documentation revision: {immutable reference or base plus identifiable diff}
Specification / model basis: {main baseline plus selected delta/model revisions; note early sync}
Execution context: {relevant environment, configuration, and tool versions}
Recorded at: {actual date/time of this evidence record}

<!-- Support template for actual evidence, not a sixth artifact or pre-apply prerequisite.
Suggested verification statuses: Pending, In progress, Ready for acceptance. Actual
acceptance is recorded separately below. When runs cover different revisions, identify
which results remain applicable and recheck affected behavior after later changes.
Architecture-only reconstruction records equivalent evidence in its runtime artifacts;
it does not create a native change just to instantiate this template. -->

## Acceptance and Evidence

| Acceptance / requirement / checked aspect | Check or method | Actual result | Evidence / revision |
| --- | --- | --- | --- |

<!-- Cover added/modified/removed/renamed requirements, affected baseline guarantees,
important risks, and consumer compatibility. Use exact path/name or existing stable ID.
One rule may need several checks and one check may cover several rules. Reference the
existing association source instead of a second independent trace index.

Use Passed, Failed, Not run, or Partial with reasons. Record actual commands/selectors,
CI runs, relevant scope and revision, or review records. A referenced test, inspected
test file, planned check, rendered diagram, or executed code line is not a passing
behavioral check. Code coverage is supplementary evidence, not a universal threshold. -->

## Model, Architecture, and Contract Review

<!-- Actual findings and evidence for applicable concerns:
- Impact/deltas agree with ownership and real consumers, including callers outside the catalog.
- Model meanings and normative rules agree; old-data semantics and new actions are distinct.
- Affected/reused handbook and local diagrams explain the reviewed implementation, with clear
  scope, relationship semantics, source, and proposed/current status.
- Real adapters meet their stated guarantees; fakes alone do not establish conformance.
- Scoped architectural-decisions/ records and the handbook index reflect actual decisions,
  supersession, and implementation status; no assumed acceptance or invented history.
- Model, handbook, diagram, ADR/index, and catalog updates are accounted for separately
  from requirement sync, including remaining finalization tied to synchronization.
A list of files opened is not a review conclusion. Omit inapplicable items. -->

## Remaining Gaps and Closure

Acceptance: Pending
Decision reference: {actual project acceptance/authority record, when available}
Closure disposition: {Blocked or Ready for normal closure, with reason}

<!-- Link unresolved work to the existing backlog. Distinguish blockers from limitations
actually accepted under project policy; record the decision and follow-up. Accepted gaps
do not become passing tests. Required unavailable checks remain blocking unless an
exception is genuinely authorized. Do not claim pending sync/model/catalog work is done.
Ready for acceptance is not Accepted; checked tasks and artifact presence prove neither.
Reassess evidence if code, rules, diagrams, or model meaning changed after the check. -->
