# Tasks: {change}

<!-- Replace examples with concrete numbered slices and commands. One Apply checklist;
no publication/deployment checkboxes. Preserve completed history as plans evolve. -->

## 1. Foundation or affected boundary checks
- [ ] 1.1 Establish or update the affected module map and executable dependency rules; prove forbidden dependencies fail and real modules are scanned.

## 2. Working slices
- [ ] 2.1 Test and implement the first observable use case through its application boundary and ports; check affected real adapters and production wiring.

## 3. Documentation and evidence
- [ ] 3.1 Deliver mapped outside-tree descriptive docs and verify change-local protected model/view/ADR proposals; preserve and compare protected baseline snapshots.
- [ ] 3.2 Record actual commands, revisions, results, and limitations in verification.md; prepare integration.json with pending states and references to the mappings.

## Integration handoff - not executed by Apply
<!-- Reference the authoritative design/model/ADR mappings; do not create a second
publication backlog. integration.json records closure state and final snapshots,
not another editable specification. Keep pending companion work visible.

Separate authorization is required to reconcile the current baseline, integrate
requirements, publish protected companions, and fix dependent references/catalog.
Run the closure helper after these writes and before the final archive move.
A required unfinished publication blocks closure. Deployment remains separate. -->

{{hook:template.tasks}}
