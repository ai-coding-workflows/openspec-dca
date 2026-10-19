# Design: {change}

## Approach and decisions
<!-- One implementation approach. Reference assessed meanings and significant ADR
rationale instead of copying them. Explain remaining choices and blocked work. -->

## Hexagonal realization
<!-- For each affected use case give the following record, or link an inspected
existing record and specify the delta. Use exact paths and stable symbols, proposed
or existing. Use recognizable process names in entry points and tests; identify
meaningful translations/compatibility aliases, not every symbol. These roles need not
be separate files/classes. Link process contracts rather than repeat their behavior. -->

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

## Publication and reconciliation mapping
| Source / inspected basis | Action / proposed section or draft | Maintained target / section | Required check |
| --- | --- | --- | --- |

<!-- Sources/targets project-relative; drafts change-relative. Map affected views,
configuration/API companion contracts and supporting sections, not only spec deltas.
Reference model/ADR mappings and the realization above instead of copying them.
Give exact file/section, action, proposed content and check for each affected target.
Include renamed keys/changed meanings, glossary links and affected language mappings
in coverage review; reference the model assessment for definition/index publication. Supporting sections in a
spec.md need explicit reconciliation after requirement merge, not whole-file replacement.
Protected targets change only during separately authorized integration; outside-tree
descriptive docs are Apply delivery. Preserve unrelated edits and protected meaning/status. -->

## Verification strategy
| Behavior / boundary / risk | Test level and concrete check | Scope / limitation |
| --- | --- | --- |

<!-- Cover affected domain/application behavior through ports, real-adapter promises,
production wiring, and executable dependency rules. Foundation: concrete local/CI
commands and at least one intentionally forbidden dependency proving detection.
Check meaningful scan coverage; explain exclusions and genuine non-applicability.
Review changed terminology and process semantics; use scoped alias/link checks where
useful, plus behavior tests. Naming alone cannot establish correct domain meaning.
This is the canonical planned test matrix; tasks reference it. verification.md
records actual results and basis, not another planned test catalogue. -->

{{hook:template.design}}
