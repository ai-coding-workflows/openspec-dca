<!-- Start with the practical effect of this change and who or what is affected.
Tables are for a short comparison, not paragraphs joined by semicolons. Where paths
make a table unreadable, use local references and list each exact path and purpose
below it. Preserve all relationships and known limits; do not guess missing ones. -->

## Starting Point and Context

<!-- Feature/use-case outcome; relevant main specs, prerequisite contracts, domain
model, maintained architecture documentation sections, owned views, and architectural-decisions/.
Use real paths and source/revision references. Record uncertainty instead of inventing
boundaries. A capability path differs from a catalog alias or a code package. -->

## Owner and Consumer Review

| Owner / exact capability path | Relationship | Disposition | Reason / needed change |
| --- | --- | --- | --- |

<!-- Dispositions: contract delta, documentation only, implementation only, unchanged,
unresolved. Match every contract-delta owner to actual delta files and rule changes;
review unexpected deltas in the opposite direction. Glob existence is not coverage.
Review prerequisite/transitive consumers plus callers/composition outside the catalog.
Transitive impact is not an automatic edit list. With no catalog, describe relevant
contract dependencies here; do not infer them from source imports alone.

Identify potentially affected definitions and requirements. Their precise proposed
meaning belongs in domain-model-changes.md or its single linked draft, not this
inventory. A definition change altering obligations needs deltas, not a documentation-
only label. Flag historical data versus new-operation semantics for the assessment.
Cross-context use does not imply shared ownership. Identify responsibility, provided/
consumed contracts, translations, and the core relative to which in/out is defined.
An architecture-only scope without a main spec is not a catalog spec owner. -->

## Additional Owners

<!-- Necessary domain/port or other owners added to this coherent effort and the
reason reported to the user. Reconcile proposal scope without broadening it silently.
During planning/Apply, do not register owners or create main specs. Catalog updates
require actual main specs and a separate publication authorization after review. -->

## Compatibility and Decisions

<!-- Agreed behavior, migration/rollback, relevant external callers, and actual decision
references. For unresolved material choices, name the work they block. Independent
slices may proceed. Neither shared context nor diagram work authorizes unrelated edits. -->

## Architecture and Delivery Consequences

| Model / architecture documentation section / local view / ADR | Action | Reason and affected rules | Authoritative / durable path |
| --- | --- | --- | --- |

<!-- Action: create, update, or reuse. Keep this inventory here and reference it from
design and both assessments. This inventory is initial impact, not duplicate draft
text or a second execution plan. A short list can replace the table. Include relevant
maintained architecture documentation pages, local architecture/ views, domain/model.md,
diagram sources, and scoped architectural-decisions/ records/index updates.

Review relevant existing views and identify material gaps. For significant architectural changes,
explain which diagrams answer the question or why existing views suffice. No diagram
per feature or unrelated whole-system rebuild is required. Name gaps and useful slices;
do not create empty chapters. domain-model-changes.md owns model mappings, the
change-local architectural-decisions.md owns ADR dispositions/mappings, and design
owns technical drafts. Keep maintained destinations read-only during planning/Apply.
Sync does not update models, architecture documentation pages, diagrams, ADRs, or catalog metadata. -->

{{hook:template.impact}}
