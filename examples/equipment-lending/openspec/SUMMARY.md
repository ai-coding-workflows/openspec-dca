# Summary

[About the example](README.md)

# Current baseline

- [System architecture](system-architecture/README.md)
  - [Goals and stakeholders](system-architecture/goals-and-stakeholders.md)
  - [Constraints](system-architecture/constraints.md)
  - [System context](system-architecture/system-context.md)
  - [Architectural decisions](system-architecture/architectural-decisions.md)
- [Domain contract](specs/contexts/lending/domain/spec.md)
  - [Domain model](specs/contexts/lending/domain/model.md)
- [Return feature](specs/contexts/lending/features/return-equipment/spec.md)
  - [Current runtime view](specs/contexts/lending/features/return-equipment/architecture/runtime.md)
- [Loan storage port](specs/contexts/lending/ports/loan-store/spec.md)
- [HTTP adapter](specs/contexts/lending/adapters/in/http/spec.md)
- [Database adapter](specs/contexts/lending/adapters/out/database/spec.md)
  - [Current mapping view](specs/contexts/lending/adapters/out/database/architecture/mapping.md)

# Proposed change

- [Reading the change](worked-change.md)
- [Proposal](changes/record-return-condition/proposal.md)
- [Owner and consumer review](changes/record-return-condition/impact.md)
- [Domain delta](changes/record-return-condition/specs/contexts/lending/domain/spec.md)
- [Return feature delta](changes/record-return-condition/specs/contexts/lending/features/return-equipment/spec.md)
- [Loan storage port delta](changes/record-return-condition/specs/contexts/lending/ports/loan-store/spec.md)
- [HTTP adapter delta](changes/record-return-condition/specs/contexts/lending/adapters/in/http/spec.md)
- [Design](changes/record-return-condition/design.md)
- [Tasks](changes/record-return-condition/tasks.md)
- [Proposed ADR](changes/record-return-condition/architectural-decisions/adr-lending-001.md)
- [Verification status](changes/record-return-condition/verification.md)
