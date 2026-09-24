# {Domain owner}: domain model

Status: Proposed
Scope: {bounded context or clearly scoped domain}
Behavioral contract: {relative link to the owning spec.md}

<!-- Optional companion, normally placed at the domain owner's model.md. It is not a
new OpenSpec artifact or a separate owner. Choose Current or Proposed explicitly;
identify any accepted-but-unimplemented target rather than calling it implemented.
Keep only sections that explain this domain. No complete DDD-pattern inventory is
required, and a small model can remain a short document. -->

## Purpose and Vocabulary

<!-- Explain the scope and concepts needed to understand its contracts. Define a
term here only when this is its authoritative source; otherwise link the definition.
Use relevant distinctions and counterexamples, not a glossary of every code symbol.
Needs and outcomes belong in the proposal or referenced product goals. -->

| Concept | Meaning in this context | Important distinctions / references |
| --- | --- | --- |

## Identity and Relationships (optional)

<!-- Describe relevant identities, relationships, ownership, and lifecycle boundaries.
Mention entities, value objects, aggregates, or events only where useful to explain
meaning. Do not turn this into a class diagram, database schema, or implementation plan.
Add a focused model diagram when relationships would otherwise be ambiguous. -->

## States and Historical Data (optional)

<!-- Explain what relevant states and values mean, including unknown, unrecorded, or
historically valid data where applicable. Distinguish representable stored states
from newly allowed commands/transitions. Do not invent historical values to satisfy
new-input rules. A state diagram may summarize rules but must identify their source. -->

## Behavioral Rule References

<!-- Link the owning requirements for invariants, allowed transitions, decisions,
and prohibitions. Keep normative behavioral rules and concrete scenarios in spec.md;
do not maintain a second independent list here. Requirements may reference definitions
in this model without duplicating their meanings or value sets.

A definition change can change a contract. Review consuming requirements and provide
appropriate deltas; this companion is not a way to bypass behavioral change review.
Proposed model wording stays change-local or clearly marked as proposed. Name affected
requirements and durable updates in impact/design/tasks. Native requirement sync does
not merge this document; update it deliberately with a consistent accepted baseline. -->

## Open Questions (optional)

<!-- Record only unresolved model questions that matter. Identify the assumption and
which decision or delivery slice is blocked; do not present an open question as a rule.
Track delivery work in the change's shared tasks, not as a second backlog here. -->
