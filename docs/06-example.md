# A worked OpenSpec change

The equipment-lending example shows one fictional baseline and one proposed change.
It contains five main specs, four delta specs, one design, and one task list. It has
no application implementation; its seven delivery tasks are intentionally open.

## Follow the change

The request is: “record the condition of returned equipment.” Start from the return
feature, include the necessary domain and storage rules, then review consumers.
The database adapter needs implementation changes but already delegates its guarantee
to the port; it does not need a duplicate spec delta.

{{#include ../examples/equipment-lending/openspec/changes/record-return-condition/impact.md}}

## Baseline and proposed requirement

The baseline port requires a durable returned state and explicit failure behavior:

{{#include ../examples/equipment-lending/openspec/specs/contexts/lending/ports/loan-store/spec.md}}

The change replaces that requirement with its full updated content. Its exact name
is preserved, and the existing failure guarantee remains:

{{#include ../examples/equipment-lending/openspec/changes/record-return-condition/specs/contexts/lending/ports/loan-store/spec.md}}

Other deltas add the domain condition rule and update feature and HTTP behavior.
Unchanged requirements, such as rejection of unknown or already returned loans,
remain in the main spec and need not be copied into a delta.

## One delivery design and backlog

{{#include ../examples/equipment-lending/openspec/changes/record-return-condition/design.md}}

{{#include ../examples/equipment-lending/openspec/changes/record-return-condition/tasks.md}}

## Architecture has a separate lifecycle

The current runtime fragment still describes the illustrative baseline:

{{#include ../examples/equipment-lending/openspec/specs/contexts/lending/features/return-equipment/architecture/runtime.md}}

The proposed ADR stays with the active change until accepted:

{{#include ../examples/equipment-lending/openspec/changes/record-return-condition/decisions/adr-lending-001.md}}

An implementation task updates the current fragments and promotes the decision.
Spec sync does neither automatically. This also demonstrates how an arc42 chapter
can include local fragments without creating duplicate editable copies.

## Try the native commands

From this guide's root, prepare a disposable copy at a path that does not exist yet:

```sh
cp -R examples/equipment-lending /tmp/lending-ddd-demo
cp -R bundle/openspec/. /tmp/lending-ddd-demo/openspec/
cd /tmp/lending-ddd-demo
openspec schema validate openspec-ddd
openspec validate --all --strict --no-interactive
openspec status --change record-return-condition
openspec instructions apply --change record-return-condition --json
python3 openspec/ddd/ddd.py impact lending.domain
```

Expect planning artifacts to be present and **seven tasks remaining**. The integration
tests additionally demonstrate archive merging on another temporary copy. They test
text merging only, preserve unaffected requirements and architecture, and leave the
source example unfinished.
