## Why

Lending staff need to know whether returned equipment is usable or needs inspection.
A completed return currently records only that the loan ended.

## What Changes

Record a domain-valid condition on every new completed return. Save it together
with the returned state and carry it through the return feature and HTTP boundary.
**BREAKING:** the return request now requires a condition. For this example, all
callers are controlled by the team and a coordinated rollout is an explicit assumption.
Automatic maintenance scheduling is outside scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `contexts/lending/domain`: define recorded return conditions.
- `contexts/lending/ports/loan-store`: persist condition and state together.
- `contexts/lending/features/return-equipment`: require and pass a valid condition.
- `contexts/lending/adapters/in/http`: map and validate the request field.

## Acceptance

A usable or needs-inspection return is saved with its condition. Missing or unknown
conditions, unknown loans, and repeated returns are rejected. A failed save leaves
the stored loan unchanged. Pre-existing returns retain an explicit unrecorded
condition; migration never guesses their historical condition.

## Impact

One change spans four contract deltas and a database implementation adaptation.
See impact.md for review of owners, callers, and architecture.
