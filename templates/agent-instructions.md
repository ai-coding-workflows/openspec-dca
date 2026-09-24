## Working with OpenSpec DDD

Use native OpenSpec workflows and the project's configured schema. Resolve an
explicit change name or spec path before relying on conversation context. Catalog
aliases identify owners; native OpenSpec spec commands need capability paths.

Before planning revisions or implementation, read the relevant main specs together
with the selected change's deltas, impact review, architecture, and ADRs. A baseline
alone does not describe an active change's target. Read prerequisite contracts first.

Keep one design and task list per coherent change. Include necessary domain/port
refinements and report added owners and reasons. Review consumers; do not silently
expand scope to all of them. Tailor normative requirements to their owner; keep model
definitions in one authoritative companion when useful. Clarify unresolved material
behavior/compatibility choices, respecting decisions and authorization already provided
by the user.

When refining, reconcile proposal, impact, deltas, design, and tasks. Obtain current
native artifact instructions when creating missing files or substantially rewriting
an artifact. Preserve valid completed history and record newly discovered work.

Use test-first slices for new or changed executable behavior: check the expected test
failure, implement, then refactor with tests passing. State a reason when that order is
not appropriate. Update current architecture and any domain-model companion with accepted
implementation. Preserve accepted ADR rationale; explicitly accept or supersede decisions.
Spec synchronization does not update architecture, model companions, ADRs, or the optional
catalog. Record actual evidence and remaining gaps before closing a change. Never implement
archived changes.
