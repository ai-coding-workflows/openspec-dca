# Choose a workflow

Start with one outcome and coordinate its delivery in one change. “Record the
condition of returned equipment” starts at the return feature but also needs a
domain rule, a storage guarantee, and an HTTP mapping. Each rule stays with its
owner; one design and task list coordinate the work.

Necessary domain/port changes are included and reported with a reason. Review
dependent adapters in the same effort. Routine mappings follow the agreed contract;
choices such as whether existing callers may omit the new field need clarification.
Being inside one bounded context does not make unrelated improvements part of the change.

The examples below use **Pi's `/opsx-*` commands**. These are agent prompts, not shell
commands. Other integrations may use a different spelling; see [setup](09-tooling.md).

## Define and plan a new change

```text
(opsx-explore) → opsx-propose → review planning → opsx-apply
```

Use `explore` while the problem or compatibility choices are unclear. Use `propose`
when the intended outcome is clear enough to prepare the change. With this schema,
it prepares `proposal → impact → specs → design → tasks`, stopping before code.
Clarification happens when needed; there is no separate mandatory clarify command.

```text
/opsx-propose record-return-condition: Start from lending.return.
Require a condition for each new return. Include necessary domain and port changes
and report additional owners. Discuss the compatibility of existing HTTP callers.
```

Before apply, review whether the deltas, design, and tasks agree. For a focused
requirements checklist, ask the agent to check ambiguity, failure behavior, and
compatibility now, or after a later requirements revision. Store a useful checklist
in the change; it is not a second implementation backlog or proof of acceptance.

For stepwise artifact creation, enable the optional `new`, `continue`, and `ff`
workflows. `new` starts the effort; `continue` advances an available artifact;
`ff` prepares the remaining artifacts. The terminal equivalent for discovering what
to write is `openspec status` followed by `openspec instructions <artifact-id>`.

## Refine an active change

```text
(read-only impact/diff review) → opsx-update → fill missing artifacts → opsx-apply
```

`update` revises existing planning artifacts and reconciles their consequences.
This covers the former `update → diff → propagate` loop without a separate propagation
command. Ask for a read-only impact/diff review when you want to understand the
consequences first; the optional DDD helper supplies the consumer review set.

```text
/opsx-update record-return-condition: Refine the rejection behavior for invalid
conditions and reconcile the existing impact, deltas, design, and tasks.
```

The generated OpenSpec 1.13.1 update workflow shows revisions and confirms them
artifact by artifact. It does not create missing artifacts or additional delta
files. When a new owner needs a delta, obtain the `specs` instructions and ask the
agent to create that missing file before proceeding. A glob artifact can already
be marked done after one file exists; status cannot tell whether all owners are covered.

| State after revision | Next step |
| --- | --- |
| Existing design and tasks remain current | Review consistency, then `apply` |
| Design or tasks need revision | Reconcile them with `update`, then `apply` |
| An artifact is absent | Get its native instructions and create it; optional `continue` helps |
| Another delta file is needed inside an existing specs artifact | Get `instructions specs`, create the file, and reconcile scope/design/tasks |
| Important behavior or compatibility remains undecided | Resolve it before dependent planning or code |
| Prior effort is finished or archived | Start a new change with `propose` |

You do not repeat planning simply because a spec changed. You do need an up-to-date
design and task list before implementation. Preserve valid completed tasks; add
new work and explain any tasks reopened by the revision.

## Implement, review, and close gaps

```text
opsx-apply → acceptance review → (reconcile tasks → opsx-apply → review)
          → opsx-archive
```

`apply` executes the selected change's tasks. Implement useful slices across owners
instead of starting a new plan/tasks pair for every spec. For larger work, use several
sessions and reload only the relevant baseline, deltas, architecture, and task slice.
Split the effort into linked changes when outcomes can be delivered independently.

Review actual behavior against acceptance and the combined baseline plus deltas.
Run appropriate tests and record results in `verification.md`. The optional `verify`
workflow assists with conformance review; it does not replace application tests or
the project's required reviews.

For a confirmed implementation gap, add an unchecked task if existing tasks do not
cover it, then apply and review again. This is the former “converge” loop. If the
required behavior changes instead, return to the refinement workflow.

Archive after acceptance, required checks, and durable documentation are complete.
The native archive workflow handles outstanding spec synchronization and archives the
change. `sync` is useful when you deliberately want the main specs updated while
keeping the change active. It is not another implementation step or an acceptance gate.

## Supporting activities

| Need | When and how |
| --- | --- |
| Clarify a business or compatibility choice | Explore before proposing, or discuss the choice during refinement |
| Requirements-quality checklist | After requirements stabilize; revisit after substantial changes |
| Analyze consistency and coverage | Before apply and after planning revisions; review proposal, impact, deltas, design, tasks |
| Architecture review | After design for significant boundaries/decisions; after implementation for conformance |
| Review delivered behavior | After apply; use tests and acceptance evidence, optionally `verify` |
| Converge on missing work | After confirmed gaps; reconcile tasks and repeat apply/review |
| Find where to resume | Native `status --all`, `list`, and per-change apply instructions |

These activities do not require a matching command for every verb. Ask the agent
for a scoped read-only review when appropriate. The bundle adds no parallel set of
`l-*` prompts. OpenSpec owns agent integration and the change lifecycle.

## Command responsibilities by workflow

| Workflow | Native agent operations | Main responsibility |
| --- | --- | --- |
| Understand and prepare | `explore`, `propose`; optional `new`, `continue`, `ff` | Clarify the outcome and create change artifacts |
| Refine planning | `update` | Reconcile existing artifacts without writing implementation code |
| Deliver | `apply` | Execute tasks and maintain delivery evidence |
| Verify and close | Optional `verify`, then `archive`; `sync` when needed separately | Review conformance, merge deltas, retain history |

There are no separate native `plan`, `tasks`, `checklist`, `analyze`, or `converge`
commands in this bundle. Design and tasks are schema artifacts; the other activities
are focused reviews or iterations within these workflows.
