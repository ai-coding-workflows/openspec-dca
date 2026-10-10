# Build OpenSpec schemas

Build with Python 3.10+ and the standard library. The root `build.py` dispatches
to `scripts/schema-builder/build.py`; both entry points remain available.
Run from the repository root:

```sh
# All four compositions plus the separate unchanged legacy schema.
python3 build.py schemas

# One DDD schema without optional components, in a new directory.
python3 build.py schemas --base --output build/schema-ddd/openspec-ddd

# DDD with both architecture and user documentation.
python3 build.py schemas --component arc42 --component user-doc --output build/schema-docs/openspec-ddd
```

Each composed v3 output is a complete native OpenSpec schema directory with
`schema.yaml`, `templates/`, and `helpers/` directly in the variant directory.
Install one chosen build under
the name `openspec-ddd` in a project's
`openspec/schemas/openspec-ddd/`, then review and merge its generated configuration,
agent-instruction (for example, AGENTS.md), and README starters into project-owned
files, preserving customizations. Copying the chosen schema includes its helpers
without a second copy. Schema-only support templates are not automatically published documentation.

For an empty new project, use `python3 build.py project_templates` to assemble those sources
into project destinations with optional ready-to-build documentation skeletons.
The root default command builds both schemas and project templates; explicit `schemas`
remains schema-only. See [the starter builder](../starter-builder/README.md).

The default build writes `build/schemas/<variant>/`, plus `index.json`
and a readable `README.md`. For example, `ddd+arc42+user-doc` contains DDD with
both documentation components. The four compositions are `ddd`, `ddd+arc42`,
`ddd+user-doc`, and `ddd+arc42+user-doc`, plus unchanged `legacy`.
The native schema name stays `openspec-ddd`.
Components are discovered from `component.json`; all dependency-valid subsets are
built once in a deterministic dependency order. Unknown dependencies, cycles, and
composition conflicts fail the build. Component order does not resolve prose conflicts.

Repeated matrix builds replace only output whose ownership manifest and content
hashes still match. Unowned directories, symlinks, and changed output are rejected.
All variants are composed and staged before replacing the previous output. A matrix
build can use another dedicated directory with `--output`; never point it at an
installed schema or a shared output directory such as `build/` itself.

Single-schema builds (`--base`, repeated `--component`, or `--legacy`) require a new
`--output` directory. They never update installed schemas or merge customizations.
Output beneath `build/` is ignored by Git. Generated files are not editable sources.

## Source ownership and components

Canonical sources live in
[`src/schemas/`](../../src/schemas/):

- `ddd/files/` owns seven native artifacts, DDD ownership/model rules, local
  descriptive architecture preparation/publication mappings, ADR assessments and records, verification,
  and protected contract/model/ADR/catalog publication boundaries.
- `ddd/helpers/` owns `ddd.py`, `check.py`, the shared canonical ADR reader
  `model.py` and standard-library
  `project_root.py`. The whole helper directory,
  including `model.py`, is included automatically in every composed v3 output
  under `helpers/`.
- `helper-packs/docs/` owns the single canonical thin `docs-check.py` orchestrator.
- `components/arc42/` adds handbook templates, locations, navigation, baseline-view
  guidance, and ADR index conventions. Its `helpers/` owns the optional mdBook
  `adr-preprocessor.py`, distributed only when arc42 is selected.
- `components/user-doc/` adds guide, tutorial, and troubleshooting templates plus
  audience, impact, optional planning drafts, maintained-page delivery mappings, and
  verification guidance.

Architecture reconstruction remains a separate host workflow, not a schema component
or a builder selection. Each documentation component can be selected independently.
DDD remains the foundation; components do not introduce native artifacts or change
the dependency graph. Artifact readiness, completed tasks, verification, acceptance,
and publication remain separate.

`src/schemas/legacy/openspec-ddd/` retains the five-artifact schema used by the
handbook's existing worked example. The build copies it to
`build/schemas/legacy/`. It is a separate supported workflow, not a
snapshot of the composed seven-artifact schema. New compositions use `ddd/files/`;
this repository layout change does not migrate existing projects or example artifacts.
Legacy remains historical and unchanged: no helpers are automatically added. A legacy
adopter may separately copy `src/schemas/ddd/helpers/` into its installed schema's
`helpers/` directory.

## Additive extension format

A hook is a marker on its own line in a base file. For example, inside the impact
artifact's YAML instruction block:

```text
      {{hook:instructions.impact}}
```

Components contribute complete blocks to shared hooks through the existing manifest
`contributions` field. Contributions append in CLI selection order; matrix builds use
stable dependency order. They do not replace base instructions or each other. Ordinary
prose rendering separates blocks with blank lines, removes common fragment indentation,
and indents nonblank lines to the marker's indentation, preserving relative indentation.
Unused hooks disappear. Authors supply ordinary Markdown or prose, without embedding
indentation or a special framing newline.

Operation hooks use a separate safe item renderer: each fragment is one nonempty plain
prose guidance item (possibly multiline). The builder uses `json.dumps()` to quote the
entire item as a YAML-compatible string, supplies indentation and the list marker, and
preserves Unicode through escapes. YAML-looking text remains literal string content,
not list items, mappings, tags, or new OpenSpec fields. Do not author YAML structure or
nested hook markers. Ordinary project and artifact prose keeps its ordinary renderer.
Operation markers are allowed only once each in `templates/config.yaml`, under the
matching `operations.apply.guidance` or `operations.archive.guidance` at six-space
indentation. Invalid placement and unknown operation hooks fail before output is written.

There are five hook families, with 22 named hooks across 22 insertion points:
8 native instructions (seven artifacts plus Apply), 8 templates (seven native plus
verification), 3 project destinations, 2 operation destinations, and 1 support index.

| Hook | Destination |
| --- | --- |
| `instructions.<artifact>` | Native instruction body for each of the seven artifacts |
| `instructions.apply` | Native Apply instruction body |
| `template.<artifact>` | Additional sections in each native artifact template |
| `template.verification` | Additional sections in the verification support template |
| `project.context` | Configuration context: concise component facts, locations, conventions |
| `project.agent-instructions` | Agent-instruction starter: component execution and ownership obligations |
| `project.readme` | OpenSpec README starter: reader-friendly role and lifecycle |
| `operation.apply` | Configuration Apply guidance: one safely rendered prose item |
| `operation.archive` | Configuration archive guidance: one safely rendered prose item |
| `support-index` | Support descriptions and relative links in the template-library README |

Artifact names are `proposal`, `impact`, `domain-model`, `specs`, `design`,
`architectural-decisions`, and `tasks`. Keep the three project destinations distinct;
do not repeat full policy in all three. Generic lifecycle and protected-publication
contracts belong to the DDD base; components add scope-specific reminders and targets.
`support-index` is the place for Markdown links relative to the generated `templates/`
directory. Components need only supply hooks relevant to their concern.

Create `components/<name>/component.json` with these fields (the optional
`helper-packs` field selects shared helper providers):

```json
{
  "description": "Optional project documentation",
  "requires": [],
  "helper-packs": ["docs"],
  "contributions": {
    "instructions.impact": "fragments/impact.txt",
    "template.impact": "fragments/impact-section.txt",
    "project.context": "fragments/project-context.txt",
    "project.agent-instructions": "fragments/project-agent-instructions.txt",
    "project.readme": "fragments/project-readme.txt",
    "operation.apply": "fragments/operation-apply.txt",
    "operation.archive": "fragments/operation-archive.txt"
  }
}
```

Put extra output files under `files/`, using output-relative paths, and contribution
text under `fragments/`. Use destination-specific project fragments instead of copying
the same full policy into context, agent instructions, and README. Operation fragments are plain prose
items, not preformatted YAML. Adding an ordinary documentation
component requires no base edits; `user-doc` demonstrates composition with arc42.

A component's optional `helpers/` directory is copied into output `helpers/`.
`helper-packs: ["docs"]` references `src/schemas/helper-packs/docs/`; a selected
provider is copied once even when both arc42 and user-doc request it. Distinct
providers claiming the same output file fail, even with identical bytes. The sole
file-collision exception is `helpers/README.md`: preserve the base README as the
first section, then append deterministic sections headed `Helper pack: docs`,
`Component: arc42`, and `Component: user-doc` for the selected providers.

Both documentation components distribute the same generic `docs-check.py`, not an
arc42-conformance checker. It invokes adjacent `check.py` for optional DDD metadata
and requires a separately installed generic builder via `--builder` or
`BOOK_BUILDER`. Only conventional `<root>/scripts/md-book-builder/book.py` discovery
is provided as a convenience; arbitrary builder locations are supported. Generic
source/include/HTML validation and builds remain in `scripts/md-book-builder/`,
which contains no DDD validation or ADR generation. The canonical orchestrator is
`src/schemas/helper-packs/docs/docs-check.py`, installed as
`openspec/schemas/openspec-ddd/helpers/docs-check.py`. Its metadata stage continues to use
`check.check_project`; it adds no parallel manifest. `model.py` reads canonical ADR
source without validation or rewriting; `check.validate_decisions` is an explicit
preflight for project-owned renderers. Catalog/graph logic remains in `ddd.py`,
not a second catalog model. See the [helper API](../../src/schemas/ddd/helpers/README.md#shared-adr-reading-api).
Rebuilding or installing helpers does not migrate an adopted ADR source format.
The arc42 component's optional `adr-preprocessor.py` generates a directory-grouped book view only
when explicitly configured in `[preprocessor.adr]` and given one `{{#adr-index}}`
marker. It shares the model and generic validation, supports HTML and `book-export`,
and leaves maintained records/indexes unchanged. Installation does not activate it.
See the [ADR view setup](../../src/schemas/components/arc42/helpers/README.md#optional-mdbook-adr-view).

From the adopting project's root:

```sh
python3 openspec/schemas/openspec-ddd/helpers/ddd.py check
python3 openspec/schemas/openspec-ddd/helpers/ddd.py context OWNER
python3 openspec/schemas/openspec-ddd/helpers/ddd.py impact OWNER
python3 openspec/schemas/openspec-ddd/helpers/check.py --root .
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
```

DDD helper commands are unchanged. Default root discovery uses the installed
helpers' nearest `openspec` ancestor and its project parent, not a fixed depth;
explicit `--root` is supported. `--ddd-helper` selects an alternate metadata
checker when needed, including ambiguous multi-schema installations. Legacy
`openspec/ddd/` is still a supported fallback, not the recommended primary layout.

Dependencies in `requires` must be selected earlier using repeated `--component`
arguments. There is no implicit dependency selection. Unknown hooks/components,
duplicate selections, invalid manifests, overlapping output files, and escaping
fragment paths fail before output is written. Shared hooks are allowed; shared
output-file ownership is not, except the composed `helpers/README.md` described
above. Component fragments and files must be final text,
without nested hooks or legacy slots.

Hooks extend prose and templates, not YAML structure. Do not use them to insert
artifacts or dependencies. A future need for extra native artifacts requires an
explicit composition design and validation against OpenSpec. Contributions must
preserve native requirement-delta syntax and task tracking. Planning stays change-local;
Apply updates mapped descriptive sources outside `openspec/specs/**`, such as the arc42
handbook at `openspec/system-architecture/`, project-root user docs, and approved navigation/
assets, and checks actual maintained targets. The entire `openspec/specs/**` tree remains
read-only during planning and Apply, including specs, local architecture, diagrams/assets,
models, and indexes: no create/edit/remove/rename or indirect/generated writes. Prepare and
check protected local-view proposals and source-to-maintained-target mappings inside the
change in the one Apply checklist. Their actual publication and dependent links remain in
the non-checkbox Integration handoff for separately authorized sync/archive-stage integration.
Companion publication is explicit work, not automatic native sync; native sync merges only
requirement deltas, never local architecture or other non-spec documents. Do not label staged
views delivered/maintained-current or claim no pending publication while it remains.
Maintained model companions, ADR records/status, catalog, shared-store, acceptance, and
deployment protections continue even outside that tree. Components add descriptive targets,
not exceptions to these protections or links to drafts/nonexistent protected targets. Structural
validation does not detect contradictory prose; review combined instructions and do not
assume component order resolves policy disagreements.

## Migrating from replacement slots

The old `slots` manifest field and inline `{{slot:...}}` markers are unsupported.
Keep the base's general DDD text and move component-specific guidance into complete
blocks at the relevant hooks. Replace word substitutions with explicit component
locations/conventions under `project.context`; describe support files under
`support-index`. Architecture reconstruction remains a separate host workflow, not
a selectable package. Compare generated instructions and review/merge installation
changes with project customizations; do not overwrite an installation.

### Migrating custom project guidance

Repository-owned manifests and base destinations migrate atomically. The old
`project-guidance` hook has no compatibility alias: unknown-hook failures direct
custom component authors to `project.context`, `project.agent-instructions`, and
`project.readme`. Split its substance into concise project facts, execution/ownership
obligations, and a reader-friendly role/lifecycle explanation respectively. Move
scoped Apply/check reminders into `operation.apply`; use `operation.archive` for
maintained-target/link/check confirmation and explicit remaining deferrals/status.
Keep existing native instruction, template, and support-index contributions.

Use the manifest example above and put one nonempty plain prose item in each operation
fragment. Do not supply YAML structure, nested hooks, or new native fields; the builder
owns list markers and string quoting.
The Python standard-library builder needs no new dependency. Generated config guidance
is an installation starter: review and merge it, AGENTS/agent instructions, and README
into existing project-owned files. A rebuild does not rewrite installed customizations
or authorize documentation publication or deployment.

## Checks

```sh
OPENSPEC_BIN=/path/to/openspec-1.13.1 python3 -m unittest discover -s tests -v
./scripts/book.sh build
python3 scripts/md-book-builder/check.py --rendered
```

Documentation commands use `scripts/md-book-builder/book.py` (also through
`build.py docs`); see the [book builder guide](../book.md). Root `book-builder.toml`
selects books and their export/serve settings when present; absent it, the runner
discovers root `book.toml` and `book.*.toml`. The checker stays single-book with
root `book.toml` as its default and supports `--config`/`--book`. It checks sources
and existing HTML without building or validating DDD metadata; use the docs
orchestrator for optional metadata checks plus source/build/rendered checks.

Builder checks cover additive ordering, DDD independence, destination-specific prose,
safe operation-item rendering, indentation, dependencies, malformed contributions,
conflicts, and safe output.
Native tests install components alone and in combination into temporary projects,
validate schemas/templates, and check the seven-artifact lifecycle and `skip_specs`.
They inspect contributed native instructions and templates, not only copied files.
These checks do not establish delivery acceptance for an application.
