## Working with OpenSpec DDD

### Entry points and scope

Read openspec/README.md, the relevant system handbook sections, and the project agent
instructions. The reusable library is openspec/schemas/openspec-ddd/templates/; its
files are starters, not an application baseline or automatically registered commands.
For native contract delivery, use the installed schema's artifact instructions. Resolve
an explicit change name or capability path. Catalog aliases are not native spec paths.
Read prerequisite contracts, baseline plus selected deltas, impact,
domain-model-changes.md and its sources/drafts, design, the change's
architectural-decisions.md assessment, and tasks. Read relevant owned views and
existing ADRs. Never implement archived changes.

### Writing for the person reviewing the change

Use the document language already chosen by the project; do not translate code
identifiers, field names, enum values, paths, or existing requirement headings.
Write for someone who understands the product but has not investigated this change.
Explain the operation and its consequence before using an implementation term.
Introduce necessary terms in ordinary words, then give the exact name in parentheses.
For example, describe a stored record of a completed request before calling it a
"durable receipt". Explain "atomic" by naming which changes must succeed together
and what is not guaranteed; do not use it as a synonym for all retry safety.

Start with a short overview, then the details needed to implement and verify it.
Keep full technical conditions, exceptions, optional values, identity rules, historic
data handling, and uncertainty. Split them into focused sections rather than deleting
them. Use short complete sentences. Do not turn a paragraph into a single table cell.
Use a compact overview table or short entries; long paths belong in a source/location
section with local references. References are navigation, not a new identifier system.

For model changes, name each concept or external mapping, identify Add/Change/Remove/
Rename/Document existing/Reuse where justified, and compare known current meaning
with the proposal. Label unknowns explicitly. Missing documentation is not evidence
that a class, field, or behavior is new. A changed source file is not automatically
a changed domain meaning. Distinguish domain definitions, external mappings, and
execution rules while keeping links between them. Show retained meaning and removals
explicitly; do not invent a model element just to complete a table.

For an unresolved decision, separate the question, observed facts, practical risk,
options, recommendation, and actual decision status. Describe each option's delivered
scope, deferred work, costs/risks, and tests under comparable headings. A recommendation
is not acceptance. Do not hide a verification prerequisite behind "no open questions";
name the exact work it blocks. Terms such as "shared core" need a responsible component
or an explicit note that the supplied sources do not yet identify it.

Check the rewrite against the source before finishing: every material rule, identifier,
condition, risk, open question, and evidence limitation must remain findable. Do not
invent old behavior, field names, publication targets, successful tests, or guarantees.
Keep native spec delta headings and task checkbox syntax unchanged. Readability does
not add an artifact, bypass a review, or authorize maintained-file writes during Apply.

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

Reconcile all seven artifacts when scope changes: proposal, impact, domain-model,
specs when applicable, design, architectural-decisions, and tasks. The two assessments
are always produced; reasoned reuse/no-change is valid and need not create a model or
an ADR. Impact identifies affected definitions; domain-model-changes.md specifies
proposed meaning once or links a single model draft. Design explains the approach;
architectural-decisions.md assesses record needs and destinations. An individual
record owns its detailed rationale; the assessment and design link rather than copy.
The existing skip_specs route affects specs only, not either assessment. Match each
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
Impact identifies create/update/reuse. The model assessment owns semantic drafts and
source-to-target mappings; the decision assessment owns ADR dispositions and mappings;
design owns proposed technical views. tasks.md tracks preparation and verification,
with a non-checkbox Integration handoff referencing those mappings. Keep changed
views inside the selected change during Apply. Reuse existing views without cosmetic
edits and record actual conformance findings; templates are not current diagrams.

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

### Apply boundary and separately authorized publication

In native planning and Apply, treat openspec/specs/**, openspec/system-architecture/**,
openspec/catalog.json, and all explicitly mapped maintained documentation targets as
read-only. This includes new main specs and maintained models, local views, ADRs, and
shared indexes. Do not create, edit, delete, rename, reformat, regenerate, or indirectly
write them. Do not invoke sync/archive or baseline promotion within Apply. Approved
code/test changes remain in scope; this is not a prohibition on implementation.

Prepare all proposed documentation in the selected change: domain-model-changes.md or
models/ drafts, delta specs, design.md or architecture/ drafts, and the decision
assessment with optional architectural-decisions/ records. Use exact project-relative
destinations and change-relative draft paths. An implemented change-local view is not
its published baseline. Main model meanings remain authoritative for the existing
baseline while the assessment defines the proposed revision; do not silently swap them.

Keep publishing actions OUT of Apply checkboxes. Record a non-checkbox Integration
handoff in tasks.md with source mapping references, prerequisites, actual authorization,
and publication status/evidence. Preparing it is Apply work; executing it is not.
If an old task conflicts, preserve its intent in that handoff and report the conflict;
do not publish to satisfy the checklist. Never create a main spec to satisfy the helper.
At Apply start record the baseline snapshot, including existing dirty files. At the
end check protected additions/deletions/renames/content; preserve unrelated user edits.
A prompt is not an enforced write boundary: use runner/permission checks where available.

When tracked work is finished, report verification and pending integration, then stop.
Later explicit publication re-reads the current integration baseline, reconciles
concurrent semantic/text changes, checks ADR IDs/links, and promotes accepted model,
view, and record revisions deliberately. Keep one editable maintained source and
preserve ADR rationale. A changed requirement uses a reviewed delta; non-spec documents
need explicit reconciliation, not a blind full-file overwrite. Native requirement sync
does not merge model/view/ADR/index/catalog content. Register new catalog owners only
after their main specs exist. Resolve the handoff and required acceptance/checks before
archive; an accepted ADR or all_done does not prove publication or implementation.

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
