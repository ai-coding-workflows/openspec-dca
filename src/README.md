# OpenSpec DDD modular bundle



## Contents

- `schemas/ddd/`: canonical base schema, support templates and read-only helpers.
- `schemas/components/`: optional arc42 and user-doc fragments/templates/helpers.
- `schemas/helper-packs/docs/`, `addons/`: retained documentation support.
- `project_templates/`: starter sources; the user-doc manifest intentionally stops
  instantiating empty type-based chapters. The base manifest still maps the canonical
  setup prompt to `PROJECT_SETUP.md`. Existing project files are not migrated/deleted.
- `dist/schemas/`: four generated, installable compositions, not additional sources.
- `tools/compose_schemas.py`: small reference composer for this archive's hook format.
- `tests/`: executable helper, composition, failure-path and reproducibility tests.

The uploaded archive did **not** include its referenced `build.py`, original schema
and starter builders, or the reusable mdBook builder. The reference composer builds
schemas plus helpers only; it does not claim to replace those tools or generate full
project starters/books. Merge these source changes into the corresponding locations
of the original repository and use that repository's normal builder when available.

## Install one generated schema

For example, copy `dist/schemas/ddd+arc42+user-doc/` to the new project's
`openspec/schemas/ddd+arc42+user-doc/`. Choose `ddd`, `ddd+arc42`, or `ddd+user-doc`
instead when those components are not needed. Keep the adjacent `helpers/` directory.

Merge the selected output's `templates/config.yaml` into `openspec/config.yaml`
and its `templates/agent-instructions.md` into the project's actual agent guidance.
Preserve existing settings and do not activate a second conflicting instruction file.
Native OpenSpec, not this archive, generates agent commands/skills.

With the project's installed, compatible CLI:

```sh
openspec --version
openspec schema which ddd+arc42+user-doc
openspec schema validate ddd+arc42+user-doc
```

Use `templates/project-setup.md` with the actual goal, stack constraints and first
use case. It authorizes foundation Apply work only, not protected publication or
archive. `templates/project-architecture.md` is the concrete implementation-map
starter. A framework/language is not chosen by this bundle.

`templates/glossary.md` supplies a context-scoped index for concepts AND processes,
even without arc42. Reuse a suitable existing glossary; `openspec/glossary.md` is a
suggested new location, not an automatically installed second index. Conceptual
meanings stay in the domain model; process scope and behavior stay in their owning
feature/use-case specification. The arc42 glossary starter follows this same policy.
Follow the base template's grouped, alphabetically ordered layout. Use one file or
several linked units as useful; an entry point/global index references or is generated
from canonical entries rather than independently maintaining them. Review navigation,
ordering and definition access in the intended output, including after integration.
The bundle does not include a sorter/splitter or silently move existing project files.
Stage links to unpublished definitions until authorized integration.

`templates/documentation-policy.md` is the common policy. The optional Documentation
profile section in `project-architecture.md` references existing audiences, roots,
outputs, checks and exceptions rather than creating another configuration format.
Use actual project tooling/CI for enforcement; helper documentation states which
checks are and are not implemented. No tool or deployment is authorized by a policy.

To adopt starter changes in the modular source repository, merge
`project_templates/user-doc/manifest.json`, its landing/navigation sources and shared
guidance. Copying only a generated schema does not update an external starter builder.
Do not delete adopted pages merely because they were removed from the new manifest.

After a real change is created, check its effective instructions rather than assuming
that editing the project default changed existing change metadata:

```sh
openspec status --change CHANGE --json
openspec instructions design --change CHANGE --json
openspec instructions apply --change CHANGE --json
openspec instructions archive --change CHANGE --json
```

Check the installed CLI's support for `skip_specs`, operation guidance, and any
retirement/already-synced archive options actually used. No dummy spec files are an
acceptable workaround for incompatible CLI behavior.

## Regenerate and test this bundle

The reference composer uses Python 3.10+ and the standard library. It refuses to
replace an existing output directory; select a new disposable directory:

```sh
python3 tools/compose_schemas.py --output /tmp/ddd-schema-build
```

The tests additionally use PyYAML to parse rendered schema/configuration files:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

All Python helper implementations, including `closure.py`, are unchanged from
revision 2. Their guide clarifies how existing receipt fields cover supporting
sections inside a main spec. Helpers are independent of the application language
and are not an architecture or prose-quality analysis engine.

## Integration is a separate gate

The schema requires three outcomes before closure:

```text
Requirement deltas integrated
AND required model / language / architecture / ADR / contract companions explicitly published
AND glossary / supporting content / dependent references / translations / maps / catalog reconciled
```

Apply prepares change-local drafts, evidence and a pending `integration.json`.
Separately authorized integration reconciles the current baseline and performs the
actual publications. Finalize the reviewed receipt, then run the selected helper:

```sh
python3 openspec/schemas/ddd+arc42+user-doc/helpers/closure.py --root . inputs --change CHANGE
python3 openspec/schemas/ddd+arc42+user-doc/helpers/closure.py --root . check --change CHANGE
```

`inputs` prints change-relative fingerprints; it does not mark work complete.
Read [the helper guide](schemas/ddd/helpers/README.md) before creating the receipt.
The checker verifies declared states, snapshots, delta coverage, file/reference
existence, completed tasks and relevant metadata. It neither publishes nor proves
semantic correctness, actual test execution, link-anchor validity or authority.

`operations.archive.guidance` is advisory. A required project CI check or integration
wrapper must invoke the helper to make failure a hard gate. A bare native archive
command is not intercepted. Check after integration and before the final archive
move; do not force Apply to publish protected files to satisfy a premature gate.