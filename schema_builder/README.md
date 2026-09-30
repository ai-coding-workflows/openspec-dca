# Compose the v3 schema

Build with Python 3.10+ and the standard library. Run from the repository root:

```sh
# DDD without optional documentation conventions.
python3 schema_builder/build.py --output build/schema-ddd/openspec-ddd

# DDD with both architecture and user documentation.
python3 schema_builder/build.py --component arc42 --component user-docs --output build/schema-docs/openspec-ddd
```

Each output is a complete native OpenSpec schema directory with `schema.yaml` and
`templates/`. It retains the native name `openspec-ddd`; the destination's parent
can distinguish builds. Install one chosen build in a project's
`openspec/schemas/openspec-ddd/`, then merge its configuration and agent guidance
starters. Support files are templates, not automatically published documentation.

The builder requires a new output directory. It does not update an installed schema
or merge project customizations. Output beneath `build/` is ignored by Git.
Generated files are not editable sources.

## Source ownership and components

Canonical sources live in
[`bundle/openspec/schema-builder/`](../bundle/openspec/schema-builder/):

- `ddd/files/` owns seven native artifacts, DDD ownership/model rules, local
  architecture, ADR assessments and records, verification, and publication boundaries.
- `components/arc42/` adds handbook templates, locations, navigation, baseline-view
  guidance, and ADR index conventions.
- `components/user-docs/` adds guide, tutorial, and troubleshooting templates plus
  audience, impact, drafting, publication-mapping, and verification guidance.
- `components/architecture-reconstruction/` adds guidance for a separately provided
  architecture-only host workflow. It supplies neither that runtime nor a handbook.
  Select it explicitly when adopting that workflow; arc42 does not require it.

For example, add `--component architecture-reconstruction` to the combined command
when that separate workflow is available. Every component can also be selected alone.
DDD remains the foundation; components do not introduce native artifacts or change
the dependency graph. Artifact readiness, completed tasks, verification, acceptance,
and publication remain separate.

`schema_builder/openspec-ddd_v3/` is the historical supplied snapshot. It is retained
for reference, not edited or used as the generated-output oracle. Whole-block
composition intentionally changes wording and placement. The shipped schema at
`bundle/openspec/schemas/openspec-ddd/` remains the guide's five-artifact installation
default; the builder does not upgrade it implicitly.

## Additive extension format

A hook is a marker on its own line in a base file. For example, inside the impact
artifact's YAML instruction block:

```text
      {{hook:instructions.impact}}
```

Components contribute complete blocks to shared hooks. Contributions append in CLI
selection order; they do not replace base instructions or each other. Unused hooks
render as empty text. The builder separates blocks with blank lines, removes common
fragment indentation, and indents every nonblank line to the marker's indentation.
Relative indentation within a block is preserved. Authors supply ordinary Markdown
or prose, without YAML embedding indentation or a special framing newline.

There are four hook families, with 18 named hooks across 20 insertion points:

| Hook | Destination |
| --- | --- |
| `instructions.<artifact>` | Native instruction body for each of the seven artifacts |
| `instructions.apply` | Native Apply instruction body |
| `template.<artifact>` | Additional sections in each native artifact template |
| `template.verification` | Additional sections in the verification support template |
| `project-guidance` | Project README, agent instructions, and configuration context |
| `support-index` | Support descriptions and relative links in the template-library README |

Artifact names are `proposal`, `impact`, `domain-model`, `specs`, `design`,
`architectural-decisions`, and `tasks`. `project-guidance` is deliberately rendered
in three places, so use self-contained prose and project-relative paths there.
`support-index` is the place for Markdown links relative to the generated `templates/`
directory. Components need only supply hooks relevant to their concern.

Create `components/<name>/component.json` with exactly these fields:

```json
{
  "description": "Optional project documentation",
  "requires": [],
  "contributions": {
    "instructions.impact": "fragments/impact.txt",
    "template.impact": "fragments/impact-section.txt",
    "project-guidance": "fragments/guidance.txt"
  }
}
```

Put extra output files under `files/`, using output-relative paths, and contribution
text under `fragments/`. Multiple hooks may reference one fragment when the same
complete block makes sense at each destination. Adding an ordinary documentation
component requires no base edits; `user-docs` demonstrates composition with arc42.

Dependencies in `requires` must be selected earlier using repeated `--component`
arguments. There is no implicit dependency selection. Unknown hooks/components,
duplicate selections, invalid manifests, overlapping output files, and escaping
fragment paths fail before output is written. Shared hooks are allowed; shared
output-file ownership is not. Component fragments and files must be final text,
without nested hooks or legacy slots.

Hooks extend prose and templates, not YAML structure. Do not use them to insert
artifacts or dependencies. A future need for extra native artifacts requires an
explicit composition design and validation against OpenSpec. Contributions must
preserve native requirement-delta syntax, task tracking, and the base publication
boundary. Structural validation does not detect contradictory prose; review combined
instructions and do not assume component order resolves policy disagreements.

## Migrating from replacement slots

The old `slots` manifest field and inline `{{slot:...}}` markers are unsupported.
Keep the base's general DDD text and move component-specific guidance into complete
blocks at the relevant hooks. Replace word substitutions with explicit component
locations/conventions under `project-guidance`; describe support files under
`support-index`. For the former reconstruction guidance bundled with arc42, select
`architecture-reconstruction` explicitly. Compare generated instructions and merge
installation changes with project customizations; do not overwrite an installation.

## Checks

```sh
OPENSPEC_BIN=/path/to/openspec-1.13.1 python3 -m unittest discover -s tests -v
./scripts/docs.sh build
python3 scripts/md-book/check.py --rendered
```

Builder tests cover additive ordering, DDD independence, reconstruction separation,
indentation, dependencies, malformed contributions, conflicts, and safe output.
Native tests install components alone and in combination into temporary projects,
validate schemas/templates, and check the seven-artifact lifecycle and `skip_specs`.
They inspect contributed native instructions and templates, not only copied files.
These checks do not establish delivery acceptance for an application.
