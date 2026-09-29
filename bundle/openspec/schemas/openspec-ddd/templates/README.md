# OpenSpec DDD template library

This installed library lives at `openspec/schemas/openspec-ddd/templates/`.
Only five files are selected by the native schema as artifact templates. The other
files are optional support/configuration sources and handbook starters. Their presence
does not add artifact IDs, dependencies, commands, or automatic document generation.

## Native artifacts

| Artifact ID | Template | Generated location inside a native change |
| --- | --- | --- |
| proposal | [proposal.md](proposal.md) | `proposal.md` |
| impact | [impact.md](impact.md) | `impact.md` |
| specs | [spec.md](spec.md) | `specs/<exact-capability-path>/spec.md` |
| design | [design.md](design.md) | `design.md` |
| tasks | [tasks.md](tasks.md) | `tasks.md` |

Keep required headings and exact-name delta semantics. Remove placeholder/irrelevant
sections when instantiating; do not publish the unfilled template as a completed artifact.
Schema instructions govern stage behavior. Put project-specific context in the live
config rather than duplicate the entire generic policy in several instruction sources.

## Support templates and destinations

| Source | Use / target relative to the project root |
| --- | --- |
| [config.yaml](config.yaml) | Merge into `openspec/config.yaml`; do not replace local settings |
| [catalog.json](catalog.json) | Optional empty starter for `openspec/catalog.json`; never overwrite existing entries |
| [agent-instructions.md](agent-instructions.md) | Merge into the actual project agent instructions; this file does not register them |
| [openspec-README.md](openspec-README.md) | Adapt as `openspec/README.md` |
| [architecture.md](architecture.md) | An owned `architecture/<view>.md` or suitable focused system view |
| [architectural-decision.md](architectural-decision.md) | One record under the responsible `architectural-decisions/` |
| [domain-model.md](domain-model.md) | Optional `domain/model.md` at the responsible scope |
| [verification.md](verification.md) | Actual evidence in a native change's `verification.md`, not a pre-apply artifact |
| [system-architecture/README.md](system-architecture/README.md) and sibling starters | Useful pages under `openspec/system-architecture/` |

The handbook README lists its available topics. Adapt only useful sections and retain
links only to instantiated/existing sources. Required baseline views can share a page;
a library of thirteen starter files does not require thirteen empty project pages.
The handbook's `architectural-decisions.md` indexes actual records; the singular
`architectural-decision.md` above is the record template. Do not confuse the two.

For native delivery, updates to models, architecture, diagram sources, ADRs/index, and
catalog are explicit work separate from requirement sync. Current views describe
implemented/observed design; accepted targets and actual acceptance remain distinct.
For architecture-only reconstruction, use its approved runtime plan/reviews and do
not create specs, needs, native change metadata, or another task list just to use a
support template. No additional host routing or native artifact is installed here.
