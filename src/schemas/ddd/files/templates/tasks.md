<!-- One tasks.md for the entire change. Only checkbox items belong to Apply.
Replace examples with real slices, owners, dependencies, and completion checks.
Read impact, domain-model-changes.md, specs when applicable, design, and
architectural-decisions.md. Preserve completed history; explain reopened tasks.
Open material model/decision questions block dependent work, not unrelated slices.

Planning leaves maintained destinations unchanged.
Apply updates mapped descriptive documentation outside openspec/specs/** in the development checkout.
Track actual outside-tree updates and checks beside implementation, plus preparation/checks
of change-local local-architecture/model/ADR proposals. Optional drafts alone are not outside-tree delivery.
The entire openspec/specs/** tree remains read-only during planning and Apply.
This includes creation, edits, deletion, renaming, and indirect/generated writes, regardless of file type.
During Apply, maintained model companions, ADR records, and openspec/catalog.json also remain
protected wherever located. Keep sync/archive, local architecture publication and other protected
publication, shared-store writes, and deployment outside Apply checkboxes. Reference remaining
separate work in the non-checkbox handoff below. -->

## 1. Implementation and Contract Checks

- [ ] 1.1 {Owner and prerequisites: add/adapt the relevant test, implement the useful slice, refactor, and verify; explain test-first exceptions.}

## 2. Cross-owner Integration and Documentation Delivery

- [ ] 2.1 {Check real-adapter guarantees, cross-owner behavior, failure cases, compatibility, and migration where applicable; name evidence.}
- [ ] 2.2 {Update mapped maintained descriptive documentation outside openspec/specs/** and check it against the implementation; optional drafts alone do not complete delivery.}
- [ ] 2.3 {Prepare and check change-local local-architecture proposals for targets under openspec/specs/** and any model/ADR revisions; record exact publication mappings without writing maintained protected paths.}

## 3. Apply Evidence and Publication Preparation

- [ ] 3.1 {Record actual checks, reviewed revisions, baseline plus delta/model basis, remaining gaps, and acceptance evidence in verification.md.}
- [ ] 3.2 {Compare the entire openspec/specs/** tree and other protected files with their pre-Apply snapshot, including new/deleted/renamed paths: protected content unchanged, mapped outside-tree updates delivered, prior dirty work preserved; prepare the publication handoff for pending local views and other protected content.}

<!-- Relevant tests may already exist. Do not force failing tests for documentation
or unchanged behavior. Pick the right level, not an E2E test for every scenario.
Check outside-tree documentation delivery only after maintained targets and required checks are complete.
Checking local-view preparation or handoff readiness does not mean protected maintained publication happened.
Ready for acceptance is not Accepted. A failed/not-run/partial check remains visible. -->

## Integration Handoff - Not Executed by Apply

Remaining separate publication: {Pending / Complete / No separate publication needed, with reason}
Authorization / operator reference: {actual separate authorization, or Not yet authorized / Not applicable}

| Source of publication details | Required integration effect / prerequisite | Actual publication evidence |
| --- | --- | --- |

<!-- Use ordinary table rows, NOT checkboxes. Reference model mappings in
domain-model-changes.md, view mappings in design.md, and ADR mappings in
architectural-decisions.md; do not copy those target inventories here. Include spec
sync, local architecture publication under openspec/specs/**, model/ADR promotion,
dependent reference/index updates, catalog registration, and release/deployment only where required.
Publication of local views in the protected tree belongs to separately authorized sync/archive
integration, not Apply; native requirement sync does not publish those views. Actual descriptive
updates outside the protected tree belong in Apply tasks, not deferred handoff rows.
Existing main specs are a prerequisite for catalog entries.
No handoff rows are needed for unaffected sources; state No publication needed
only when that is genuinely true of the change.

This is a handoff in the single tasks.md, not a second implementation backlog and
not a new native integration artifact/command. Before separately authorized writes,
re-read the integration baseline, reconcile overlapping changes and ADR IDs, and
resolve staged/durable links. Keep publication pending until actually performed.
Archive only after real acceptance, required checks, and handoff resolution; native
requirement sync alone does not complete non-spec updates. All Apply tasks checked
means implementation, permitted outside-tree delivery, and change-local preparation finished,
NOT protected local views/contracts were published, the change was accepted, or a site/release was deployed. -->

{{hook:template.tasks}}
