# The core idea

Work is coordinated through a **change**. Lasting behavior is owned by **main specs**.
OpenSpec keeps a proposed contract change as a delta until it is synchronized into
those main specs. A change can affect several owners while keeping one design and
one task list.

| Information | Location | Responsibility |
| --- | --- | --- |
| Main specification | `openspec/specs/<capability>/spec.md` | Maintained behavioral baseline |
| Proposed contract delta | `openspec/changes/<change>/specs/<capability>/spec.md` | Added, modified, removed, or renamed requirements |
| Proposal and impact review | Change directory | Outcome, scope, owners, compatibility, affected consumers |
| Design and tasks | Change directory | Delivery approach and remaining work |
| Architecture and ADRs | Near their owner or in system documentation | Current design and retained decision rationale |
| Verification evidence | Change directory and test/review systems | Evidence for acceptance, with actual results |

Each normative rule has one owner. The lending domain defines valid return
conditions. A feature uses that definition. The storage port defines a successful
save. An adapter specifies its boundary behavior and documents its implementation
separately. Repeating a summary is useful; maintaining competing rule definitions is not.

## Two dependency graphs

Contract dependencies tell you which rules to read and which consumers to review.
For example, a feature and a database adapter can both consume the same storage
port. The optional DDD catalog records these relationships.

OpenSpec's artifact dependencies tell you which change documents can be prepared
next. The custom schema uses this sequence:

```text
proposal → impact → specs → design → tasks → apply
```

These are documentation prerequisites, not a task execution schedule. Implementation
tasks need their own dependencies and useful delivery slices. Keeping the graphs
separate avoids treating folder order as architecture or automatically rewriting
every consumer when a shared contract changes.

## Agreement and evidence

This guide recommends keeping main specs as the baseline while reviewing and
implementing deltas. After implementation and verification, sync the deltas and
archive the change. OpenSpec also allows earlier sync; if you use it, explicitly
record that the new baseline is accepted but still awaiting implementation.

Synchronization merges contract text. It does not verify code, update architecture
fragments, or accept ADRs. Likewise, artifact files and checked task boxes do not
prove correctness. Record tests, acceptance review, and unresolved gaps before
closing the change.
