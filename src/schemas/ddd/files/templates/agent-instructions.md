## Working with OpenSpec DDD

Read openspec/README.md, the selected schema's templates/architecture-policy.md, relevant
contracts and the project's implementation map before planning or changing code.
Use the selected active change and baseline plus its deltas/model revisions.
Write complete, precise sentences; distinguish evidence, proposals and decisions.
Keep one authoritative definition, one design and one Apply task list.

The seven artifacts separate outcome, impact, model meaning, requirement deltas,
implementation design, decisions and tasks. No-change model/ADR assessments are
brief; never create empty specs, ports, models or records for symmetry.
Context owners and inward dependencies are required. Map use cases to actual
application boundaries, ports, adapters and composition; test those dependencies
with the stack's real module/compile graph and negative controls. Real adapters
must meet their contracts; passing mocks alone do not establish this.

Planning stays change-local. During Apply all openspec/specs/** content, maintained
models, ADR records/status and the catalog are protected, including generated
writes and file moves. Snapshot these paths and preserve existing dirty work.
Apply may deliver explicitly mapped descriptive documentation outside that tree
in the local checkout, without changing protected meaning or decision status.

Apply stops after implementation, evidence and publication preparation. Separate
authorization covers baseline reconciliation, requirement sync, explicit companion
publication and dependent link/map/catalog updates. Sync alone does not publish
companions. Required unfinished publication blocks closure. Read the installed
config's archive guidance and helpers/README.md, then run closure.py before the
final archive move. The helper checks declared evidence, not semantic correctness
or authority. Wire required checks into project CI/wrappers; native command readiness
and advisory guidance do not enforce them. Shared-store writes/deployment are separate.

{{hook:project.agent-instructions}}
