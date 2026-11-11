# Optional user-doc component

Select `user-doc` through the existing builder's component selection. It is
independent of arc42 and adds guidance/templates through existing hooks, without
changing the seven-artifact graph. Availability is not activation; no new native
OpenSpec configuration key or runtime component mechanism is introduced.

The [template guide](files/templates/user-doc/README.md) applies the base DDD
`documentation-policy.md` to reader-facing material. Coverage follows actual readers
and tasks, including installation/setup/administration when relevant. No mandatory
folder tree, audience split, task-per-file rule or size quota applies.

## Contributions

| Existing stage | Added responsibility |
| --- | --- |
| Proposal/impact | Readers, tasks/prerequisites, whole affected units and overlap; reasoned no-impact |
| Design | One map of audience/need, inspected basis, action/target and checks; reuse project profile |
| Tasks/Apply | Deliver mapped descriptive sources, review whole units/navigation, resolve findings |
| Verification/integration | Actual safe procedure/structure checks, exceptions and durable-link reconciliation |
| Support library | Reusable topic templates; not populated manual chapters |

Model meaning and significant decisions remain in their existing owners. No page
becomes a native spec owner merely by documenting it; changing explanatory prose
needs no dummy normative delta. Accepted documentation obligations remain binding
whether or not this component is selected.

## Delivery and publication

Use the chosen project root, default `user-doc/`. Planning stays change-local.
Apply delivers mapped outside-tree descriptive sources in the local checkout after
reading targets and preserving concurrent work. Protected models, ADRs/catalog and
all `openspec/specs/**` content remain protected, including generated changes and
moves. Their publication/dependent links belong to separately authorized integration
using the base mappings, handoff and closure receipt. A draft is not delivery; a
completed task or preview is not acceptance or deployment.

Inspect approved generator output and required navigation changes. Keep warnings
at the action. Use only safe authorized examples; do not invent observed behavior.
Use the shared docs helper when applicable and installed; it is not a semantic or
page-size checker. This component installs no automatic splitter, linter rules, CI,
reference generator or publisher. Tool changes require project authority.

The project starter now copies only configuration, a draft entry point and minimal
navigation. Topic templates remain in the schema library. No auto-created empty
chapters; replace the draft entry point before publication. This changes future
starters, not existing project files. Deliberately merge generated guidance and
manifest changes through the original repository's builder; do not overwrite adopted
customizations. The included reference composer does not build project starters.
