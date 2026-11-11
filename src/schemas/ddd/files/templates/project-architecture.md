# {Project}: implementation map and test commands

<!-- Foundation draft: keep inside the foundation change until authorized publication.
Suggested target: openspec/specs/system/composition/architecture/implementation-map.md.
An architecture-only scope needs no dummy spec.md or catalog entry. Reuse a suitable
existing project location rather than silently relocating it. -->

## Contexts and ownership
<!-- Only justified contexts; first named process/use case and links to authoritative
concept/process definitions and the selected glossary. Do not duplicate vocabulary.
Business vs technical ownership; explicit shared values and cross-context contracts. -->

## Source realization
| Context / role | Actual module, package or path | Public boundary / permitted dependencies |
| --- | --- | --- |

<!-- Domain, application/ports, inbound/outbound adapters, composition. Include framework
entry points, generated sources, type dependencies, aliases and re-export surfaces.
No forced directory names; do not use a global utils/services folder as implicit ownership.
Use domain/process names in the meaningful public symbols; reference boundary translations
and compatibility aliases. Do not maintain an exhaustive term-to-identifier inventory. -->

## Executable boundary rules
<!-- Exact checks, positive scan scope, exclusions/reasons, deliberate invalid fixtures,
and scoped accepted exceptions. Explain detection gaps such as reflection/dynamic imports. -->

## Local and CI commands
| Purpose | Exact runnable command | What it proves / prerequisites |
| --- | --- | --- |

<!-- Core unit/application tests through ports; real-adapter contract/integration tests;
architecture rules and negative controls; production wiring smoke; required build/lint
checks; definition-link and scoped terminology checks where useful; closure check. No fake commands or silent skips.
Name the repository's required CI entry point. External branch protection still needs
actual hosting configuration and must not be claimed merely because YAML was written. -->

## Documentation profile (when relevant)
<!-- Reuse/reference existing project settings rather than create a second inventory.
Only fill missing choices: readers and tasks; versions/languages; source roots and
published formats; editable vs generated units; selected glossary entry point(s).
Use documentation-policy.md. No mandatory directory layout or metadata per page.
Record exact checks in Local and CI commands above: scope, required failure gates,
configurable size/growth/entry-count review signals, exceptions with reasons/review
triggers, and risk-based safe procedure checks. No universal size thresholds.
Distinguish template/draft/history/include exclusions from publishable content.
A docs profile is not a newly required artifact or a new openspec/config.yaml key. -->

## Composition and evolution
<!-- How configuration and implementations are bound, consistency ownership where
needed, boundary-change maintenance, and accepted decision references. -->
