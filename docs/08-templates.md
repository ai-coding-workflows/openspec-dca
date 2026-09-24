# Reusable templates

The native schema's templates are inputs to OpenSpec's artifact instructions.
Keep them in `openspec/schemas/openspec-ddd/templates/` in an adopting project and
customize them there under version control. They define proposal, impact, delta
specs, design, and tasks; they do not install agent commands.

The additional files in the guide's `templates/` directory cover durable documentation
and evidence. Merge the configuration and agent guidance into existing project files
instead of replacing project-specific instructions. Only require sections that carry
useful information for the change.

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

`verification.md` records results after implementation; it is intentionally not a
required pre-apply artifact. Its existence is not a machine-enforced acceptance gate.
Use project checks or review policy where enforcement is required.
