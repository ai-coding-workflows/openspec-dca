# Verification: {change}

Status: Pending
Checked code / documentation revision: {immutable reference or base plus identifiable diff}
Specification / model basis: {inspected baseline plus selected delta/model-assessment/draft revisions}
Execution context: {relevant environment, configuration, and tool versions}
Recorded at: {actual date/time of this evidence record}

<!-- Support template for actual evidence, not an eighth artifact or pre-Apply prerequisite.
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
- domain-model-changes.md and referenced model drafts agree with the deltas; historical
  semantics and new actions are distinct. Assessment findings are resolved for dependent work.
- Change-local technical drafts and reused maintained views explain the reviewed target,
  with clear scope, semantics, source, and publication status. Do not fail merely because
  intentionally protected baseline views still describe the earlier implementation.
- Real adapters meet their stated guarantees; fakes alone do not establish conformance.
- The change's architectural-decisions.md assessment and any records reflect actual
  decisions/status and intended supersession, without assumed approval or invented history.
- Maintained spec/model/view/ADR files, handbook, and catalog remain unchanged from the
  pre-Apply snapshot, including added/deleted/renamed files and preserved prior dirty work.
- Proposed publication effects are accounted for in tasks.md's Integration handoff and
  its linked mappings. Native sync does not perform non-spec publication.
A list of files opened is not a review conclusion. Omit inapplicable items. -->

## Remaining Gaps and Closure

Acceptance: Pending
Decision reference: {actual project acceptance/authority record, when available}
Integration / publication: Pending
Closure disposition: {Awaiting integration / Blocked / Ready for archive, with actual reason}

<!-- Link unresolved work to the existing backlog. Distinguish blockers from limitations
actually accepted under project policy; record the decision and follow-up. Accepted gaps
do not become passing tests. Required unavailable checks remain blocking unless an
exception is genuinely authorized. Do not claim pending sync/model/catalog work is done.
Ready for acceptance is not Accepted; checked tasks and artifact presence prove neither.
Apply can finish with Integration / publication pending. A separately authorized operation
records what was actually published, its revision, reconciliation and link checks, and
any remaining blockers before Ready for archive is appropriate. Native all_done is not
that decision. Reassess evidence affected by code/model/spec/view changes or rebasing. -->
