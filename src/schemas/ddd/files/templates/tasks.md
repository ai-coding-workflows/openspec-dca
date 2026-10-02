<!-- One tasks.md for the entire change. Only checkbox items belong to Apply.
Replace examples with real slices, owners, dependencies, and completion checks.
Read impact, domain-model-changes.md, specs when applicable, design, and
architectural-decisions.md. Preserve completed history; explain reopened tasks.
Open material model/decision questions block dependent work, not unrelated slices.

Keep maintained baseline paths read-only in planning/Apply. Changes to main specs,
models, shared views, ADRs/indexes, and catalog belong to a separately authorized
publication. Reference their assessment/design mappings in the non-checkbox handoff
below. Do not disguise publishing as an implementation or documentation checkbox. -->

## 1. Implementation and Contract Checks

- [ ] 1.1 {Owner and prerequisites: add/adapt the relevant test, implement the useful slice, refactor, and verify; explain test-first exceptions.}

## 2. Cross-owner Integration and Change-local Documentation

- [ ] 2.1 {Check real-adapter guarantees, cross-owner behavior, failure cases, compatibility, and migration where applicable; name evidence.}
- [ ] 2.2 {Prepare or update the referenced model/view/ADR drafts inside this change and check their consistency with the implementation and assessments.}

## 3. Apply Evidence and Publication Preparation

- [ ] 3.1 {Record actual checks, reviewed revisions, baseline plus delta/model basis, remaining gaps, and acceptance evidence in verification.md.}
- [ ] 3.2 {Compare maintained baseline paths with their pre-Apply snapshot, including added/deleted/renamed files and prior dirty work; prepare the Integration handoff without publishing.}

<!-- Relevant tests may already exist. Do not force failing tests for documentation
or unchanged behavior. Pick the right level, not an E2E test for every scenario.
Check preparation only after it is complete; it does not mean publication happened.
Ready for acceptance is not Accepted. A failed/not-run/partial check remains visible. -->

## Integration Handoff - Not Executed by Apply

Publication status: Pending
Authorization / operator reference: {actual separate authorization, or Not yet authorized}

| Source of publication details | Required integration effect / prerequisite | Actual publication evidence |
| --- | --- | --- |

<!-- Use ordinary table rows, NOT checkboxes. Reference model mappings in
domain-model-changes.md, view mappings in design.md, and ADR mappings in
architectural-decisions.md; do not copy those target inventories here. Include spec
sync, model/view/ADR promotion, reference/index updates, and catalog registration
only where required. Existing main specs are a prerequisite for catalog entries.
No handoff rows are needed for unaffected sources; state No publication needed
only when that is genuinely true of the change.

This is a handoff in the single tasks.md, not a second implementation backlog and
not a new native integration artifact/command. Before separately authorized writes,
re-read the integration baseline, reconcile overlapping changes and ADR IDs, and
resolve staged/durable links. Keep publication pending until actually performed.
Archive only after real acceptance, required checks, and handoff resolution; native
requirement sync alone does not complete non-spec updates. All Apply tasks checked
means Apply work finished, NOT the baseline was updated or the change was accepted. -->

{{hook:template.tasks}}
