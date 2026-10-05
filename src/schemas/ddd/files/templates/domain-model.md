# {Context or responsible scope}: domain model

{Explain the model's purpose and scope in two or three sentences, before any implementation or change history.}

<!-- Optional model support template, NOT the template for the required domain-model
artifact. That assessment uses domain-model-changes.md. Use this template only when
one substantial model draft or maintained companion is useful; a small model may
remain in an identified spec section. No additional native artifact is introduced.
During planning/Apply, write a draft inside the change and reference it from the
assessment; keep maintained targets unchanged. Remove irrelevant headings and all
authoring comments. Label proposed versus observed/current meaning honestly in drafts.
Do not force entities, fields, states, or diagrams that do not apply.

The assessment explains what changes and why, sources, Before/Proposed comparisons,
compatibility, approval questions, and publication mappings. This model explains what
the concepts mean and how they relate. Do not copy the assessment or publication log
into the model. Keep inspected revisions and evidence in short references; task progress,
authorization history, and publication status belong in the assessment/handoff/evidence.
Implementation rationale belongs in design/views/ADRs, not conceptual definitions. -->

## Concepts and Vocabulary

{Define each affected concept in ordinary language. Explain the distinctions a reader needs to interpret the model.}

<!-- Define each meaning once. A compact concept table can help, but use focused prose
for conditions and exceptions rather than wide cells. Use the domain's vocabulary,
not an inventory of implementation classes, database tables, or mandatory DDD patterns.
A technical responsibility may have a conceptual model without business entities. -->

## Identity and Relationships

{Describe applicable identities, relationships, ownership boundaries, and distinctions between similar concepts.}

<!-- Answer how concepts relate and what identifies them. Include relevant cardinality,
lifetime, or ownership distinctions when established. If identity is not applicable,
explain that briefly rather than inventing an ID. Use a small diagram only where it
makes relationships clearer; label its scope and relationship semantics and keep one
editable source. A diagram or list of type names alone is not a model definition. -->

## Values and Meaning (when relevant)

{Explain significant attributes or value concepts, allowed values, and the meaning of optional or unknown information.}

<!-- Use a small field/value table when it clarifies meaning. Distinguish absence,
unknown, an explicit clear, and a default where the model does; do not equate them
merely because an implementation uses null. Preserve exact identifiers and supported
values without inventing fields. Technical serialization/mapping details belong in a
separate short representation section only when useful, not in place of semantics. -->

## Invariants and Rule References

{Explain valid and invalid combinations or relationships, with references to their owning requirements or observed sources.}

<!-- Explain enough meaning to interpret a concrete instance. Normative obligations
and scenarios remain in the owning specs; cite exact paths/names or existing stable IDs,
not a second editable rule set. Describe derived summaries as such. For architecture-only
reconstruction without contracts, cite observed behavior and uncertainty instead of
inventing obligations, goals, acceptance, or missing historical values. -->

## Lifecycle and Historical Data (when relevant)

{Explain meaningful state changes, what survives them, and how existing data differs from what new operations may produce.}

<!-- Explain relevant creation, modification, removal, or read/resume behavior. Do not
force a state machine on a static value model. A state table or diagram is a summary of
owning transition/invariant rules, not an independent normative source. Unknown old
behavior remains unknown; valid stored representations do not automatically authorize
an equivalent new transition. -->

## Examples (when useful)

{Show a representative instance or composition and explain the resulting identities, relationships, values, or state. Include a contrasting invalid or unknown case when it clarifies a significant distinction.}

<!-- Examples demonstrate the definitions and their boundaries; they are not new
requirements or executed tests. Prefer concrete, small examples over process narration.
Check each example against the definitions and owning requirements. -->

## References

{Link the owning contract, relevant ADR/view, and useful source representations. Put inspected revisions or reconstruction evidence here only when needed.}

<!-- In a change-local draft, link the before/after assessment instead of recreating it.
Keep representation mappings separate from conceptual definitions. Preserve exact paths
and uncertainty; code existence alone does not establish model completeness or approval.
Material unresolved semantic questions belong in the assessment with the work they block;
a model may retain a short linked question where needed to prevent a false definition. -->

<!-- Semantic review before publication: can a product-informed reader explain the
concepts and interpret a concrete example without reading change history or implementation?
Check applicable identities, relationships, values/unknowns, invariants, and lifecycle;
preserve conditions/exceptions and reconcile examples with owning requirements. Heading
presence or native artifact readiness is not evidence of this review. Reuse/no-change
assessments need no new model or invented sections. During separately authorized integration,
merge reviewed meanings into a coherent model against the current baseline; do not promote
assessment prose wholesale or overwrite newer content with a stale full draft. Native spec
sync does not merge models, and no automatic template/spec/model sync is implied. -->
