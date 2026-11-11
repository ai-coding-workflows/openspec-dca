# Domain-centered architecture policy

This selected schema requires a domain-centered ports-and-adapters architecture.
Use the project's language and framework idioms; these are responsibility and
source-dependency rules, not mandatory directory names or class patterns.

1. **Own behavior by context.** Business rules and application workflows belong to
   an explicit core. Delivery packages, database tables, and technical folders do
   not establish context boundaries. Start with the smallest justified context set.
2. **Point dependencies inward.** Domain code is independent of application glue,
   adapters, frameworks, persistence, and I/O. Application code uses its domain and
   core-owned contracts, not concrete infrastructure or other contexts' internals.
   Approved pure libraries and explicitly governed shared values are allowed.
3. **Name the boundaries.** Driving adapters call application entry points; driven
   adapters implement required ports. A function, protocol, interface, or module API
   can be a port. Features may own inbound behavior without a duplicate port spec.
   Define external input/output, failure, consistency, and retry meaning as needed.
4. **Assemble at the edge.** Composition binds implementations and configuration.
   Keep business decisions out of routes/controllers, serializers, persistence,
   and rendering. Inject environmental effects such as time when behavior depends
   on them; no hidden service locator or ORM type leakage into the core.
5. **Keep contexts encapsulated.** Use published contracts for inter-context calls,
   with consumer-owned ports/translations where required. A reusable mechanism may
   be shared; it must not absorb a consuming context's business rules.
6. **Realize and test the map.** Record concrete source modules, ports, adapters,
   and bindings. Check source dependencies, including compile/type dependencies,
   aliases/re-exports and generated code where relevant. Test the core in isolation,
   real adapters against promised guarantees, and representative production wiring.
   Prove architecture checks reject deliberately invalid fixtures.
7. **Make exceptions explicit.** An accepted deviation needs a narrow scope, owner,
   rationale, review/removal trigger, and matching test allowance. A framework
   convention or convenient import is not an implicit exception.

Keep context-first modules/packages where the stack permits. Framework-required
entry-point locations may stay where the framework expects them; map and test the
boundary instead of adding empty wrappers. Do not create empty specs, adapters,
interfaces, diagrams, repositories, or shared kernels to complete a pattern.

Publish the project's concrete realization in its owned implementation map, not
by rewriting this reusable policy as though it described existing code.

## Ubiquitous Language

Use a shared language within each bounded context for concepts, relationships,
named processes/use cases, actions, states/outcomes and events where relevant.
The same word may have different explicitly scoped meanings in different contexts.

Keep conceptual meanings in the owning domain model; process scope, triggers,
completion and behavior in the owning feature/use-case specification; shared rules
in domain requirements. Runtime views explain collaboration, not a second process
contract. A cross-context process has an explicit contract owner and references
its participants; the glossary does not become that owner.

The glossary indexes terms by kind, context and a link to the authoritative file
and section. Reuse an existing glossary; short explanations identify terms without
copying rules. Definitions need no separate file per term or mandatory filesystem hierarchy.
Group the glossary by bounded context/scope; separate genuinely shared domain terms
and technical terms when needed. Sort context sections alphabetically and entries
by canonical display term, case-insensitively. Optional kind subgroups remain
alphabetically sorted internally. Follow glossary.md for layout and growth.
One logical glossary need not be one file or one file per context. Split by useful
scope/kind only when needed; retain entry-point navigation and one maintained entry
per scoped meaning. Additional global indexes link to or are generated from those
entries. Check links in the intended publication format, not only in the repository.
Use documentation-policy.md for granularity and project-specific checks.

Use recognizable terms across code, tests, specifications, diagrams, current docs
and active changes. Allow native identifier conventions and explicitly mapped
translations, external representations and compatibility aliases. Assess public
API/configuration/data compatibility before renaming. Not every term needs a code
type, and ordinary technical identifiers need no invented domain equivalent.

Assess terminology evolution in the existing domain-model artifact. Distinguish
established meanings, proposals and unknowns; do not invent stakeholder agreement.
A meaning change can affect obligations without changing its name. Apply uses the
baseline overlaid with the selected change; historical records retain their wording.
Maintained language definitions follow model/spec protection regardless of location.
Index-only edits follow mapped documentation rules; stage links to unpublished
owners until integration. Ordinary naming does not require an ADR.
