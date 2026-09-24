# Reusable templates

The native schema's templates are inputs to OpenSpec's artifact instructions.
Keep them in `openspec/schemas/openspec-ddd/templates/` in an adopting project and
customize them there under version control. They define proposal, impact, delta
specs, design, and tasks; they do not install agent commands.

The additional files in the guide's `templates/` directory cover durable documentation
and evidence. Merge the configuration and agent guidance into existing project files
instead of replacing project-specific instructions. Only require sections that carry
useful information for the change.

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
{{#include ../bundle/openspec/schemas/openspec-ddd/templates/impact.md}}
```

## Architecture fragment template

```markdown
{{#include ../templates/architecture.md}}
```

## Decision template

```markdown
{{#include ../templates/decision.md}}
```

## Verification template

```markdown
{{#include ../templates/verification.md}}
```

`design.md` holds the verification strategy; `verification.md` records actual results
after implementation and is intentionally not a required pre-apply artifact. Identify
the tested code revision, specification basis, and execution context. Its existence is
not a machine-enforced acceptance gate. Use project checks or review policy where
enforcement is required.
