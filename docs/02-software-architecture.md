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

## Assembly and reusable modules

The **composition root** connects concrete implementations to the application.
It can choose a database adapter, read configuration, and supply the objects needed
by a use case. Knowing these implementations is its responsibility.

Reusable technical capabilities may belong in **modules**: for example, document
rendering or authenticated transport. A module can have an internal model and a
carefully restricted public API. Reuse alone does not make it a separate business
context. Equally, a concept such as identity may be a substantial business context
in one system and a technical integration in another; the classification depends
on the problem and ownership, not its name.

These boundaries explain useful documentation owners. They do not prescribe a
fixed number of folders or a separate service for every feature.
