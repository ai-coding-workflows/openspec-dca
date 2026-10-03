# Architectural decisions for change: {change}

<!-- Use ordinary wording for the choice and its consequences. This file is the
assessment/index, not a place to duplicate full ADRs. Keep actual approval separate
from recommended choices. Exact IDs and source paths remain intact. -->

## Assessment

Reviewed design and sources: {design revision plus relevant existing ADR/model/spec references}
Summary: {which significant choices need durable records, or why none are needed}

<!-- This change-local assessment is always produced, also with skip_specs. A concise
No ADR required explanation or explicit reuse of existing records is enough when
appropriate. Do not create an empty records directory or a fictional ADR to fill it.
This file is not an individual ADR and not the maintained architecture documentation decision index. -->

## Decision Dispositions

| Choice / existing ADR | Disposition | Reason | Record / actual status |
| --- | --- | --- | --- |

<!-- Dispositions: Reuse existing, New ADR, Supersede existing, No ADR required.
These are assessment choices, NOT decision statuses or review-outcome enums.
Reference an actual existing record for reuse. For a new/superseding decision,
create its change-local record with architectural-decision.md; link detailed
rationale instead of copying it here or independently in design. Routine choices
can remain in design. Actual Proposed/Accepted/Rejected status and authority are
recorded by the individual ADR. This table does not grant acceptance. -->

## Records and Integration Targets

| Existing record / inspected basis | Change-local record | Intended maintained destination | Decision reference / supersession / publication prerequisite |
| --- | --- | --- | --- |

<!-- Only needed when a record is created or changed. Draft record paths are relative
to this change (architectural-decisions/...); maintained sources/destinations are
project-relative. Preserve accepted history and stable IDs. Do not update shared
numbering, maintained record status/supersession, or the catalog during Apply. The entire
openspec/specs/** tree stays read-only during planning/Apply, including descriptive indexes.
Mapped descriptive indexes outside that tree may link existing durable records with their actual
status; this does not accept or promote records. Prepare entries depending on unpublished records
or protected local views here and reference them from the Integration handoff, not maintained links
to transient drafts. Check identity collisions/current baselines before separately authorized
sync/archive publication. -->

## Open Decisions

| Decision question | Why it matters now | Options / recommendation | Work waiting for the decision |
| --- | --- | --- | --- |

<!-- Keep cells short. Link to the option comparison in design or the individual
ADR; do not maintain a second copy. Explain the practical problem before unfamiliar
technical terms. Preserve the option labels and distinguish recommendation from
selection. Put a field/API check in the appropriate prerequisite even if no new
architecture decision is required. -->

<!-- Name unresolved material decisions and the work they block. No open decisions
is a valid answer only after review. Resolve before dependent implementation; file
presence or a selected disposition is not acceptance. Preserve project approvals,
not a new mandatory approval process just for this artifact. -->

## Consistency Review

<!-- Record the review against domain-model-changes.md, the applicable deltas, and
design.md. If a choice changes semantics or obligations, reconcile those artifacts
before dependent tasks. If detailed rationale moved from design into an ADR, leave
one canonical proposed record plus links. An accepted change-local ADR may still
be unimplemented or unpublished. Keep these states distinct. -->

{{hook:template.architectural-decisions}}
