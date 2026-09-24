# Install and use the OpenSpec DDD bundle

This bundle targets ordinary repository-local OpenSpec projects. It is independent
of application language and framework. OpenSpec stores and worksets are outside this
guide's tested scope; the optional helper resolves files relative to one project root.

## Install the native integration

Install the tested OpenSpec release with Node.js 20.19.0 or newer, then initialize
your application project:

```sh
npm install --global @fission-ai/openspec@1.13.1
cd /path/to/project
openspec init --tools pi --profile core
```

For another agent, choose its native integration. OpenSpec generates Pi commands
under `.pi/prompts/opsx-*.md` and skills under `.pi/skills/openspec-*/`. The core
profile includes explore, propose, update, apply, sync, and archive. Follow the
setup output and reload your agent session if needed.

This guide uses Pi's spelling, such as `/opsx-propose`. Upstream documentation often
uses `/opsx:propose`. Always use the spelling printed for your chosen integration.
Do not copy the Pi prompt files to another agent and assume registration works.
See [upstream supported tools](https://openspec.dev/docs/supported-tools).

For optional `new`, `continue`, `ff`, and `verify` workflows, run
`openspec config profile`, select the desired workflows, then `openspec update`.
The profile preference is global to OpenSpec; it is separate from the project-local
DDD schema. Core commands are sufficient for the default workflow in this guide.

## Add the DDD schema

For a first installation, copy the schema into the initialized project. Run these
commands from this guide's root, replacing the target path:

```sh
mkdir -p /path/to/project/openspec/schemas
cp -R bundle/openspec/schemas/openspec-ddd /path/to/project/openspec/schemas/
```

Review and merge `templates/config.yaml` into the existing `openspec/config.yaml`.
At minimum set `schema: openspec-ddd`. Keep existing context, rules, operation
guidance, and agent settings. Add the relevant project checks and architecture
entry points. Merge `templates/agent-instructions.md` into the project's agent
instructions so the ownership rules also apply to ordinary review/refinement requests.

From the application root, verify the installation:

```sh
openspec schema which openspec-ddd
openspec schema validate openspec-ddd
openspec templates --schema openspec-ddd
```

The schema defines `proposal → impact → specs → design → tasks`. Apply tracks
`tasks.md` and requires all five planning artifacts. OpenSpec decides readiness from
artifact existence. The prose instructions require meaningful content and review;
they are not enforced semantic gates.

For updates, diff the installed schema against this bundle and merge changes with
local customizations. Do not blindly repeat a directory copy over a customized
installation. `openspec update` refreshes native agent integrations, not this schema.

## Optional catalog and helper

Copy the helper and start a catalog only when the ownership graph is useful:

```sh
cp -R bundle/openspec/ddd /path/to/project/openspec/
```

Use `templates/catalog.json` as the starting shape for `openspec/catalog.json`, or
adapt the example catalog. Do not replace an existing catalog with the empty template.
An entry has a stable alias, a main spec path, and consumed owner IDs:

```json
{
  "id": "lending.return",
  "kind": "feature",
  "path": "openspec/specs/contexts/lending/features/return-equipment/spec.md",
  "depends_on": ["lending.domain", "lending.loan-store"],
  "architecture": ["openspec/specs/contexts/lending/features/return-equipment/architecture/runtime.md"]
}
```

All referenced owners must exist in the catalog. Paths are project-relative existing
files. Optional `contracts`, `architecture`, and `decisions` arrays identify additional
context explicitly. A `domain/model.md` companion remains documentation owned by its
main spec owner; it does not create another capability or catalog node, and native spec
sync does not update it. New proposed owners remain in `impact.md` until main specs exist.

From the application root:

```sh
python3 openspec/ddd/ddd.py check
python3 openspec/ddd/ddd.py context lending.return
python3 openspec/ddd/ddd.py impact lending.domain
```

All three commands are read-only and return JSON. Python 3.10+ is sufficient, without
extra packages. Use `--root /path/to/project` before the subcommand when running from
elsewhere. `context` lists prerequisites first and includes explicit architecture/ADR
references. `impact` lists transitive consumers for review, not an edit instruction.

`check` rejects invalid references, duplicate IDs/paths, and dependency cycles, and
reports main specs missing from the catalog. It does not validate actual architecture,
discover external callers, or evaluate proposed deltas. OpenSpec handles change and
spec validation; the helper supplies only the additional DDD graph.

The helper does not implement the optional requirement-to-test traceability convention
described in the [workflow guide](05-change-workflow.md). That manifest is project-owned
and does not change `depends_on`, catalog validation, or OpenSpec acceptance behavior.

## Pass a spec or a change

For a new effort, give the agent the outcome plus a catalog alias or main spec path:

```text
/opsx-propose record-return-condition: Start from lending.return.
Record the condition of each new return.
```

The same request can use the exact file path:

```text
/opsx-propose record-return-condition: Start from
openspec/specs/contexts/lending/features/return-equipment/spec.md.
Record the condition of each new return.
```

The agent resolves this free text using the catalog and actual specs. Naming the
starting owner is enough; the impact review discovers necessary related work.
You can name several owners if you already know them. An agent's file mention is
also suitable when it makes the actual file available.

Once the change exists, pass its **change name** to follow-up commands:

```text
/opsx-update record-return-condition: Reconcile the compatibility decision.
/opsx-apply record-return-condition
```

Native terminal commands use different arguments:

```sh
# OpenSpec capability path, not the DDD alias or full spec.md path:
openspec show contexts/lending/features/return-equipment --type spec

# Change name, not its directory or a spec ID:
openspec status --change record-return-condition

# The optional DDD helper resolves both aliases and main spec paths:
python3 openspec/ddd/ddd.py context openspec/specs/contexts/lending/features/return-equipment/spec.md
```

There is no additional saved DDD selection. Use explicit change names when several
efforts are active. Archived changes are history; later work starts a new change.

## Find open steps and tasks

Use native commands from the application root:

```sh
openspec list
openspec status --all
openspec status --change record-return-condition --json
openspec instructions apply --change record-return-condition --json
```

`list` shows active changes and task progress. `status --all` shows their artifact
readiness. Per-change apply instructions report `state`, `progress`, individual
`tasks` with a `done` flag, and missing required artifacts. This command only prints
instructions; it does not execute implementation work. JSON is available for an
agent or another reporting tool to aggregate all active changes.

The teaching example has `isPlanningComplete: true` but seven pending tasks. Missing
artifacts, absent/empty tasks, or unfinished tasks require different next actions.
Even `state: all_done` means tracked tasks are checked, not that acceptance is proven.
Native status does not infer stale designs, unresolved prose questions, unrecorded
review findings, missing delta coverage, or test failures. Ask for a consistency
review and inspect `verification.md` for those concerns.

## Validation and closure

```sh
openspec validate --all --strict --no-interactive
```

Run this structural check alongside the adopting project's actual tests and
documentation checks. A docs-only or refactoring change with no behavioral change
sets `skip_specs: true` in its `.openspec.yaml`; the specs artifact is skipped while
impact, design, tasks, and verification still describe the actual work. Never use
this flag to hide a genuine behavior change or leave delta files beside it.

Main specs receive requirement deltas during native sync/archive. Architecture,
ADRs, catalog changes, and non-spec documents remain explicit tasks. Catalog
registration of a newly created owner must be included in the closure review.

The guide's integration tests check the supported CLI version, nested spec discovery
and merge, native Pi generation, artifact readiness, the no-spec route, and the
difference between planning completion and remaining tasks. They do not invoke a
language model or certify the quality of its generated artifacts.
