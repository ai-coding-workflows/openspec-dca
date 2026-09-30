# User-documentation templates

Use these optional starters for people who use or configure the product. They are
not the product manual and not extra OpenSpec artifacts. Remove authoring comments
and sections that do not help the reader when writing a real page. Keep the project's
chosen language and explain necessary technical terms before relying on them.

## Where the files belong

| Purpose | Location |
| --- | --- |
| Installed template library | `openspec/schemas/openspec-ddd/templates/user-documentation/` |
| Proposed text and supporting assets | `openspec/changes/<change>/user-documentation/` |
| Maintained user documentation | `user-documentation/` at the project root |
| Maintained system architecture, when arc42 is selected | `openspec/system-architecture/` |

The draft and maintained folder share a name but not a lifecycle. During planning
and Apply, change-local drafts may be written; the maintained root and mapped assets
stay unchanged, including newly proposed pages. Use the separately authorized
Integration Handoff for promotion. A spec sync does not publish user pages.

An existing project-root documentation directory may be retained when explicitly
chosen in project instructions and design mappings. Do not move it automatically.
The builder installs templates, not a populated root handbook. Copying this README
as the user's handbook would publish process instructions, not product help.

## Choose a page for the reader's question

| Need | Starter |
| --- | --- |
| Learn a first complete task with a controlled example | [Tutorial](tutorial.md) |
| Complete a real task, including configuration | [How-to](how-to.md) |
| Look up exact values, settings, or supported options | [Reference](reference.md) |
| Understand a concept, outcome, or important limit | [Explanation](explanation.md) |
| Recognize and safely recover from a problem | [Troubleshooting](troubleshooting.md) |

Start with a short purpose and expected outcome. Name real entry points and needed
permissions. Keep warnings before the affected action; missing, cleared, rejected,
and retried values must not become interchangeable just to shorten the text.
Do not publish guessed menus, defaults, commands, role names, or results. Record
unknowns in the change's working artifacts until resolved for the affected page.

## Reading structure, not architecture structure

Design navigation around reader goals and audiences. A function overview can link
to several tasks; one task may cross several specs. No page-per-spec rule, mandatory
folder tree, or arc42 numbering applies. Configuration instructions and complete
setting references serve different questions: link them rather than repeat every
value in both places. Keep internal evidence paths and draft review notes out of
public prose unless they genuinely serve the reader.

When pages become difficult to scan, first look for mixed goals or audiences. Split
independently useful topics and retain a short overview and links. Keep a coherent
procedure together when a split would make the task harder. A long parameter list
may remain a single reference if it is easy to search and navigate. Length signals
need review, not automatic deletion or arbitrary page splitting.

Use a screenshot to locate a control, a flow diagram to explain a user's choices,
or a concept diagram to explain a relationship. Include text steps, captions or
text alternatives, and the important conditions. Reuse accurate sources, keep an
editable diagram source, use safe sample data, and check the supported product
version. Do not invent screenshots or copy internal component diagrams without a
reader need. No renderer is required merely because a template mentions diagrams.

## Participate in the existing DDD process

Impact owns the reader/page coverage assessment, including reasoned no-change results.
Design owns the page structure and exact source/draft/destination mapping. Tasks
contains the one Apply checklist for writing and checking drafts. Verification
records actual checks and gaps. The non-checkbox Integration Handoff references
the design mapping; it is not another inventory or an implicit release command.
Model meanings and normative guarantees remain in their existing owning sources.
Add documentation requirements only for actual changed obligations, not every edit.

Check syntax, links/navigation, exact examples/settings, and important user tasks at
appropriate levels. Review the combined proposed book or pages, not only isolated
drafts, accounting for renamed or removed content and unchanged context. Use safe,
authorized examples without real secrets or unapproved external writes. Record the
product/docs snapshot, roles, commands or walkthroughs, actual results, and limits.
A green build does not prove the procedure works. A source test is not a test run.

Before promotion, re-read the current destination, reconcile concurrent changes,
check availability in the intended product version, and resolve final links and
navigation. Rendering for review is not deployment. Ready for acceptance, accepted,
integrated, and published are distinct states.

## Scope of this component

This component has no dependency on arc42 or architecture reconstruction. It
supplies prose hooks and these support templates only: no eighth artifact, native
configuration flag, index schema, automatic splitter, mdBook setup, linter rules,
CI, generated reference pipeline, or runtime implementation. Tools and existing
documentation obligations are adopted explicitly by the project. Not selecting
this component never waives already accepted documentation requirements.
