# Equipment lending system architecture

This small handbook describes the fictional baseline in this example. It gives a
system-wide entry point; the lending specs own the detailed contracts and local
architecture. The active change proposes return-condition behavior that is not yet
implemented or part of this baseline.

Read [goals and stakeholders](goals-and-stakeholders.md),
[constraints](constraints.md), and [system context](system-context.md) for the
architecture inputs. The [decision index](architectural-decisions.md) distinguishes
accepted records from the proposed change-local ADR. The current
[return runtime view](../specs/contexts/lending/features/return-equipment/architecture/runtime.md)
and [database mapping view](../specs/contexts/lending/adapters/out/database/architecture/mapping.md)
remain with their owners.

These sections cover the arc42 introduction, constraints, context, and decisions.
Other system-wide sections can be added when there is useful content; empty chapters
are not required. `specs/system/` would be for a genuine system-owned contract, not
another handbook.
