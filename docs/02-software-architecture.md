# A software architecture that supports the model

The documentation approach can describe many architectures. A domain-centered
ports-and-adapters design provides a useful example because its responsibilities
are explicit. Using the documentation layout does not require adopting this design.

## Domain and use cases

The **domain** contains concepts and rules meaningful to the problem being solved.
For equipment lending, those might be a loan, a borrower, and a return condition.
The domain should not need to understand HTTP requests or database rows to express
whether a return condition is valid.

A **use case** describes an operation performed for a person or another system,
with a recognizable goal and outcome. Returning equipment is a use case. Validating
one field or calling a repository method is normally a step, not a separate use case.
Its application logic coordinates domain rules and ports to produce the outcome.

A **feature** is a lasting capability and a stable home for one or several related
use cases. Keep features as the default organizational unit. A feature may contain
only one use case; no additional grouping or folder is required. Split out a use
case only when separate contract ownership or independent evolution justifies it,
not because it has its own endpoint or application class.

A **scenario** is a concrete example of a requirement, such as rejecting a return
without a condition. Alternative and failure scenarios normally remain with the
requirement they explain. A **change** is the temporary delivery effort that adds
or modifies these lasting contracts; it is not another level of feature granularity.

A **bounded context** is an area where a model and its vocabulary have a consistent
meaning. Lending and maintenance could eventually become distinct contexts if their
models and responsibilities warrant it. A bounded context is not automatically a
microservice, a repository, or a deployment unit. A small application may need only one.

## Ports and adapters

A **port** describes a conversation across a boundary. An inbound port exposes a
use case to callers. An outbound port describes a capability the use case needs,
such as loading and saving loans. A port includes behavioral obligations, not just
method names: for example, how absence or a failed save is reported.

An **adapter** connects that conversation to a technology. An HTTP endpoint can
adapt an incoming request into a return operation. A database adapter can implement
the storage port. A command-line interface could invoke the same operation through
the same inbound contract.

```text
At runtime:
HTTP request → application use case → storage port → database adapter

In the source code:
application → ports and domain
HTTP adapter → inbound port
storage adapter → storage port and domain
```

The difference matters. The application invokes storage at runtime, but its code
knows the storage contract, not a particular database implementation. Replacing the
database should not require importing its driver into the lending rules.

Ports do not eliminate real differences between providers. If a new implementation
cannot meet a required guarantee, the team must resolve that mismatch explicitly.
Pretending that incompatible services share the same contract moves the problem
rather than solving it.

### Direction and documentation ownership

`in` and `out` are relative to the documented application core or capability.
They describe who drives the interaction, not the direction of each data transfer
or of source-code dependencies. State the reference boundary in local views.

Feature specs normally own the technology-independent behavior exposed through
inbound ports. Do not add an inbound-port spec merely to repeat that behavior.
Keep `ports/` flat unless separately maintained inbound and outbound contracts make
`ports/in/` and `ports/out/` useful. A feature, use case, port, and endpoint need not
correspond one-to-one, and the specification tree need not mirror code packages.

### Ports and adapters across scopes

Ports and adapters are not restricted to a bounded context. Place them with the
context, technical capability, or explicitly owned system responsibility whose
contract they serve. A consuming context may own a port and an adapter that
translates to another context's published contract; communication across contexts
does not by itself imply shared ownership.

A technical capability may own its own ports and adapters. A system-owned adapter
may serve several contexts while referencing their contracts. Sharing a server,
database, or library alone does not require shared behavioral ownership. For an
integration spanning several cores, state its role at each boundary rather than
assigning an ambiguous global direction. Keep business orchestration explicitly
owned instead of hiding it in adapters or composition.

## Assembly and technical capabilities

The **composition root** connects concrete implementations to the application.
It can choose a database adapter, read configuration, and supply the objects needed
by a use case. Knowing these implementations is its responsibility.

Independently meaningful technical contracts may belong in **technical capabilities**:
for example, document rendering or authenticated transport. A capability can have an
internal model and a carefully restricted public API. Reuse alone does not make it a
separate business context. Equally, a concept such as identity may be a substantial
business context in one system and a technical integration in another; the
classification depends on the problem and ownership, not its name.

Use `openspec/specs/technical-capabilities/<capability>/` when the contract and its
evolution deserve independent explanation and review. This is an optional ownership
scope, not a mandatory layer or a container for every shared utility. Consumer count
does not determine identity, and context-specific ports stay with their context.

These boundaries explain useful documentation owners. They do not prescribe a
fixed number of folders or a separate service for every feature.
