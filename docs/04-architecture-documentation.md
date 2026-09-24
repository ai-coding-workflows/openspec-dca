# Combining specifications with arc42

A reader usually wants a coherent explanation of the whole system. A maintainer
usually wants to edit a detail near the component that owns it. Modular architecture
documentation supports both needs.

**arc42** organizes architecture descriptions around questions about goals,
constraints, context, strategy, building blocks, runtime behavior, deployment,
crosscutting concepts, decisions, quality, risks, and terminology. It provides a
useful reading structure; it does not define the software's component boundaries.

Keep system-wide explanations centrally: why the system exists, what surrounds it,
how it is deployed, and which quality goals matter. Keep a component's detailed
structure or a feature's runtime scenario near its spec. The handbook can include
those local fragments where they help explain a system view.

```text
Local feature architecture/runtime.md ──→ arc42 runtime chapter
Local adapter architecture/mapping.md ──→ relevant building-block explanation
Scoped decisions/ records             ──→ grouped decision overview
Central system descriptions          ──→ context, strategy, deployment, risks
```

An include assembles existing text. It does not create a second editable source.
Changing the local fragment updates the assembled chapter on the next build.
Selection still requires judgment: including every implementation detail would make
the handbook hard to read. A feature also need not become a separate architectural
building block merely because it has a specification.

## Describing the present and preserving the reasoning

An architecture description explains the current design. An **Architecture Decision
Record**, or ADR, preserves the context, choice, alternatives, and consequences of
a significant decision. These records help future maintainers understand why an
apparently simpler alternative was not chosen.

Keep local decisions near their owner and broader decisions at their shared scope.
A useful published navigation is Global → Contexts → their subtrees, with reusable
Modules alongside them. Several ADRs can share one ownership page. Individual ADR
files remain separately editable and can have stable IDs and links.

Accepted rationale should remain available. When a choice changes, record the new
reasoning and explicitly supersede the old decision. Update the current architecture
description as well, so readers do not need to reconstruct today's design from a
sequence of historical decisions.

## Updating architecture during an OpenSpec change

Put proposed implementation choices in the change's `design.md` and, where useful,
change-local proposed ADRs. Name the durable architecture and decision paths in the
design and tasks. During implementation, update current views and explicitly accept
or supersede the corresponding decisions. Preserve earlier accepted rationale.

OpenSpec's requirement delta merge handles `spec.md` files. It does not promote an
ADR, update a runtime fragment, or maintain the catalog. Check these explicit tasks
before closure. A proposed architecture fragment kept near its owner must clearly
state that it is proposed; otherwise readers will confuse the target with the present.

## Publication is a separate concern

Markdown can be reviewed with the code. A tool such as mdBook can publish it as a
searchable handbook and include local fragments. This guide demonstrates includes
in the [worked example](06-example.md). It uses ordinary chapter links rather than
a custom automatic ADR-discovery plugin.

A dependency catalog, automatic ADR indexing, and broken-link checking can improve
the process, but they are separate automation choices. They do not arise simply
from using Markdown or adopting arc42. Document any generated content and identify
its editable source clearly.
