## Why

<!-- Explain the problem, intended outcome, and who benefits. Reference existing
architecture documentation/product goals and their sources when available. No need per contract rule
or separate needs hierarchy is required. Distinguish evidence from assumptions. -->

## What Changes

<!-- Describe observable changes, explicit exclusions, and compatibility breaks.
Keep one coherent effort. A feature may contain several actor-goal use cases;
a validation step, endpoint, or class does not automatically become a new owner. -->

## Capabilities

### New Capabilities

<!-- Exact intended paths relative to openspec/specs, or None. Use contexts/,
technical-capabilities/, or system/ only where a real responsibility merits a contract.
Do not list architecture-only directories, template files, or catalog aliases. -->

### Modified Capabilities

<!-- Exact existing capability paths and intended obligation changes, or None.
For a native change without behavioral changes, explain skip_specs: true in
.openspec.yaml and create no deltas. -->

## Acceptance

<!-- Observable success plus important rejection/failure and compatibility outcomes.
Identify material decisions that must precede dependent work. Reuse existing decisions;
do not treat this proposal or future tests as actual acceptance evidence. -->

## Impact

<!-- Starting owners, code/system boundaries, and likely architecture documentation/model/local-view
consequences. Include necessary domain/port changes with reasons. Detailed consumer
and documentation review belongs in impact.md, not a duplicate inventory here.
The domain-model and architectural-decisions artifacts assess meaning and decision
records explicitly. They remain required when specs are skipped; no new model or ADR
is forced. Keep planning proposals change-local. The entire openspec/specs/** tree remains
read-only during planning and Apply, including descriptive local architecture and assets/indexes.
Prepare/check local-view proposals inside the change for publication in separately authorized
sync/archive integration; native requirement sync does not publish those companions automatically.
Apply delivers mapped descriptive documentation outside that tree alongside implementation.
Maintained models/ADR records, catalog registration, shared-store writes, and deployment remain
separately protected wherever located. -->

{{hook:template.proposal}}
