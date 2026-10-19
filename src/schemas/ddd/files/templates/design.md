# Design: {change}

## Approach and decisions
<!-- One implementation approach. Reference assessed meanings and significant ADR
rationale instead of copying them. Explain remaining choices and blocked work. -->

## Hexagonal realization
<!-- For each affected use case give the following record, or link an inspected
existing record and specify the delta. Use exact paths and stable symbols, proposed
or existing. These roles need not be separate files/classes. -->

### {Use case / owning context}
- Driving adapter and application entry point:
- Domain rules and application implementation:
- Outbound ports and contract references (or none, with reason):
- Driven adapters and external/cross-context mappings:
- Composition location and concrete bindings:
- Source dependency direction, including type/re-export/generated edges:
- Representative runtime and failure/transaction flow:
- Verification locations and commands:

## Delivery slices and risks
<!-- Small working slices; consistency, compatibility, migration/rollback as relevant. -->

## View and implementation-map publication
| Source / inspected basis | Action / proposed section or draft | Maintained target | Required check |
| --- | --- | --- | --- |

<!-- Sources/targets project-relative; drafts change-relative. Reuse the realization
above as an input rather than creating a duplicate map. Protected targets are
published only during separately authorized integration. Outside-tree descriptive
docs are Apply delivery; preserve unrelated edits and protected meaning/status. -->

## Verification strategy
| Behavior / boundary / risk | Test level and concrete check | Scope / limitation |
| --- | --- | --- |

<!-- Cover affected domain/application behavior through ports, real-adapter promises,
production wiring, and executable dependency rules. Foundation: concrete local/CI
commands and at least one intentionally forbidden dependency proving detection.
Check meaningful scan coverage; explain exclusions and genuine non-applicability.
Planning names checks; verification.md records actual execution and revisions. -->

{{hook:template.design}}
