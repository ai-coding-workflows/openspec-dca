# OpenSpec DDD template library

This library lives at `openspec/schemas/openspec-ddd/templates/`. The native schema
now selects **seven** artifact templates. Support templates and architecture documentation starters
remain separate: their presence does not generate extra workflow steps.

## Readable without losing the detail

The schema now requests plain-language explanations before technical detail. Model
assessments use an overview plus per-model current/proposed comparisons. Decisions
separate the problem, options, recommendation, and actual approval. Exact identifiers,
conditions, risks, and sources stay available in focused sections.

These changes affect writing and layout only. They do not add a workflow artifact,
rename a capability or native requirement, change an approval, or allow publication
inside Apply. A missing Before value must be labelled unknown, not invented.
Local source labels are navigation aids, not a new mandatory tracking system.

## Native artifacts

| Artifact ID | Template | Output inside the selected change |
| --- | --- | --- |
| proposal | [proposal.md](proposal.md) | `proposal.md` |
| impact | [impact.md](impact.md) | `impact.md` |
| domain-model | [domain-model-changes.md](domain-model-changes.md) | `domain-model-changes.md` |
| specs | [spec.md](spec.md) | `specs/<exact-capability-path>/spec.md` |
| design | [design.md](design.md) | `design.md` |
| architectural-decisions | [architectural-decisions.md](architectural-decisions.md) | `architectural-decisions.md` |
| tasks | [tasks.md](tasks.md) | `tasks.md` |

The order is proposal -> impact -> domain-model -> specs -> design ->
architectural-decisions -> tasks -> Apply. The dependencies express readiness,
not infallible approval or a ban on revising earlier work. The existing skip_specs
route skips specs only. Both assessments remain required and can briefly explain
Reuse existing / Not affected or No ADR required with real sources and reasons.

`domain-model-changes.md` owns the semantic change assessment or links its single
draft. It does not replace the durable model. `architectural-decisions.md` owns the
change's record assessment, not copied ADR rationale or a second architecture documentation index.
No generic optional artifact field, new review outcome, or decision approval engine
is introduced. Status based on file presence still needs semantic review.

## Support templates and destinations

| Source | Use and eventual destination |
| --- | --- |
| [config.yaml](config.yaml) | Merge into active `openspec/config.yaml`; do not replace local settings |
| [catalog.json](catalog.json) | Optional empty starter; never overwrite populated catalog data |
| [agent-instructions.md](agent-instructions.md) | Merge into the actual project instructions; this file does not register tools |
| [openspec-README.md](openspec-README.md) | Starter for `openspec/README.md` |
| [domain-model.md](domain-model.md) | Optional complete model draft; eventually the owned `domain/model.md` |
| [architectural-decision.md](architectural-decision.md) | One record; eventually a scoped `architectural-decisions/` file |
| [architecture.md](architecture.md) | One local/shared view; eventually an owned view or architecture documentation detail |
| [verification.md](verification.md) | Actual change evidence in `verification.md`, not a pre-Apply prerequisite |

During planning, prepare change-local model/view/ADR proposals and exact maintained-target
mappings in the responsible assessment/design. The entire openspec/specs/** tree remains
read-only during planning and Apply, including descriptive local views and their assets/indexes.
Prepare/check those views inside the change and record maintained publication in the handoff
for separately authorized sync/archive integration. Apply updates mapped descriptive sources
outside that tree; model companions, ADR records, and catalog remain protected wherever located.
Do not create placeholders for links or accept decisions through prose.

The [model assessment](domain-model-changes.md) records changes, evidence, comparisons,
and publication mappings. The optional [model](domain-model.md) explains concepts,
relationships, values/unknowns, invariants, and applicable lifecycle, using examples or
diagrams where useful. Publish coherent reviewed meaning, not the assessment wholesale.
A reader should understand the model without change history or implementation; record
that semantic review in existing handoff/evidence, not as an additional artifact.

The singular [architectural-decision.md](architectural-decision.md) is an individual
record. This directory's [architectural-decisions.md](architectural-decisions.md)
is the change assessment. Keep records distinct from assessment/index summaries.

## Apply versus publication

Only Apply work appears as tracked checkboxes in tasks.md. A non-checkbox Integration
handoff in that same file points to publication mappings and their actual status.
Apply updates and verifies mapped descriptive sources outside openspec/specs/**, including
component-authorized user pages/handbooks, alongside implementation. Optional outside-tree drafts
alone are not delivery. Apply prepares/checks change-local local-view/model/ADR proposals and their
handoff; it does not publish protected targets, sync/archive, register catalog entries, write shared
canonical stores, or deploy a site. All checked tasks means permitted delivery/preparation finished,
not that protected local views were published, the change accepted, or a site deployed.

Protected companion publication occurs only in separately authorized sync/archive integration,
with current-baseline reconciliation, durable link/ID checks, and actual closure evidence.
Native requirement sync does not merge local architecture or other non-spec content; publish mapped
companions explicitly. These are agent/review rules, not an enforced path sandbox or a new command.

## Selected component support

{{hook:support-index}}
