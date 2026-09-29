# About this guide

OpenSpec DDD combines three useful ideas: OpenSpec for delivering changes, explicit
ownership of domain contracts, and modular architecture documentation. It applies
to projects with one or several bounded contexts and does not prescribe a language,
framework, deployment model, or test runner.

OpenSpec already separates maintained specifications from proposed changes.
The DDD contribution is deciding **which owner defines a rule**, which consumers
must be reviewed, and how architecture and decisions stay aligned with delivery.

For example, a request to record the condition of returned equipment starts with
one feature. It can require a domain rule, a stronger storage guarantee, and an HTTP
mapping. These are several owning contracts but one delivery effort.

In an adopting repository, `openspec/README.md` is the documentation entry point.
`openspec/system-architecture/` explains the system as a whole; `openspec/specs/`
holds owned contracts and local documentation; `openspec/changes/` coordinates
proposed work. Use `technical-capabilities/` for independently meaningful technical
contracts and `architectural-decisions/` for scoped decision records. The handbook's
`architectural-decisions.md` is their index, not another record store. See the
[directory structure](03-structure.md) and [architecture handbook](04-architecture-documentation.md).

Read the [core idea](01-core-idea.md), then the [workflow guide](05-change-workflow.md).
The [example](06-example.md) shows baseline specs and change deltas separately.
The [tooling chapter](09-tooling.md) explains installation and actual Pi commands.

The [architecture chapter](04-architecture-documentation.md) defines the small
baseline of views and when additional diagrams are required. The [template chapter](08-templates.md)
connects those rules to planning, durable documents, and actual verification. These
are documentation and review conventions, not extra native workflow stages.

The schema, templates, catalog format, and example belong to this guide.
OpenSpec provides the CLI and agent integrations. Upstream references:

- [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- [OpenSpec customization](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- [CLI reference](https://openspec.dev/docs/cli)
- [Supported agent integrations](https://openspec.dev/docs/supported-tools)
- [arc42 documentation](https://docs.arc42.org/)
