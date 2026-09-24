## Working with OpenSpec DDD

Merge these instructions into the project's existing agent instructions. Follow the
configured native workflow; do not introduce a parallel lifecycle or approval process.
Keep artifacts proportionate. Remove unused optional sections rather than filling
all templates with boilerplate; preserve required native artifact structure.

### Select and understand the work

Resolve the change name or spec path from the request and repository state. Ask only
when a material ambiguity remains; do not request information already available.
Catalog aliases identify owners; native spec commands use capability paths. Archived
changes are history: later implementation belongs in a new change.

Before planning revisions or implementation, read relevant main specs, active deltas,
impact, model companions, architecture, and ADRs. Read prerequisite contracts first.
The target is the baseline plus applicable deltas, not either in isolation. Identify
any deliberate early sync and the implementation still outstanding.

### Ownership and granularity

A feature is a lasting capability and the default home for related use cases. A use
case has an actor goal and recognizable outcome; a field validation or repository
call is normally a step. Do not create separate owners merely for classes or endpoints.

A need explains purpose or value in the proposal or a referenced goal. Requirements
state observable obligations. A domain-model companion explains meaning, identity,
relationships, and state semantics where needed. Keep one authoritative definition;
changed meanings that alter obligations also require the relevant contract deltas.
Distinguish supported historical data from the rules for new commands or transitions.

`in` and `out` are relative to the application core and describe driving/driven roles,
not the direction of returned data. Feature specs normally own behavior exposed
through inbound ports. Separately document a port only when an independent contract
is useful. Adapters own boundary-specific mappings and reference consumed contracts.
Keep the existing flat `ports/` layout unless a deliberate migration is justified;
do not add duplicate inbound specs or require spec paths to mirror code packages.

Use the optional catalog as a reading and consumer-review aid, not as proof of the
actual architecture. `depends_on` means contract consumption; keep code and test links
separate. Use the read-only helper only if installed. Review external callers and
composition where relevant, and retain reasons for reviewed-but-unchanged consumers.

### Ports and adapters across ownership scopes

Ports and adapters are not restricted to bounded-context directories.
Place them with the context, module, or explicitly owned system/integration
scope responsible for their contracts and implementation responsibilities.

Cross-context communication does not automatically imply shared ownership.
A consuming context may own a required port and an adapter that translates
to another context's published contract. Keep the two contracts distinct
where their meanings or guarantees differ; do not introduce duplicate
specifications where a separate contract adds no value.

Reusable technical capabilities may own ports and adapters in a named
module. A shared application adapter may serve several contexts while
referencing their contracts. Sharing a process, server, or library alone
does not require shared contract ownership.

Define `in` and `out` relative to the documented core or boundary.
For integrations spanning several cores, state each boundary role rather
than imposing an ambiguous global direction.

Do not centralize domain-specific contracts merely because several contexts
use similar technology. Keep business orchestration explicitly owned rather
than hiding it in adapters or composition.

### Plan and refine

Keep one design and task list per coherent outcome. Include necessary domain/port
refinements and explain added owners without silently expanding unrelated scope.
Reconcile proposal, impact, deltas, design, and tasks after scope or behavior changes.
A contract-delta disposition needs actual delta content for that owner, not just a
completed specs artifact. Preserve exact requirement names and valid completed history.
Obtain current native artifact instructions before creating missing files or making
substantial artifact rewrites.

Plan enough to implement the next slice safely, not every test or implementation
detail in advance. Record assumptions and which open decisions block which work.
Respect decisions and authorization already given; do not invent approvals or decide
unresolved material behavior/compatibility choices by silently writing code.

## System architecture and owned documentation

Use `openspec/README.md` as the documentation entry point.

The shared architecture handbook lives in `openspec/system-architecture/`.
It explains system goals, constraints, context, the current design, and
crosscutting concerns. Read its overview and the sections relevant to the
selected change, together with the affected owners' local documentation.

Keep detailed models, contracts, architecture views, and architectural
decision records with their responsible owners. The handbook references
or includes these sources without maintaining competing copies.

Use `technical-capabilities/` for independently meaningful technical
contracts and `architectural-decisions/` for scoped decision records.

For each change, identify affected handbook sections and local views in
impact and design. Track their updates in tasks and review their consistency
with the implemented design in verification. Keep proposed and current
states explicit. Spec synchronization does not update these documents.

### Architecture views and diagrams

Maintain a context overview and a high-level structure diagram for the documented
system. A concise table may replace a simple context diagram. Reuse adequate existing
views. When adopting this policy, identify missing baseline views as explicit work;
do not turn an unrelated small change into a whole-system documentation rewrite.

For each architecture-relevant change, review affected views in impact and explain
necessary proposed views in design. Require focused diagrams where a changed boundary,
dependency, significant interaction, or deployment arrangement would otherwise remain
ambiguous. Include relevant failure paths in selected runtime views; use domain-model
diagrams for difficult state or relationship semantics. No diagram is required per
feature, use case, requirement, or class.

Each view needs a question, scope, clear status, and labeled relationship semantics.
Do not conflate contract consumption, source dependencies, runtime calls, data flow,
or deployment. Maintain one editable diagram source using project-supported tooling;
renderings and published includes are derived views. Keep proposed views identifiable,
name durable destinations, and track updates in the shared tasks. Review maintained
views against implementation before closure; successful rendering alone is not enough.

### Tests, traceability, and closure

Use test-first slices for new or changed executable behavior: observe the expected
failure, implement, then refactor with tests passing. Reuse adequate existing tests;
record a reason when this order is not appropriate. Protect behavior-preserving
refactoring with suitable regression tests; documentation-only work needs no artificial
red phase. A Markdown scenario is not an executed test.

Choose checks by obligation and risk: domain tests for rules, use-case tests for
orchestration, port-conformance tests for applicable real adapters, adapter tests for
mappings, and selected integration/migration tests. Fakes alone do not establish real
adapter conformance. No universal code-coverage percentage or exhaustive advance test
list follows from this process; preserve any stricter project policy.

Link requirements to checks using existing stable IDs or capability path plus exact
requirement name. Do not rename requirements merely to introduce IDs during a change.
Use architecture code entry points for navigation; avoid hand-maintained line numbers
or a complete requirement-to-function matrix. Evidence may be many-to-many. Do not
use incomplete trace links as the sole basis for excluding tests.

Record actual results, tested revisions, acceptance findings, and remaining gaps in
verification.md. Cover changed requirements and affected baseline guarantees; shared
checks are allowed. Never invent test results, passing coverage, or acceptance. A test
reference is not a run; executed code is not necessarily behavior checked by assertions.

Keep model and architecture updates consistent with their stated baseline, and record
accepted-but-unimplemented states explicitly. Preserve accepted ADR reasoning; accept,
reject, or supersede decisions explicitly. Spec sync does not maintain these documents
or the optional catalog. Check required durable updates and obtain or reference the
project's actual acceptance decision before closure; advisory text is not a CI gate.
