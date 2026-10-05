# Verification: {change}

Status: Pending
Checked code / documentation revision: {immutable reference or base plus identifiable diff}
Specification / model basis: {inspected baseline plus selected delta/model-assessment/draft revisions}
Execution context: {relevant environment, configuration, and tool versions}
Recorded at: {actual date/time of this evidence record}

<!-- Support template for actual evidence, not an eighth artifact or pre-Apply prerequisite.
Suggested verification statuses: Pending, In progress, Ready for acceptance. Actual
acceptance is recorded separately below. When runs cover different revisions, identify
which results remain applicable and recheck affected behavior after later changes. -->

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
- Model clarity: a product-informed reader can explain the concepts and interpret a concrete
  example without change history or implementation. Review applicable identities, relationships,
  values/unknowns, invariant summaries, and lifecycle; reconcile examples with owning requirements
  while preserving conditions/exceptions. Record actual findings and checked model revision,
  not just headings or files read. Reuse/no-change outcomes need no new model.
- Published models explain coherent meaning, not copied assessment/process metadata. Keep
  publication authorization/history in handoff/evidence and concise references in the model;
  publication remains separately authorized and is not performed by this review.
- Actual outside-tree documentation and reused views explain the implementation at the checked
  revision, with clear scope/semantics and one maintained source. Optional drafts alone do not
  complete outside-tree delivery. Check change-local local-view/model/ADR proposals against that
  same basis; their preparation is not maintained publication under openspec/specs/**.
- Real adapters meet their stated guarantees; fakes alone do not establish conformance.
- The change's architectural-decisions.md assessment and any records reflect actual
  decisions/status and intended supersession, without assumed approval or invented history.
- The entire openspec/specs/** tree and other protected model/ADR/catalog files remain unchanged
  from the pre-Apply snapshot, regardless of file type, including new/deleted/renamed paths and
  generated outputs. Mapped outside-tree documentation received planned updates with prior dirty
  and unrelated work preserved.
- The handoff records local architecture publication under openspec/specs/** and other remaining
  protected work at separately authorized sync/archive integration. Keep unpublished local views
  Pending; do not report completed outside-tree edits as pending promotion. Native requirement
  sync does not publish local views or other non-spec companions; record explicit publication evidence.
A list of files opened is not a review conclusion. Omit inapplicable items. -->

## Remaining Gaps and Closure

Acceptance: Pending
Decision reference: {actual project acceptance/authority record, when available}
Maintained descriptive documentation outside openspec/specs/**: {Complete / Pending / Not affected, with checked targets}
Change-local local-architecture proposals: {Checked / Pending / Not affected, with basis}
Local architecture publication under openspec/specs/**: {Pending / Complete / Not affected, with actual publication evidence}
Remaining separate integration / publication: {Pending / Complete / Not needed, with reason}
Closure disposition: {Awaiting integration / Blocked / Ready for archive, with actual reason}

<!-- Link unresolved work to the existing backlog. Distinguish blockers from limitations
actually accepted under project policy; record the decision and follow-up. Accepted gaps
do not become passing tests. Required unavailable checks remain blocking unless an
exception is genuinely authorized. Do not claim pending sync/model/catalog work is done.
Ready for acceptance is not Accepted; checked tasks and artifact presence prove neither.
Apply may finish with local-view/contract/model/ADR/catalog publication or release pending.
Required outside-tree descriptive delivery must actually be completed and checked; local-view
preparation/checks may be complete while maintained publication remains Pending. Record actual
revisions, reconciliation, links, and blockers. At separately authorized sync/archive integration,
explicitly publish mapped protected companions and record results before Ready for archive is
appropriate. Native requirement sync does not do this automatically; all_done is not that decision. Reassess evidence affected by code/model/spec/view changes or rebasing. -->

{{hook:template.verification}}
