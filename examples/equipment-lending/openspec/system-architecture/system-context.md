# System context

The illustrative boundary exposes a lending return operation to an HTTP caller and
uses a database adapter to persist loan state. The
[HTTP adapter](../specs/contexts/lending/adapters/in/http/spec.md) owns request and
response mapping; the [storage port](../specs/contexts/lending/ports/loan-store/spec.md)
owns the persistence guarantee. This overview does not replace either contract.

The example names team-controlled callers in the active change, but does not model
an actual deployed environment or external organization. Internal lending owners
and their interactions are described by their specs and local architecture views.
