# OpenSpec DDD bundle

Editable sources live here: `schemas/ddd/`, `schemas/components/`,
`schemas/legacy/`, `schemas/ddd/helpers/`, `schemas/helper-packs/docs/`, and
`addons/mdbook/`, and `project_templates/`.
Build and install a selected schema from the repository root:

```sh
python3 build.py
mkdir -p /path/to/project/openspec/schemas
cp -R build/schemas/ddd /path/to/project/openspec/schemas/openspec-ddd
```

Select another generated variant when needed. Set `schema: openspec-ddd` in the
project's configuration and merge the selected output's `templates/config.yaml`
and `templates/agent-instructions.md`, preserving existing settings.
The five-artifact worked example uses `build/schemas/legacy/`.

Every composed v3 schema includes its `helpers/` directory automatically; do not
copy helpers a second time. The historical five-artifact `legacy` output adds no
helpers. If desired, copy the optional canonical helpers separately for legacy:

```sh
cp -R src/schemas/ddd/helpers /path/to/project/openspec/schemas/openspec-ddd/helpers
```

The catalog commands use `openspec/catalog.json`; the separate metadata checker
also works without a catalog. For optional architecture publishing, install the
separate [mdBook addon](addons/mdbook/README.md).

OpenSpec installs its own agent commands with `openspec init --tools pi` (or another
supported integration). This bundle does not copy or fork generated commands.

From the adopting project's root, the installed helper reads an
`openspec/catalog.json` catalog:

```sh
python3 openspec/schemas/openspec-ddd/helpers/ddd.py check
python3 openspec/schemas/openspec-ddd/helpers/ddd.py context lending.return
python3 openspec/schemas/openspec-ddd/helpers/ddd.py impact lending.domain
python3 openspec/schemas/openspec-ddd/helpers/check.py --root .
```

The shared standard-library `project_root.py` resolves the default root from the
installed helpers' nearest `openspec` ancestor to its project parent, not a fixed
path depth. Explicit `--root` is supported (`ddd.py --root PATH check`). The older
`openspec/ddd/` installation remains a supported fallback, not the primary layout.

Both arc42 and user-doc select the shared generic documentation helper pack. Its
`docs-check.py` uses adjacent `check.py` for DDD metadata and a separately installed
`md-book-builder/book.py` for generic source/include/HTML checks and builds. Select
that builder with `--builder` or `BOOK_BUILDER`; it may live in arbitrary folders.
Use `--ddd-helper` for an alternate metadata checker or ambiguous multi-schema
installations. No arc42-specific conformance checker is distributed.

`ddd.py` commands produce JSON and never write files. `context` accepts catalog IDs, spec
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

For an empty new project, `python3 build.py project_templates` generates the four v3
compositions under `build/project_templates/`. Their manifests in `project_templates/` map existing
composed schema templates to project destinations and add project-only skeletons.
Documentation variants include selected books and the canonical reusable book tool;
DDD-only has no publishing dependency. Group declarations and component metadata
assemble a reviewable `AGENTS.proposal.md`, not an active `AGENTS.md`. Shared intros
and packages occur once through group/ancestor activation; canonical agent fragments
are not copied into a second maintained source. `python3 build.py` builds both collections.
Do not use starters to overwrite existing projects. See
[the starter builder](../scripts/starter-builder/README.md).

For the modular v3 variant, see [the Python schema builder](../scripts/schema-builder/README.md).
Its sources live under `src/schemas/`; select DDD alone or add arc42,
user documentation, and separately selected architecture-reconstruction guidance.
Components contribute additive blocks through shared hooks and own their support files.
