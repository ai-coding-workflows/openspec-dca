# Runtime

<!-- Starter for openspec/system-architecture/runtime.md. Explain a representative
selection of architecturally significant interactions; do not enumerate every use
case or copy every local sequence diagram into a second editable source. -->

## Scenario selection

| Scenario / question | Why architecturally significant | Authoritative local/shared view | Current or proposed |
| --- | --- | --- | --- |

<!-- Choose relevant success and failure paths: cross-owner coordination, transaction
boundaries, asynchronous work, retries, concurrency, or partial failure where present.
Identify accepted versus assumed behavior through actual contract/source references. -->

## Interaction views

<!-- Include or reference focused diagrams when the interaction would otherwise be
ambiguous. State participants, ordering, relationship semantics, scope, status, and
editable source. Distinguish runtime calls/messages from code dependencies. Link domain
state meaning rather than redefine invariants. A diagram is not an executable test. -->

## Consistency and failure boundaries

<!-- Explain relevant commit/rollback, retry/idempotency, unknown outcomes, and consumer
behavior with evidence. A communication failure alone does not prove a remote rollback.
Expose actual mismatches without silently changing the authoritative contract. -->

## Evidence and open questions

<!-- Link actual implementation/review evidence and relevant tests or runs. Reading
assertions does not prove tests passed. Record gaps and the work/decision they block. -->
