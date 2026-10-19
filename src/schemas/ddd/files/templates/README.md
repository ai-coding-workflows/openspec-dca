# OpenSpec DDD template library

The seven native artifacts are proposal, impact, domain-model (producing
`domain-model-changes.md`), specs, design, architectural-decisions and tasks.
Their templates provide headings, not evidence or automatic approval.

## Reusable policy and foundation

- [Architecture policy](architecture-policy.md): stack-independent ownership and dependency rules.
- [Project setup prompt](project-setup.md): adopt the schema and build tested project boundaries.
- [Implementation map](project-architecture.md): concrete modules, ports, bindings and runnable checks.
- [Config](config.yaml), [agent guidance](agent-instructions.md), and
  [OpenSpec entry point](openspec-README.md): merge into the adopting project.
- [Catalog](catalog.json): optional empty starter, not a replacement for an existing catalog.

## Change support, not more native artifacts

Use [domain-model.md](domain-model.md), [architecture.md](architecture.md), and
[architectural-decision.md](architectural-decision.md) only for useful substantial drafts.
[verification.md](verification.md) records actual execution/review.
[integration.json](integration.json) records the three closure states and final
file snapshots; see [the helper guide](../helpers/README.md) for its exact format.
It is not a publication engine, second plan, or pre-Apply prerequisite.

Planning is change-local. Apply may deliver mapped outside-tree descriptive docs,
but the whole openspec/specs/** tree, maintained models/ADRs and catalog stay protected.
Separate authorized integration must merge requirements, explicitly publish necessary
companions, and reconcile dependent links/maps before closure. Archive guidance is
advisory; project CI/wrappers provide the actual gate.

{{hook:support-index}}
