## Approach

Add condition to the return input and loan model. Validate using the domain rule,
then persist the returned state and condition through the existing storage port.
The database adapter uses one transaction. HTTP validates the request shape and
maps domain/use-case outcomes according to its delta spec.

## Decisions and Alternatives

The proposed ADR-LENDING-001 records the atomic-save decision. Two separate durable
writes would permit partial returns. A needs-inspection condition is recorded, but
maintenance automation is outside this change. Domain values are not duplicated in
adapter-specific enumerations without an explicit mapping.

## Delivery Slices and Dependencies

1. Domain/input and port tests establish the target behavior.
2. Storage migration and adapter implement the stronger guarantee.
3. Feature, HTTP, and callers carry the condition through one integration flow.
4. Failure coverage, documentation, and acceptance evidence complete delivery.

## Architecture and ADR Updates

Update `openspec/specs/contexts/lending/features/return-equipment/architecture/runtime.md`
and `openspec/specs/contexts/lending/adapters/out/database/architecture/mapping.md`.
When accepted, promote the proposed ADR to
`openspec/specs/contexts/lending/decisions/adr-lending-001.md` with its actual status
and add that path to relevant catalog entries. No accepted ADR is superseded here.
These are explicit implementation tasks, not OpenSpec spec-sync side effects.

## Compatibility, Migration, and Risks

Keep the stored condition nullable for historical returns; only new return commands
require it. Coordinate callers and service deployment in the teaching scenario.
Before release, verify that rollback preserves newly collected values. A real rollout
needs concrete deployment and rollback commands from its application repository.

## Verification

Use domain, port-conformance, feature, HTTP, and end-to-end failure tests. Include
invalid conditions and pre-existing return migration. Run OpenSpec structural checks
and project documentation checks, then record actual results in verification.md.
No application test commands can be supplied by this documentation-only example.
