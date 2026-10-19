# {Project}: implementation map and test commands

<!-- Foundation draft: keep inside the foundation change until authorized publication.
Suggested target: openspec/specs/system/composition/architecture/implementation-map.md.
An architecture-only scope needs no dummy spec.md or catalog entry. Reuse a suitable
existing project location rather than silently relocating it. -->

## Contexts and ownership
<!-- Only justified contexts; first use case and authoritative business concepts.
Business vs technical ownership; explicit shared values and cross-context contracts. -->

## Source realization
| Context / role | Actual module, package or path | Public boundary / permitted dependencies |
| --- | --- | --- |

<!-- Domain, application/ports, inbound/outbound adapters, composition. Include framework
entry points, generated sources, type dependencies, aliases and re-export surfaces.
No forced directory names; do not use a global utils/services folder as implicit ownership. -->

## Executable boundary rules
<!-- Exact checks, positive scan scope, exclusions/reasons, deliberate invalid fixtures,
and scoped accepted exceptions. Explain detection gaps such as reflection/dynamic imports. -->

## Local and CI commands
| Purpose | Exact runnable command | What it proves / prerequisites |
| --- | --- | --- |

<!-- Core unit/application tests through ports; real-adapter contract/integration tests;
architecture rules and negative controls; production wiring smoke; required build/lint
checks; documentation/link checks; closure check. No fake commands or silent skips.
Name the repository's required CI entry point. External branch protection still needs
actual hosting configuration and must not be claimed merely because YAML was written. -->

## Composition and evolution
<!-- How configuration and implementations are bound, consistency ownership where
needed, boundary-change maintenance, and accepted decision references. -->
