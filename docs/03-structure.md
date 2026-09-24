# Organizing contracts and changes

Keep OpenSpec's `specs` and `changes` roots. Organize the capability paths below
them around contract ownership. The same relative path identifies the owner in a
main spec and in a change's delta spec.

```text
openspec/
├── config.yaml
├── catalog.json                          optional DDD ownership/dependency map
├── schemas/openspec-ddd/                  workflow schema and templates
├── ddd/ddd.py                            optional read-only helper
├── specs/
│   ├── contexts/lending/
│   │   ├── domain/spec.md
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
| Meaning and allowed values of return condition | Domain spec |
| Successful save persists state and condition together | Storage port spec |
| Return accepts input, applies rules, and reports an outcome | Feature spec |
| JSON mapping and HTTP status codes | HTTP adapter spec |
| Database columns and transaction implementation | Database architecture fragment |
| Selected provider and wiring | Composition scope |

A storage adapter may refer to its port's guarantees without repeating them. If the
guarantee changes, its implementation and architecture may need work even when its
spec needs no delta. Record this disposition in `impact.md`.

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
