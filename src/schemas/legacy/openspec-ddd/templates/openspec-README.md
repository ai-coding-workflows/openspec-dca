# OpenSpec: {project name}

<!-- Starter for openspec/README.md, not an application architecture assertion.
Replace the project name; remove authoring comments and irrelevant material. -->

## Reading the project

`system-architecture/` is the editable system handbook: goals and stakeholders,
constraints, external system context, shared design, quality concerns, and risks.
Its `README.md` describes scope and reading order when the handbook is established.
Keep only useful pages; the template collection is not a completed baseline.

`specs/` contains actual owned contracts and useful local models, views, and decisions.
Contexts own coherent business meaning. `technical-capabilities/` is for independently
meaningful technical responsibilities, not every utility. `system/` holds genuine
system-owned contracts/details, not a second handbook. Architecture-only scopes can
exist without a placeholder spec or catalog node. Create only necessary scopes.

`changes/` contains native delivery efforts and `changes/archive/` their history.
Read a change's baseline together with its deltas, impact, design, and tasks. Its
verification evidence records actual checks and acceptance, not merely file presence.
An explicitly selected architecture-only reconstruction uses its separate approved
runtime plan; it does not create specs, needs, or a native change just to document code.

## Configuration and template library

`config.yaml` is the live project configuration. The selected native schema is
`schemas/openspec-ddd/schema.yaml`. Reusable sources are in
`schemas/openspec-ddd/templates/`; start with its `README.md` for destinations.
Only proposal, impact, specs, design, and tasks are native artifact IDs. Other files
are selective support templates or handbook starters, not automatic workflow phases.
Merge the agent guidance into the project's actual agent instructions. Storing it
here does not register commands or guarantee that an agent has read it.

`catalog.json` and `ddd/ddd.py` are optional aids when installed. Preserve existing
catalog entries. Dependencies mean contract consumption, and directory names do not
change the catalog schema. Documentation may exist without a corresponding spec owner.

## Documentation lifecycle

Keep one authoritative definition or editable view. Model companions explain meaning;
specs own obligations; architecture describes implemented or explicitly proposed design.
Scoped `architectural-decisions/` holds records. The handbook's `architectural-decisions.md`
is an index, not copied rationale. Acceptance, implementation, and verification differ.
Requirement sync does not update models, handbook/local diagrams, ADRs, or the catalog.
Track and review those updates explicitly, with the inspected revision and actual results.
