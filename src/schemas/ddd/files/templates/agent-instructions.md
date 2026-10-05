## Working with OpenSpec DDD

### Entry points and scope

Read openspec/README.md, the relevant maintained architecture documentation sections, and the project agent
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

Distinguish the change assessment from a readable model. Assessments carry Before/Proposed
comparisons, sources, compatibility, approval questions, and publication mappings. Model
narratives explain concepts, applicable identities/relationships, values/unknowns, invariant
summaries, and lifecycle, with examples or diagrams where useful. Keep technical representation
separate and process metadata out of model definitions; concise references may remain. Do not
force a new model, entity, field, state, or extra artifact for reuse/no-change.

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
not add an artifact, bypass a review, or expand the mapped Apply write scope.

### Responsibilities and meaning

Keep one design and one task list per coherent change. Needs explain value in the
proposal or sourced architecture documentation/product goals; there is no mandatory need per owner.
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

Use the project's maintained architecture locations. Review relevant existing views
and identify material gaps. Record missing coverage instead of inventing
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
design owns proposed technical views and their delivery mappings. Planning keeps
proposals change-local; separate descriptive drafts are optional when useful. tasks.md
tracks actual descriptive-view updates outside openspec/specs/** during Apply, plus
preparation/checks of change-local local-view/model/ADR proposals. Its non-checkbox
handoff tracks protected publication at separately authorized sync/archive integration.
Reuse existing views without cosmetic edits and record actual conformance findings;
templates are not current diagrams.

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

Planning leaves maintained destinations unchanged and prepares proposals in the change.
Apply updates mapped descriptive documentation outside openspec/specs/** in the development checkout.
This includes component-authorized handbook/user pages, navigation, assets, and other mapped
outside-tree descriptive sources. Read current destinations, reconcile overlaps, and preserve
unaffected content and prior dirty work. This covers repo-local development sources, not a
shared canonical store, release, or site deployment.

The entire openspec/specs/** tree remains read-only during planning and Apply.
This includes creation, edits, deletion, renaming, and indirect/generated writes, regardless
of file type: specs, local descriptive architecture, models, diagrams/assets, records, and indexes.
During Apply, maintained model companions, ADR records, and openspec/catalog.json also remain
protected wherever located, including supersession/status. Do not invoke sync/archive or publish
protected content within Apply. Prepare and check local-view/model/spec/ADR proposals inside the
selected change, with exact maintained destinations and change-relative content references.
Local architecture publication under openspec/specs/** belongs to separately authorized sync/archive
integration; a checked proposal is not a current maintained view. In outside-tree mixed-content
descriptive files, preserve protected meaning/status and report staged or blocked revisions.
Descriptive status does not exempt a file from the directory-wide boundary. Keep one editable
maintained source. A view can be published without a main spec; never create a placeholder spec or
catalog entry for a link/helper. Maintain links only to existing durable sources; publication-dependent
links belong in the handoff, not maintained navigation to transient drafts or nonexistent targets.

Track outside-tree descriptive updates and change-local proposal preparation/checks in the
one Apply checklist. Keep sync/archive, local-view/model/ADR publication, catalog registration,
shared-store writes, and deployment OUT of Apply checkboxes. The non-checkbox Integration handoff
records remaining separate work, prerequisites, actual authorization, and status/evidence.
State No separate publication needed only when true; completed outside-tree edits are not pending
promotion, but local views inside the protected tree stay pending until actually published.
Preparing/checking the handoff is Apply work, not permission to execute it. Preserve any conflicting
task's intent in that handoff and report the conflict.

Snapshot the entire protected tree, other protected files, and mapped outside-tree targets at Apply
start, including prior dirty work. Compare additions/deletions/renames/content at the end: protected
paths remain unchanged and mapped outside-tree targets receive their planned updates. Check actual
permitted destinations and change-local proposals against the implementation. Optional drafts alone
do not complete outside-tree delivery; local-view preparation does not complete maintained publication.
Record results and limits without inferring acceptance from edits/tests. A prompt is not an enforced
write boundary: use runner/permission checks where available.

When tracked work is finished, report implementation, outside-tree delivery and proposal evidence,
and remaining integration, then stop. Separately authorized sync/archive integration re-reads the
baseline, reconciles local-view/model/spec/ADR changes, explicitly publishes mapped protected
companions, checks IDs and dependent links, and preserves actual acceptance/status and rationale.
Authorization for native requirement sync alone does not authorize companion publication.
Native sync does not merge local architecture or other non-spec content. Register catalog
owners only after main specs exist. Resolve the handoff and required acceptance/checks before archive;
all_done is neither acceptance nor permission to publish/deploy.

Before model publication, check whether a product-informed reader can explain its concepts
and interpret a concrete example without reading change history or implementation. Reconcile
examples and explanatory invariant summaries with owning requirements, preserving conditions
and exceptions rather than maintaining a competing rule set. Publish a coherent model from
reviewed changes, not assessment prose wholesale. Record actual semantic review in the existing
handoff/evidence; native artifact readiness and heading presence do not prove model clarity.

{{hook:project.agent-instructions}}
