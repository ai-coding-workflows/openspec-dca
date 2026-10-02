# Reading the proposed change

The request is to record the condition of returned equipment. This fictional
example has one maintained baseline and one proposed change. It contains no
application implementation, and all seven delivery tasks remain open.

Start with the [system architecture](system-architecture/), the
[return feature](specs/contexts/lending/features/return-equipment/spec.md),
the [domain model](specs/contexts/lending/domain/model.md), and the
[loan storage port](specs/contexts/lending/ports/loan-store/spec.md). These are the
current baseline. The [runtime view](specs/contexts/lending/features/return-equipment/architecture/runtime.md)
and [database mapping](specs/contexts/lending/adapters/out/database/architecture/mapping.md)
also describe the current illustrative design.

Then read the [proposal](changes/record-return-condition/proposal.md) and
[impact review](changes/record-return-condition/impact.md). The impact review
identifies the owners that need contract deltas and the consumers to review.
The database adapter needs implementation work, but its spec already delegates
the storage guarantee to the port, so it has no duplicate delta.

The [port delta](changes/record-return-condition/specs/contexts/lending/ports/loan-store/spec.md)
replaces the baseline requirement with its complete updated content. The existing
failure guarantee remains in that requirement. If a real adapter could not tell
whether a failed save had committed, the port and consumer behavior would need an
explicit decision before implementation. The
[domain delta](changes/record-return-condition/specs/contexts/lending/domain/spec.md)
adds the new-return obligation; the baseline model remains unchanged until delivery.
The [feature](changes/record-return-condition/specs/contexts/lending/features/return-equipment/spec.md)
and [HTTP](changes/record-return-condition/specs/contexts/lending/adapters/in/http/spec.md)
deltas complete the proposed behavior.

One [design](changes/record-return-condition/design.md) and
[task list](changes/record-return-condition/tasks.md) coordinate the work.
The [proposed ADR](changes/record-return-condition/architectural-decisions/adr-lending-001.md)
stays with the change until accepted. Updating the durable model, runtime view,
handbook index, and ADR location requires explicit tasks; native spec sync does
not do that work. The [verification record](changes/record-return-condition/verification.md)
reports no application tests or acceptance evidence.
