# OpenSpec: {project name}

Use the selected schema and the project's adopted agent instructions. The reusable
architecture policy is in the selected schema's templates/architecture-policy.md;
it is a policy, not evidence that this project's architecture is implemented.

## Project entry points

Record the actual context/spec roots, implementation map, accepted decisions,
local/CI check commands, definition/glossary locations and documentation roots here. For a new project use the
schema's project-setup.md prompt to establish only the justified foundation.
Suggested implementation-map destination:
openspec/specs/system/composition/architecture/implementation-map.md.
Do not link a destination until it exists; preserve its planned location in the change.
The DDD glossary indexes concepts AND named processes. Reuse an existing glossary, or
use openspec/glossary.md; definitions remain with their domain model or feature owner.
The schema's glossary.md template is navigation, not an additional behavior contract.

## Change lifecycle

Use proposal, impact, domain-model, specs, design, architectural-decisions and tasks.
No-change model/ADR assessments need no new companion. Specs may be omitted only
through the installed CLI's supported non-behavioral-change route, never dummy deltas.
Keep planning and protected model/view/ADR drafts inside the selected change.
Apply implements code/tests and mapped descriptive docs outside openspec/specs/**;
the protected baseline and catalog remain unchanged.

Integration is separately authorized: reconcile the latest baseline, merge
requirement deltas, publish needed companions, fix dependent links/maps/catalog,
record final evidence and pass the closure helper before the final archive move.
See the selected schema's helpers/README.md for commands and limits. Neither an
all-done task list nor native sync automatically publishes non-spec documentation.

The optional catalog records contract consumption, not code dependencies or task
order. Add owners only when real main specs exist; use ddd.py/check.py for their
existing structural checks. Architecture checks belong to the project's toolchain.

{{hook:project.readme}}
