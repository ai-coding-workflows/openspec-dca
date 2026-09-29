# {Context or responsible scope}: domain model

Status: {Current or Proposed; choose explicitly}
Scope: {bounded context or actual semantic responsibility}
Behavioral contract: {existing owning spec path, when present; otherwise omit}
Basis: {accepted contract baseline or proposed change; observed sources for reconstruction}

<!-- Optional full-model support template, NOT the template for the domain-model
artifact. That required assessment uses domain-model-changes.md. Instantiate this
only when a substantial single model draft helps, referenced from the assessment;
otherwise describe the focused semantic change there. During native planning/Apply,
write a draft inside the change, not to the maintained model. A small existing model
may remain in a clearly identified spec section. No automatic template/spec/model sync
is implied. In reconstruction without contracts, cite observations and existing sources;
do not fabricate specs, needs, business goals, acceptance, or new normative rules. -->

<!-- Present one named concept at a time. A small field or relationship table can
show meaning, identifiers, allowed values, and optional data more clearly than a
single paragraph. Keep technical mappings separate from domain definitions. In a
draft describing a change, link the before/after assessment rather than recreate it.
Unknown old behavior is not absence; newly documented meaning is not necessarily
new software. Preserve source-based conditions and show unresolved details. -->

## Purpose and Vocabulary

<!-- Meaning, important terms, value semantics, and scope. Keep each definition in one
authoritative source and link it. Do not duplicate value lists across model, feature,
and adapter. A referenced definition can affect obligations, so changes need impact
review. State contextual differences instead of imposing one global meaning. -->

## Identity and Relationships (optional)

<!-- Relevant identities, relationships, and boundaries. Include a model diagram when
needed, with explicit scope, semantics, and one editable source. Do not require an
inventory of DDD patterns or mirror implementation classes and database tables. -->

## States and Historical Data (optional)

<!-- Explain meanings and valid historical representations. What may already be stored
is not necessarily what a new operation is allowed to produce. Do not invent missing
historical values. Reference normative transition/invariant rules instead of independently
redefining them in a state diagram. Label any derived table or diagram as a summary. -->

## Behavioral Rule References

<!-- Link actual owning requirements and stable IDs if already used. Use exact paths/
names otherwise. For architecture-only documentation without specs, describe observed
behavior with evidence and uncertainty, not a new contractual guarantee. -->

## Open Questions (optional)

<!-- Material semantic questions, assumptions, affected decisions, and blocked work.
Native changes identify impact first, then specify proposed meaning and affected
requirements in domain-model-changes.md or this single referenced draft. Changed
obligations need deltas. tasks.md tracks preparation and a non-checkbox Integration
handoff. Keep maintained models unchanged during planning/Apply. Publish only with
separate authorization after current-baseline reconciliation; a stale full model
must not overwrite another accepted change. Reconstruction uses its approved runtime
plan. Implementation choices belong in design/views/ADRs, not model definitions. -->
