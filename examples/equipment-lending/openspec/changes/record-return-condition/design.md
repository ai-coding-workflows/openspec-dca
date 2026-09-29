## Approach

The current model has no return-condition concept. The proposed model adds:

- `ReturnCondition` has the values `usable` and `needs-inspection`. `usable` records
  that the item was assessed as usable at return. `needs-inspection` records that an
  inspection is needed after return; it does not assert the inspection outcome.
- `unrecorded` is not a `ReturnCondition` value. It means a historical return has no
  recorded assessment. Migration preserves that missing information.
- A new completed return records exactly one `ReturnCondition`.

This is proposed wording for the domain-model companion, not the current baseline.
The domain delta states the new-return obligation and rejection behavior by referring
to these definitions. Add the condition to the return input and loan model, validate
it using the domain rule, then persist the returned state and condition through the
existing storage port. The database adapter uses one transaction. HTTP validates the
request shape and maps domain/use-case outcomes according to its delta spec.

## Decisions and Alternatives

The proposed ADR-LENDING-001 records the atomic-save decision. Two separate durable
writes would permit partial returns. A needs-inspection condition is recorded, but
maintenance automation is outside this change. Domain values are not duplicated in
adapter-specific enumerations without an explicit mapping.

## Delivery Slices and Dependencies

1. Add domain and port tests for the proposed behavior, observe expected failures, then implement the model/input and stronger port contract.
2. Add migration and storage-adapter failure/conformance checks, then implement atomic persistence.
3. Add feature, HTTP, and caller checks for the end-to-end flow, then carry the condition through each boundary.
4. Complete failure and historical-data coverage, update durable documentation, and record acceptance evidence.

## Architecture and ADR Updates

Update `openspec/specs/contexts/lending/domain/model.md`,
`openspec/specs/contexts/lending/features/return-equipment/architecture/runtime.md`,
and `openspec/specs/contexts/lending/adapters/out/database/architecture/mapping.md`.
Review `openspec/system-architecture/goals-and-stakeholders.md`,
`system-context.md`, and `architectural-decisions.md` for any changes needed to
reflect the accepted design, without restating owned requirements. The model update
is tracked here because native requirement sync does not merge it.
When accepted, promote the proposed ADR to
`openspec/specs/contexts/lending/architectural-decisions/adr-lending-001.md` with its actual status
and add that path to relevant catalog entries. No accepted ADR is superseded here.
These are explicit implementation tasks, not OpenSpec spec-sync side effects.

## Compatibility, Migration, and Risks

Keep the stored condition nullable for historical returns; only new return commands
require it. Coordinate callers and service deployment in the teaching scenario.
Before release, verify that rollback preserves newly collected values. A real rollout
needs concrete deployment and rollback commands from its application repository.

## Verification

Use domain, port-conformance against the real adapter, feature, HTTP, and end-to-end
failure tests. Include invalid conditions and pre-existing return migration. Check that
tests fail for the expected reason before implementing each behavior slice. Run OpenSpec
structural checks and project documentation checks, then record actual results in
verification.md.
No application test commands can be supplied by this documentation-only example.
