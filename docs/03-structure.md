# Organizing contracts and changes

Keep OpenSpec's `specs` and `changes` roots. Organize the capability paths below
them around contract ownership. The same relative path identifies the owner in a
main spec and in a change's delta spec.

This guide uses **spec owner** as the general term: a feature, domain, port,
adapter, technical capability, or system responsibility can own a spec. Not every
OpenSpec capability path is a user-facing feature. A **documentation scope** identifies
a responsibility being described. It need not yet own a native `spec.md`; a handbook
page, architecture fragment, or ADR alone does not create a spec-owner catalog entry.

```text
openspec/
├── README.md                             documentation entry point
├── config.yaml
├── catalog.json                          optional DDD ownership/dependency map
├── schemas/openspec-ddd/                  workflow schema and templates
├── ddd/ddd.py                            optional read-only helper
├── system-architecture/
│   ├── README.md                          handbook scope and reading order
│   ├── SUMMARY.md                         optional mdBook navigation
│   ├── goals-and-stakeholders.md
│   ├── constraints.md
│   ├── system-context.md
│   ├── solution-strategy.md
│   ├── building-blocks.md
│   ├── runtime.md
│   ├── deployment.md
│   ├── crosscutting-concepts.md
│   ├── architectural-decisions.md        index of scoped ADRs
│   ├── quality-requirements.md
│   ├── risks-and-technical-debt.md
│   └── glossary.md
├── specs/
│   ├── contexts/lending/
│   │   ├── domain/
│   │   │   ├── model.md
│   │   │   └── spec.md
│   │   ├── ports/loan-store/spec.md
│   │   ├── features/return-equipment/
│   │   │   ├── spec.md
│   │   │   └── architecture/runtime.md
│   │   ├── adapters/in/http/spec.md
│   │   ├── adapters/out/database/
│   │   │   ├── spec.md
│   │   │   └── architecture/mapping.md
│   │   ├── architecture/                     context-wide views, when useful
│   │   └── architectural-decisions/adr-lending-001.md
│   ├── technical-capabilities/document-rendering/
│   │   ├── spec.md
│   │   ├── ports/                            independent contracts, when useful
│   │   ├── adapters/
│   │   ├── architecture/
│   │   └── architectural-decisions/
│   └── system/
│       ├── composition/spec.md
│       ├── composition/architecture/wiring.md
│       ├── ports/                            system-owned contracts, when useful
│       ├── adapters/                         genuinely system-owned boundaries
│       └── architectural-decisions/
└── changes/
    ├── record-return-condition/
    │   ├── .openspec.yaml
    │   ├── proposal.md
    │   ├── impact.md
    │   ├── specs/contexts/lending/.../spec.md
    │   ├── design.md
    │   ├── tasks.md
    │   ├── architectural-decisions/         proposed decisions, when useful
    │   └── verification.md                  actual delivery evidence
    └── archive/
```

This is the naming baseline for the guide, showing available locations rather
than a checklist of files to create or the current inventory of the worked example.
Its proposed ADR remains change-local until accepted; the tree also shows its
possible durable destination. Create only owners and views you need. Flat capability
paths also work: the DDD model does not require a fixed folder hierarchy.
OpenSpec 1.13.1 supports the nested paths used here; this guide tests their discovery,
validation, and merge. Keep paths stable: moving a capability is a deliberate
migration, not an incidental naming cleanup inside a behavioral change.

The root holds navigation, configuration, and the three major areas. The handbook
explains the whole system, including goals, constraints, and its external boundary.
Keep those topics together in `system-architecture/`, not as unrelated root files.
`specs/` holds owned contracts and their local models, architecture, and decisions;
`changes/` coordinates proposed work. The handbook README supplies arc42 reading
order; handbook topic filenames need no chapter numbers. These conventions describe
the adopting project's documentation, not the numbered chapters of this guide.

### Ownership scopes, not mandatory layers

`specs/contexts/<context>/` groups a business model and its responsibilities.
`specs/technical-capabilities/<capability>/` groups an independently meaningful
technical capability. Both may own ports, adapters, views, and decisions.
`specs/system/` is for genuinely system-owned responsibilities such as composition
or a shared application boundary, not a second handbook at `specs/system/architecture/`.
Keep a system responsibility's detailed views near that responsibility.

Architecture-only reconstruction may document these scopes before any main specs
exist. Do not create placeholder requirements or catalog nodes to justify local
views. OpenSpec identifies native capabilities through their `spec.md` files;
ordinary models, architecture pages, and ADRs are not capabilities by themselves.
See [adoption](07-adoption.md) for the separate architecture-only entry route.

Use one responsible scope per definition or record. A cross-context interaction
does not automatically need a shared scope. Choose placement by ownership rather
than by technology, reuse count, or a desire for symmetric directories; see
[ports and adapters](02-software-architecture.md).

## Which owner defines the rule?

| Rule or information | Owner |
| --- | --- |
| Vocabulary, concepts, and state meanings | Domain model companion, when useful |
| Normative obligations and invariants for domain behavior | Domain spec |
| Successful save persists state and condition together | Storage port spec |
| Return accepts input, applies rules, and reports an outcome | Feature spec |
| JSON mapping and HTTP status codes | HTTP adapter spec |
| Database columns and transaction implementation | Database architecture fragment |
| Selected provider and wiring | Composition scope |

A storage adapter may refer to its port's guarantees without repeating them. If the
guarantee changes, its implementation and architecture may need work even when its
spec needs no delta. Record this disposition in `impact.md`.

## Needs, models, and requirements

A **need** explains the problem or desired outcome and who benefits. Record it in
`proposal.md`, or reference an existing goal in the handbook or its authoritative
stakeholder source. A separate needs document is not required, and a new need is
not needed for every domain rule, port guarantee, or adapter mapping. Requirements
may share a need or follow from existing constraints. State the source, scope, and
owner of a binding constraint; do not present a team decision as an externally
imposed restriction.

A **domain model** explains the meaning of concepts and their relationships. A
**requirement** states an obligation of its owning contract. A **scenario** makes
that obligation concrete through an observable example. Do not force definitions
into requirement-shaped statements or treat implementation tasks as stakeholder
needs.

Keep OpenSpec's `Requirement` and `Scenario` headings for normative behavior. Tailor
their content to the owner: domain invariants and transitions; feature outcomes and
failure behavior; port guarantees; adapter representations and mappings. Quality
requirements and cross-cutting constraints also need an owner and a suitable check;
they need not be forced into a user-interaction narrative.

## Documenting the domain model

Use a companion such as `domain/model.md` when requirements alone cannot explain
the domain clearly. Cover vocabulary, concepts, identity, relationships, value
meanings, and state semantics where useful. A small domain does not need a complete
inventory of DDD patterns. Where a domain spec exists, this is an additional
view of the same owner, not a new OpenSpec capability or a second specification
lifecycle. During architecture-only reconstruction, a scoped descriptive model can
exist before a spec; link observed evidence and existing rules without inventing a
contract or a broken reference to a nonexistent `spec.md`.

Keep each definition authoritative in one place. Requirements should refer to the
model rather than independently listing the same values or redefining their meaning.
When a referenced definition changes, review its effect on those requirements and
their consumers. A model update does not replace a requirement delta when an
obligation changes.

For example, a historical return without a recorded condition can be valid historical data while a new return without a condition is rejected. Explain the meaning
of historical unrecorded data in the model; state the new-return obligation in the
domain spec. Do not replace this distinction with an invariant requiring every
historical return to have a recorded condition.

Keep implementation choices such as database columns and class layout in
architecture documentation. Diagrams and state tables may summarize the model,
but identify the authoritative definition rather than maintaining competing rules.

Name proposed model edits and affected requirements in `impact.md` and `design.md`;
track the durable update in `tasks.md`. Keep proposed wording change-local or clearly
marked as proposed. Update the maintained model consistently with the accepted
contract baseline, and record any deliberately early-synced state. Model-only
clarifications still need review; changed obligations also need requirement deltas.
The optional companion is not automatically merged by native requirement sync.
The [domain-model template](08-templates.md#domain-model-companion-template) supplies
optional prompts for meaning, relationships, historical data, and rule references;
it does not require every domain to have every section.

## Three identifiers with different jobs

| Identifier | Example | Used by |
| --- | --- | --- |
| Catalog alias | `lending.return` | DDD helper and natural-language agent input |
| OpenSpec capability path | `contexts/lending/features/return-equipment` | Native spec lookup and delta destination |
| Change name | `record-return-condition` | Native change commands and `--change` |

The catalog maps aliases to main `spec.md` files. OpenSpec itself does not resolve
these aliases. Its requirement merge also uses the exact `### Requirement: ...`
names inside a capability, so preserve those names in MODIFIED deltas. A separate
stable requirement ID may be included in the name if that is your project convention.

## Dependency direction

`depends_on` means “consumes this owner's contract.” The feature and database adapter
both consume the storage port; the port does not depend on its database provider.
Use prerequisite order to understand contracts, then review transitive consumers
of changed guarantees. External callers may not appear in the catalog and still
need review.

Catalog metadata is optional. Small projects can write the relationships directly
in `impact.md`. With a catalog, list architecture and ADR paths explicitly, including
shared-scope decisions. The helper does not discover them by convention. New owners
are proposed in the change, then registered once their main specs are created.
