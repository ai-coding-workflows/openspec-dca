# OpenSpec DDD bundle

From this repository's root, copy the bundle into an initialized OpenSpec
project:

```sh
mkdir -p /path/to/project/openspec
cp -R bundle/openspec/. /path/to/project/openspec/
```

Set `schema: openspec-ddd` in the project's `openspec/config.yaml`, preserving
existing settings. Merge relevant guidance from [the configuration template](openspec/schemas/openspec-ddd/templates/config.yaml)
and [agent instructions](openspec/schemas/openspec-ddd/templates/agent-instructions.md) rather than replacing
project-specific instructions. The copy also includes the optional `ddd/ddd.py`
helper; it is only used when the project has an `openspec/catalog.json` catalog.

For an optional architecture documentation site, install the separate
[mdBook addon](md-book/README.md).

OpenSpec installs its own agent commands with `openspec init --tools pi` (or another
supported integration). This bundle does not copy or fork generated commands.

The optional `openspec/ddd/ddd.py` helper reads an `openspec/catalog.json` catalog:

```sh
python3 openspec/ddd/ddd.py check
python3 openspec/ddd/ddd.py context lending.return
python3 openspec/ddd/ddd.py impact lending.domain
```

Commands produce JSON and never write files. `context` accepts catalog IDs, spec
files, or spec directories and returns prerequisite owners before consumers.
`impact` reports transitive consumers to review; it does not add them to change scope.
Main spec paths must live under `openspec/specs/`. Detailed contract, architecture,
and ADR files may live anywhere inside the project but must be listed explicitly.

Every entry needs a unique `id` and `path`. `depends_on` is an array of consumed
owner IDs. Optional `contracts`, `architecture`, and `decisions` arrays contain
project-relative existing files. `kind` and other descriptive metadata are retained
but have no executable meaning. Cycles, unknown dependencies, duplicate owner paths,
missing files, and paths escaping the project are rejected. Unlisted main specs are
reported so a partial catalog cannot silently appear complete.

New proposed owners remain in the change's impact review until their main specs are
created; then update the catalog. The helper checks the baseline graph only. Agents
must also read proposed deltas and manually review newly introduced dependencies.
It does not discover unlisted ADRs or external consumers and does not infer drift.

Use OpenSpec for creating changes, artifact status, task progress, validation,
synchronization, and archive. No active-change pointer, `change.json`, or separate
planning engine is introduced. Full setup and workflow guidance is in
[the tooling chapter](../docs/09-tooling.md).

For the modular v3 variant, see [the Python schema builder](../schema_builder/README.md).
Its sources live under `openspec/schema-builder/`; select DDD alone or add arc42,
user documentation, and separately selected architecture-reconstruction guidance.
Components contribute additive blocks through shared hooks and own their support files.
