# User documentation templates

These are reusable content types, not extra OpenSpec artifacts, mandatory chapters
or permanent catch-all files. Use the [base documentation policy](../documentation-policy.md)
for audiences, granularity and check classes. A project's users may be administrators,
operators, integrators or developers. Installation, setup, operation, integration
and everyday use belong when relevant; separate books are not mandatory.

## Locations and ownership

The installed library is `openspec/schemas/openspec-ddd/templates/user-doc/`.
Maintained content defaults to project-root `user-doc/`; reuse an explicitly selected
existing root rather than migrate it. Optional planning drafts can live under
`openspec/changes/<change>/user-doc/`. The library is not a completed manual.

Planning is change-local. Apply delivers explicitly mapped descriptive sources in
the local development checkout, preserving current/unrelated edits. The entire
`openspec/specs/**` tree and maintained models/ADRs/catalog remain protected even
when an index/view looks descriptive. Prepare protected revisions in the change;
actual publication and dependent links use the base non-checkbox Integration Handoff.
Do not link transient drafts or invent missing targets. Task completion, integration,
acceptance and deployment are separate; this component grants no deployment authority.

## Choose a type, then name the actual topic

| Reader need | Reusable starter |
| --- | --- |
| Learn a first complete outcome with a controlled example | [Tutorial](tutorial.md) |
| Complete a real task, including installation or configuration | [How-to](how-to.md) |
| Look up exact settings, commands or supported options | [Reference](reference.md) |
| Understand a concept or important limit | [Explanation](explanation.md) |
| Recognize and safely recover from a problem | [Troubleshooting](troubleshooting.md) |

Name pages for actual reader questions; template filenames are not required targets.
A tutorial may connect installation, setup and first use. A reference may cover
related commands. Split independent topics when navigation or prerequisites demand
it, not at an arbitrary word count. Keep coherent procedures and local warnings
together. Distinguish source topics from generated single-file books or exports.

Expose audiences, prerequisites, supported versions and outcomes through the title,
introduction or navigation where sufficient; do not require per-page metadata blocks.
Explain needed terms using the shared language and link authoritative definitions
accessible to the reader in the intended output. No competing rule/value lists.
Technical detail belongs when useful to the actual reader, not merely because it
appeared in a change or source file. Keep history distinct from current guidance.

Use screenshots/diagrams only to explain a real question; provide captions or text
alternatives, safe sample data and accurate versioned sources. Never invent screens,
roles, commands, settings/defaults or results. Keep unknowns in working artifacts
and report what they block. Do not publish unfilled starters or authoring prompts.

## Plan and verify within the existing workflow

Impact assesses affected readers and whole units, including reuse/no-impact. Design
keeps one map of audience/need, inspected basis, action/target and checks, referencing
the existing project profile. Include navigation/assets/configuration references,
old links/anchors and approved generator sources/outputs. Tasks has one Apply list;
verification records current results, actual evidence and exceptions. No eighth
artifact or repeated inventory. A page edit needs no dummy documentation requirement.

Read maintained targets before editing; review reused surrounding content and overlaps,
not only new paragraphs. Run selected structural gates and investigate size/growth/
duplication signals. Record split/consolidate/keep decisions and justified exceptions
without filling a form for every page. Check intended published destinations, not
only source-file existence. A render/link pass does not prove a procedure works.
Execute only authorized risk-relevant examples in isolation, without live credentials,
unapproved external writes or arbitrary extracted code blocks. Distinguish inspection,
execution, Not run and limits in the existing verification evidence.

Use approved generator mappings and inspect incidental output. Forbid writes into
protected targets. Do not introduce tools, CI, services or deployment merely to make
a check pass. Native sync merges requirements, not these pages or their companions.

## Component and starter scope

This component is independent of arc42. It installs no splitter, linter rules, CI,
reference generator or publisher. Existing accepted documentation obligations remain
binding when the component is absent. Merge generated guidance deliberately.

The fresh-project starter creates only book configuration, a draft landing page
and minimal navigation. It does not instantiate each content type. Select useful
topics from this library, write and verify them, then link them. The draft landing
page must be replaced before publication; a preview is not a ready handbook.
