# Fresh-project template sources

`python3 build.py project_templates` composes the four v3 selections into
`build/project_templates/<variant>/`; the root default build also builds schemas.
The installed schema directory matches the variant identifier:
`openspec/schemas/<variant>/`, selected by `schema: <variant>` in
`openspec/config.yaml`. Its contents are byte-identical to `build/schemas/<variant>/`;
the generic `openspec-ddd` name and references inside reusable templates remain
installation defaults. Project guidance is rendered for the chosen name. There is
no legacy project starter.

- `base/`: fresh project landing page/ignore rules and mappings to composed DDD guidance.
  Its README source uses `{{schema-name}}` so generated project commands name the
  selected variant.
- `arc42/`: book configuration/navigation and mappings to canonical arc42 templates.
- `user-doc/`: reader landing page/navigation/configuration and mappings to canonical
  user-doc writing templates. The schema library README is deliberately
  not published as the reader landing page.
- `documentation/`: shared wrapper/guide mappings and an explicit maintained book-tool
  payload and shared agent-guidance intro, selected once when an active component
  belongs to the documentation group or one of its descendants.
- `guidance.json`: deterministic group order, parent relationships, always-active
  groups, canonical group intros, and shared package selection.

Manifests define project file destinations and references to repository sources
or `schema:`-prefixed composed files. They also define structured book entries;
the builder renders `book-builder.toml`. Do not maintain another schema copy here.
The canonical reusable book tool remains under `scripts/md-book-builder/`; explicit
packaging excludes all runtime caches, bytecode, virtual environments, and generated assets.

Only `AGENTS.proposal.md` is generated, not an active `AGENTS.md`. Review and merge
it into the chosen project instruction file rather than maintaining a second policy.
The DDD foundation reuses the unextended canonical base template; selected components
reuse their existing canonical agent fragments. A component's `guidance` declaration
names its group, section title, and source. Activation propagates to parent groups;
shared intros/packages appear once. This supports additional groups and nested
component families without hardcoded arc42/user-doc branches. Inactive groups and
unresolved composition markers never appear in generated proposals.

Arc42 pages reuse `src/schemas/components/arc42/files/templates/system-architecture/`.
The smaller `src/addons/mdbook/` remains a distinct minimal publishing entry point
for existing projects, not another maintained set of full arc42 pages.

These are one-time sources for empty projects, not implemented applications or
verified manuals. No command prompts, sample specs, or accepted decisions are
invented. Regenerating owned distribution output is safe; copying it over an
adopted project's customized sources is not an update strategy.

See [builder authoring and safety](../../scripts/starter-builder/README.md).
