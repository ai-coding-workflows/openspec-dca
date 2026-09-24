# Organizing contracts and changes

Keep OpenSpec's `specs` and `changes` roots. Organize the capability paths below
them around contract ownership. The same relative path identifies the owner in a
main spec and in a change's delta spec.

This guide uses **spec owner** as the general term: a feature, domain, port, or
adapter can own a spec. Not every OpenSpec capability path is a user-facing feature.

```text
openspec/
├── config.yaml
├── catalog.json                          optional DDD ownership/dependency map
├── schemas/openspec-ddd/                  workflow schema and templates
├── ddd/ddd.py                            optional read-only helper
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
│   │   └── decisions/adr-lending-001.md
│   ├── modules/document-rendering/spec.md
│   └── system/composition/spec.md
└── changes/
    ├── record-return-condition/
    │   ├── .openspec.yaml
    │   ├── proposal.md
    │   ├── impact.md
    │   ├── specs/contexts/lending/.../spec.md
    │   ├── design.md
    │   ├── tasks.md
    │   ├── decisions/                       proposed decisions, when useful
    │   └── verification.md                  actual delivery evidence
    └── archive/

docs/architecture/                        central arc42 views and publication
```

This is a possible full layout. Create only owners and views you need. Flat
capability paths also work: the DDD model does not require a fixed folder hierarchy.
OpenSpec 1.13.1 supports the nested paths used here; this guide tests their discovery,
validation, and merge. Keep paths stable: moving a capability is a deliberate
migration, not an incidental naming cleanup inside a behavioral change.

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
`proposal.md`, or reference an existing product goal. A separate needs document is
not required, and a new need is not needed for every domain rule, port guarantee, or
adapter mapping. Requirements may share a need or follow from existing constraints.

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
inventory of DDD patterns. This is an additional documentation view of the same
owner, not a new OpenSpec capability or a second specification lifecycle.

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
