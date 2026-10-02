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

During native planning/Apply, new or changed model/view/ADR content is prepared
inside the selected change. Record project-relative maintained destinations and
change-relative draft sources in the responsible assessment/design. Existing
baseline documents stay read-only; don't create placeholders to satisfy links.

The singular [architectural-decision.md](architectural-decision.md) is an individual
record. This directory's [architectural-decisions.md](architectural-decisions.md)
is the change assessment. Keep records distinct from assessment/index summaries.

## Apply versus publication

Only Apply work appears as tracked checkboxes in tasks.md. A non-checkbox Integration
handoff in that same file points to publication mappings and their actual status.
Apply may prepare and verify the handoff, but may not sync, archive, promote records,
write maintained model/view/spec files, or update the shared architecture documentation/catalog. All
checked tasks means Apply work is complete, not that the baseline is published.

Later publication requires explicit authorization, current-baseline reconciliation,
link/ID checks, and closure evidence. Requirement sync does not merge non-spec
content. These are agent/review rules, not an enforced path sandbox or a new command.

## Selected component support

{{hook:support-index}}
