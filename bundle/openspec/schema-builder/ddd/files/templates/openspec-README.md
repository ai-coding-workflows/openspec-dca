# OpenSpec: {project name}

<!-- Starter for openspec/README.md, not an application architecture assertion.
Replace the project name; remove authoring comments and irrelevant material. -->

## Reading the project

Use the project's maintained architecture documentation when relevant.
Support templates describe proposed structure, not a completed baseline.

`specs/` contains actual owned contracts and useful local models, views, and decisions.
Contexts own coherent business meaning. `technical-capabilities/` is for independently
meaningful technical responsibilities, not every utility. `system/` holds genuine
system-owned contracts/details, not a second architecture documentation. Architecture-only scopes can
exist without a placeholder spec or catalog node. Create only necessary scopes.

`changes/` contains native delivery efforts and `changes/archive/` their history.
Read a change's baseline together with its deltas, impact, domain-model-changes.md,
design, architectural-decisions.md assessment, and tasks. Its
verification evidence records actual checks and acceptance, not merely file presence.

## Configuration and template library

`config.yaml` is the live project configuration. The selected native schema is
`schemas/openspec-ddd/schema.yaml`. Reusable sources are in
`schemas/openspec-ddd/templates/`; start with its `README.md` for destinations.
The seven native artifact IDs are proposal, impact, domain-model, specs, design,
architectural-decisions, and tasks. The model assessment writes domain-model-changes.md;
the decision assessment writes architectural-decisions.md in the change. Both can state
justified no-change/reuse results, including when specs are skipped. Full model, individual
ADR, architecture, evidence, and architecture documentation templates remain separate support sources.
Merge the agent guidance into the project's actual agent instructions. Storing it
here does not register commands or guarantee that an agent has read it.

`catalog.json` and `ddd/ddd.py` are optional aids when installed. Preserve existing
catalog entries. Dependencies mean contract consumption, and directory names do not
change the catalog schema. Documentation may exist without a corresponding spec owner.

## Documentation lifecycle

Keep one authoritative definition or editable view. Model companions explain meaning;
specs own obligations; architecture describes implemented or explicitly proposed design.
Scoped `architectural-decisions/` holds records. Any shared decision index
is navigation, not copied rationale. Acceptance, implementation, and verification differ.
Requirement sync does not update models, architecture documentation/local diagrams, ADRs, or the catalog.
During native planning/Apply, keep the maintained specs/models/views/ADRs, architecture documentation,
and catalog unchanged. Stage proposed content in the selected change and prepare its
non-checkbox Integration handoff in tasks.md. Baseline publication and archive require
separate authorization and reconciliation against the current integration baseline.
All checked Apply tasks are not publication or acceptance. Track actual results and
revisions at each step.

{{hook:project-guidance}}
