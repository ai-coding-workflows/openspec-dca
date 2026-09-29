## Working with OpenSpec DDD

### Entry points and scope

Read openspec/README.md, the relevant system handbook sections, and the project agent
instructions. The reusable library is openspec/schemas/openspec-ddd/templates/; its
files are starters, not an application baseline or automatically registered commands.
For native contract delivery, use the installed schema's artifact instructions. Resolve
an explicit change name or capability path. Catalog aliases are not native spec paths.
Read prerequisite contracts, baseline plus selected deltas, impact, model definitions,
owned architecture, and relevant ADRs. Never implement archived changes.

### Responsibilities and meaning

Keep one design and one task list per coherent change. Needs explain value in the
proposal or sourced handbook/product goals; there is no mandatory need per owner.
Features are stable capabilities containing actor-goal use cases, not individual
validation steps or necessarily one endpoint/class. Requirements state obligations;
scenarios illustrate them. Keep explanatory meanings and relationships in a model
companion when useful, with one authoritative definition and explicit rule references.
Distinguish supported historical data from permitted new operations. Definition changes
that alter obligations require contract review and corresponding deltas, not only prose.

Use contexts/, technical-capabilities/, or genuine system/ responsibilities under
openspec/specs/. Technical capabilities need independently meaningful contracts; reuse
alone does not create an owner. Ports/adapters can belong to any appropriate scope.
Cross-context communication does not imply a shared contract. Define in/out relative
to the documented core, not data direction. Feature specs normally own behavior exposed
through inbound ports; do not duplicate it for symmetrical folders. Shared infrastructure
alone does not imply shared business ownership or justify hidden business orchestration.

Review consumers and external callers without turning the whole dependency graph into
edit scope. Keep depends_on as contract consumption and preserve catalog schema fields.
Add catalog owners only when main specs actually exist. Use exact names in MODIFIED
requirements; optional stable IDs do not replace native exact-name matching.

### Planning and architecture views

Reconcile proposal, impact, deltas, design, and tasks when scope changes. Match each
contract-delta disposition to actual rule changes and files. Preserve completed history;
record new work and explain reopened tasks. Resolve material decisions before dependent
work, respecting prior authorizations. Plan the next slice, not every input or function.

Keep the system handbook in openspec/system-architecture/. Establish a context overview
and high-level structural diagram for a declared baseline; a simple context may use a
table and existing suitable views count. Record missing coverage instead of inventing
empty pages or forcing unrelated changes to redraw the whole system. Require additional
diagrams when material boundaries, interactions/failures, or deployment remain unclear.
Do not require a diagram per feature. Use repository-supported notation and tooling.

Each view identifies its question, scope, status, editable source, and relationship
semantics. Distinguish calls, code dependencies, contract consumption, data flow, and
execution boundaries. Explain shared/cross-context responsibility and translations.
Keep models with domain meaning and technical views with their responsible scope.
Use one editable source; published output and images may be derived representations.
Impact identifies create/update/reuse, design explains proposals and destinations,
tasks track updates, and verification records actual conformance findings. Reuse
existing views without cosmetic edits. Templates are not implemented/current diagrams.

### Tests, traceability, and evidence

For changed executable behavior, use small test-first cycles and then refactor. Reuse
adequate existing tests; explain exceptions rather than manufacture red tests for
already conforming behavior, documentation, or behavior-preserving refactoring.
Check domain rules, use cases, boundary mappings, applicable real-adapter guarantees,
and relevant integration/migration/failure behavior. A fake alone proves no real-adapter
guarantee. Markdown scenarios are not executed tests. There is no universal coverage
percentage, exhaustive upfront test inventory, or mandatory E2E test per scenario.

Use useful owner-to-code entry points and requirement-to-check links, not a manually
maintained requirement-to-line matrix. Keep reusable mappings in one source. Record
actual results and the checked code/documentation revision, spec/model basis, environment,
and uncommitted snapshot where relevant. A link, covered line, or file presence is not
conformance. Recheck evidence affected by later changes. Ready for acceptance differs
from Accepted; record the actual decision and any authorized limitations separately.

### Durable documentation and closure

Coordinate accepted model meanings with the main contract baseline and explicitly
identify early-synced but unimplemented targets. Current architecture describes the
implemented design. Proposed views remain distinguishable. Scoped architectural-decisions/
records preserve choices and rationale; the handbook's architectural-decisions.md indexes
them without copying their text. Use actual decision authority for acceptance/supersession;
an accepted ADR is not proof of implemented behavior. Track relevant model, diagram,
handbook, ADR/index, and catalog updates explicitly: requirement sync performs none of them.
Do not treat checked tasks or successful rendering as automatic acceptance or closure.

### Separate architecture-only reconstruction

When the internal brownfield workflow is explicitly selected, use its approved runtime
plan and review artifacts. Do not create a native change, specs, needs, or tasks.md only
to document the existing system. Preserve product code, tests, current specifications,
manual documentation, and ADR history. Describe evidence-backed structure, not an ideal
DDD target. Mark observed source/configuration, documented intent, inference, unknowns,
and coverage limits. Test source does not prove a passing run; configuration does not
prove deployment. Never invent business goals, guarantees, or historical alternatives.

Architecture-only scopes can be navigated by the handbook without catalog entries.
Verification uses safe available approved checks with real outcomes and visible gaps.
Keep publication separate from architecture corrections. The internal workflow retains
success/issues reviews and blocked waiting for user input; ordinary resumption stays at
the same stage. Upstream recovery requires explicit authorization, not rerouting all
publication blockers. This native schema does not implement the host state machine.
