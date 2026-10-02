# Optional user-documentation component

This component follows the existing component manifest and additive-hook model.
Select `user-doc` when composing the DDD schema with the project's builder.
It has no required component: DDD alone, DDD + arc42, DDD + user-doc, and
DDD + both are valid intended selections. The seven artifacts and their dependencies
stay in the DDD foundation. Disabling arc42 does not disable user-documentation.

The directory's presence makes it available, not enabled. Only explicit builder
selection injects its guidance and copies its support templates. No native `enabled`
flag, project-config extension key, or component runtime is introduced. Follow the
existing builder's CLI rather than an invented command in this package.

## What it contributes

| Contribution | Responsibility |
| --- | --- |
| Project guidance | Root user-documentation location, readable writing, separate publication |
| Proposal instructions | Reader groups and likely visible effects |
| Impact instructions/template | User task and page coverage; a reasoned no-impact result is valid |
| Specs instructions | Preserve actual documentation obligations without creating one per page |
| Design instructions/template | Reader-oriented structure, exact page/asset mapping, proposed checks |
| Tasks instructions/template | Drafting/checks in the one checklist, publication in the existing handoff |
| Apply instructions | Preserve maintained user pages; write/check drafts and report real evidence |
| Verification template | Actual examples, navigation/procedure checks, preserved baseline, pending publication |
| Support index and files | Six optional page-writing starters under templates/user-documentation/ |

The domain-model and architectural-decisions artifacts remain the sources of model
meaning and significant decision rationale. They do not need another user-doc assessment
or repeated definitions. The component uses the existing scopes and generic hooks only.

## Files versus content

Builder output places starters at:
`openspec/schemas/openspec-ddd/templates/user-documentation/`.
That is the template library, not the handover of a complete handbook.

Real maintained pages belong at `user-documentation/` in the project root. During a
native change, drafts belong at `openspec/changes/<change>/user-documentation/`.
Only separate authorized integration updates maintained pages. An explicitly chosen
existing root can be retained; this component does not automatically migrate files.

All new public pages must answer a reader question. A change with no documentation
impact can use a short reason in impact and omit empty downstream tables. User pages
are not native spec owners, and their references are not contract dependency edges.
Accepted documentation requirements remain binding whether or not this optional
component is selected; component selection is not a waiver mechanism.

## Scope of this update

This addition handles the DDD process and optional writing support first. It does
not change arc42, architecture reconstruction, the native artifact graph, existing
review outcomes, or the builder. It installs no publisher, linter, automatic splitter,
CI workflow, reference generator, new handbook baseline, or user-doc reconstruction
process. Selecting a component is not permission to rewrite installed project guidance.
Merge generated config/agent starters into active project files deliberately.

See [the template guide](files/templates/user-documentation/README.md) for writing and
verification rules. The external builder implementation/README is not included in
this upload; actual composition and OpenSpec integration still require target tests.
