# Building blocks

Status: {Current or Proposed}
Scope: {system and detail level}
Basis: {inspected revision or proposed change}
Question: {which responsibilities and relationships this view explains}

<!-- Starter for openspec/system-architecture/building-blocks.md. A high-level structural
diagram is part of the declared baseline. Include one or reference an adequate existing
source; use a small text-based diagram where appropriate. Do not invent a ports-and-
adapters structure, bounded contexts, or spec ownership from directory names alone. -->

## Structural overview

<!-- Show important responsibilities and explicit relationship types. Distinguish code
dependencies, consumed contracts, and runtime calls. Explain scope, status, legend,
and single editable source. A diagram can combine types only when unambiguous.
A feature, bounded context, code package, and deployment unit are not automatically
one-to-one. Summarize internal context relationships here or link a context map. -->

## Responsibilities and local views

| Responsibility / scope | Role | Provided / consumed contracts, when present | Local view / evidence |
| --- | --- | --- | --- |

<!-- Contexts express coherent business meaning; technical-capabilities/ contains
independently meaningful technical responsibilities. System-owned components need
an explicit scope. Architecture-only areas can appear without a placeholder spec
or catalog node. Keep detailed class/module lists at the relevant local view. -->

## Boundaries, adapters, and shared components

<!-- Explain relevant in/out roles relative to each core and cross-context translations.
The consumer's required contract need not equal the provider's offered contract.
A shared server/library alone does not establish shared business ownership. Keep
orchestration explicit instead of hiding it in generic adapters or composition. -->

## Assumptions and verification

<!-- Source links and material gaps. Identify changed/reused views in impact and review
against the implemented revision. Successful rendering alone is not dependency validation. -->
