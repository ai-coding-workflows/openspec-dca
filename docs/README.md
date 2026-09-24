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

Read the [core idea](01-core-idea.md), then the [workflow guide](05-change-workflow.md).
The [example](06-example.md) shows baseline specs and change deltas separately.
The [tooling chapter](09-tooling.md) explains installation and actual Pi commands.

The schema, templates, catalog format, and example belong to this guide.
OpenSpec provides the CLI and agent integrations. Upstream references:

- [OpenSpec concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- [OpenSpec customization](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)
- [CLI reference](https://openspec.dev/docs/cli)
- [Supported agent integrations](https://openspec.dev/docs/supported-tools)
- [arc42 documentation](https://docs.arc42.org/)
