# New DDD project

This is a fresh-project starter, not an implemented application. The installed
`{{schema-name}}` schema contains the selected DDD and optional documentation guidance.
Customize the project name, context, checks, and documentation before relying on them.
Writing prompts and successful rendering are not verified product documentation.

## Initialize your agent integration

From this project root, install the supported OpenSpec release and initialize
its native integration:

```sh
openspec --version
openspec init
openspec schema which {{schema-name}}
openspec schema validate {{schema-name}}
openspec templates --schema {{schema-name}}
```

Select the actual agent integration in the installed CLI. Native OpenSpec generates
agent commands and skills; this template intentionally contains none. Preserve
`openspec/config.yaml` and your existing project instructions/customizations when
updating integrations. Read the installed schema's `templates/README.md` for
support-template responsibilities.

## Review the proposed agent guidance

`AGENTS.proposal.md` combines the DDD foundation, shared group introductions, and
only the selected component instructions. It is a reviewable proposal, not active
agent policy. Review and merge useful sections into the project's `AGENTS.md` or
the chosen agent instruction file, preserving existing rules. Do not maintain two
active copies. This template deliberately does not supply an active `AGENTS.md`.

## Establish the foundation

Use `PROJECT_SETUP.md` with the actual project goal, stack constraints and first
use case. It creates a tested implementation map, core/adapter/composition checks
and executable architecture rules. The prompt authorizes foundation Apply work,
not protected publication or archive. A language/framework has not been selected
by this template. Schema helpers use Python independently of application tooling.

## Ownership and metadata

`openspec/catalog.json` starts empty because no main specifications exist yet.
Catalog use is optional; register only actual maintained main specs and valid references.
Do not create dummy specs or ADRs merely to satisfy checks.

```sh
python3 openspec/schemas/{{schema-name}}/helpers/check.py --root .
```

OpenSpec owns its native change lifecycle. Artifact readiness, completed tasks,
executed verification, and acceptance remain separate states. Native spec sync
merges requirement deltas, not architecture, models, ADRs, catalog entries, or user docs.

## Integration closure

The schema's `templates/integration.json` is a pending evidence starter. During
separately authorized integration, merge requirements, explicitly publish required
companions and reconcile dependent links/maps/catalog. After recording current
snapshots and actual review, run:

```sh
python3 openspec/schemas/{{schema-name}}/helpers/closure.py --root . check --change CHANGE
```

Run this before the final archive move. See the helper README for its format and
limits; it does not merge content, run tests or intercept native archive. Wire the
check into the project's CI/integration wrapper to make failure block closure.

## Documentation variants

If this starter contains `book-builder.toml`, it also includes a relocatable
`scripts/md-book-builder/` package and `scripts/book.sh` / `scripts/book.cmd` wrappers.
Only the selected books are configured. On Windows use `scripts\book.cmd`.

```sh
./scripts/book.sh build
./scripts/book.sh export
python3 openspec/schemas/{{schema-name}}/helpers/docs-check.py --source-only
python3 openspec/schemas/{{schema-name}}/helpers/docs-check.py
```

The first build may download the managed mdBook toolchain. Use `--docker` for the
pinned Docker toolchain instead. Markdown export is configured by default; PDF is
optional and requires its managed dependencies. These commands render/check sources;
they do not establish semantic correctness, delivery acceptance, or site deployment.
Read `scripts/book.md` when present for tooling details.

Architecture sources are under `openspec/system-architecture/` when arc42 is selected.
User-facing sources are under `user-doc/` when user-doc is selected.
Remove unused chapters together with their navigation entries rather than publishing
empty claims. Keep unknowns explicit and replace writing prompts with checked content.

## Updating an adopted project

This directory is a one-time starting point. Never copy a regenerated starter over
an existing project. Diff and merge selected schema/tool updates while preserving
project-owned configuration, sources, integrations, and unrelated work.
