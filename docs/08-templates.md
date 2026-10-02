# Reusable templates

The native schema's templates are inputs to OpenSpec's artifact instructions.
Keep them in `openspec/schemas/openspec-ddd/templates/` in an adopting project and
customize them there under version control. They define proposal, impact, delta
specs, design, and tasks; they do not install agent commands.

The additional files in `src/schemas/legacy/openspec-ddd/templates/` cover the OpenSpec
entry point, optional system handbook sections, domain models, local architecture,
architectural decisions, and evidence. Merge the configuration and agent guidance
into existing project files instead of replacing project-specific instructions. Only require sections that carry
useful information for the change.

### Template names and destinations

Paths in the first column refer to this guide's template sources; destinations
refer to the adopting project. A destination is created only when useful.

| Template source | Destination |
| --- | --- |
| `templates/openspec-README.md` | `openspec/README.md` |
| Selected files from `templates/system-architecture/` | Corresponding pages under `openspec/system-architecture/` |
| `templates/domain-model.md` | The responsible domain's `model.md`, when a companion is useful |
| `templates/architecture.md` | `architecture/<view>.md` at the responsible context, technical-capability, system-responsibility, or narrower scope |
| `templates/architectural-decision.md` | `<scope>/architectural-decisions/<adr-id>.md`; proposed records may start in `openspec/changes/<change>/architectural-decisions/` |
| `templates/verification.md` | `openspec/changes/<change>/verification.md` |

The handbook's `architectural-decisions.md` indexes ADRs; it is not produced by
copying the ADR template into the handbook. An architecture fragment does not
require a placeholder spec, and a new technical capability does not require an
empty copy of every template. See the [scope layout](03-structure.md).

## Keep instructions and templates aligned

Project configuration supplies concise context and artifact-specific authoring
rules. Agent instructions describe the cross-artifact working rules. Templates
structure individual outputs. Keep their terminology and expectations consistent
without copying the entire handbook into every prompt or demanding identical
sections from every owner.

| Native artifact | Authoring expectation |
| --- | --- |
| Proposal | Explain need, actors, outcome, scope, non-goals, and observable acceptance; reference existing goals rather than create a mandatory needs hierarchy |
| Impact | Review owners and consumers; record actual contract-delta coverage and model/view/ADR changes, including create, update, or reuse and unresolved choices |
| Specs | Keep native requirement/scenario headings, exact-name merge semantics, and complete modified requirements; tailor questions to the owning contract |
| Design | Explain the approach, relevant alternatives, proposed views and destinations, compatibility, open decisions, and verification strategy for the next slices |
| Tasks | Maintain one actionable backlog covering tests, implementation, relevant model/diagram/ADR/catalog updates, and actual evidence |

Merge these prompts into the relevant existing sections of the installed schema
rather than appending a second design or task list. Keep the schema's artifact IDs
and dependencies unchanged. A documentation-only effect can be described in impact's
consequences without inventing a catalog owner or relying on a new parser disposition.
Views and verification remain part of existing artifacts, not new native gates.

## Owner-specific writing prompts

Keep OpenSpec's native requirement/scenario structure, but select prompts by owner
rather than requiring every spec to answer the same questions. A requirement states
an obligation; a scenario gives an observable example. Use a domain model companion
for definitions and relationships that do not themselves state obligations.

| Owner | Useful prompts |
| --- | --- |
| Domain | Which model definitions, invariants, and transitions govern this behavior? |
| Feature | Whose goal is served, and what outcomes and rejections are observable? |
| Port | What obligations, guarantees, and failure semantics cross the boundary? |
| Adapter | How are external representations and outcomes mapped to the owned contracts? |

If the project maintains `domain/model.md`, keep each definition authoritative in
one place. Proposed model edits belong in change-local planning text with affected
requirements identified; accepted model updates need an explicit task because native
requirement sync does not merge them.

## Impact review template

```markdown
{{#include ../src/schemas/legacy/openspec-ddd/templates/impact.md}}
```

## System handbook starters

Copy `templates/openspec-README.md` to `openspec/README.md` and
`templates/system-architecture/README.md` to `openspec/system-architecture/README.md`.
Add only the handbook sections your system needs; the supplied section starters
show scope and ownership, not mandatory empty pages. Link authoritative contracts,
models, local views, and scoped ADRs rather than copying them.

The handbook overview should link a context overview and high-level structural
diagram, including adequate pre-existing sources. Apply the
[view selection and maintenance rules](04-architecture-documentation.md#architecture-views-and-diagrams)
without generating empty sections. A partial brownfield baseline states its covered
scope and evidence gaps rather than claiming all views are complete.

## Domain-model companion template

```markdown
{{#include ../src/schemas/legacy/openspec-ddd/templates/domain-model.md}}
```

Keep normative behavior at its owner and reference those rules from the model.
For architecture-only reconstruction, omit a contract link that does not yet exist;
record observed meanings and evidence without creating requirements. This template
is optional and introduces neither a native artifact nor a second spec owner.

## Architecture fragment template

State the question, scope, and current/proposed status. Include or reference the
single editable diagram source when the view policy requires one, explain the
relationship semantics, and identify material assumptions or omissions. Cross-scope
views name their responsibilities and boundary roles. Optional code entry points
provide navigation, not a conformance claim.

```markdown
{{#include ../src/schemas/legacy/openspec-ddd/templates/architecture.md}}
```

## Architectural decision template

Separate the decision, alternatives, and consequences. Record actual acceptance
and supersession without assuming that an accepted decision has been implemented.
Preserve historical rationale, link delivery and verification, and do not invent
alternatives for a reconstructed decision. Use the record's existing identity even
when its directory or implementation location changes.

```markdown
{{#include ../src/schemas/legacy/openspec-ddd/templates/architectural-decision.md}}
```

## Verification template

```markdown
{{#include ../src/schemas/legacy/openspec-ddd/templates/verification.md}}
```

`design.md` holds the verification strategy; `verification.md` records actual results
as checks are performed and is intentionally not a required pre-apply artifact.
Identify the checked code or documentation revision, specification basis, and
execution context. Distinguish verification progress from the actual acceptance
decision. Passed, failed, not-run, and partial checks retain their real results even
when a limitation is accepted. Link corrective work or authorized follow-up instead
of creating a second backlog. The file's existence is not a machine-enforced
acceptance gate; use project checks or review policy where enforcement is required.
