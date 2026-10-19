# DDD helpers

These read-only, standard-library Python 3.10+ tools work without arc42 or mdBook.
Every composed v4 schema variant includes this optional `helpers/` directory;
install it with the selected schema under `openspec/schemas/openspec-ddd/`.
Existing helper APIs are unchanged; `closure.py` adds a read-only integration
receipt check. The original alternate `openspec/ddd/` location remains supported.

Without `--root`, installed helpers infer the project from the nearest ancestor
named `openspec`, regardless of schema name or directory depth, even when invoked
from outside the project. Otherwise they search the nearest current-directory
ancestor with an `openspec/` directory, `book-builder.toml`, or `book.toml`, then
helper ancestors with a book marker, finally the current directory. `--root` selects
an existing project directory explicitly. Catalog and decision arguments remain
project-relative. Keep `ddd.py`, `check.py`, `model.py`, `project_root.py`, and `closure.py`
together; no package install or additional dependencies are needed.

## Integration closure receipt

The revised profile uses one `integration.json` inside each change as closure
**evidence**, not another native planning artifact or an automatic publisher.
Prepare it during Apply with `pending` states. Finalize it only after separately
authorized integration and actual review. `tasks.md` references the authoritative
model/design/ADR mappings; do not write another editable publication plan here.

```sh
python3 openspec/schemas/openspec-ddd/helpers/closure.py --root . check --change CHANGE
python3 openspec/schemas/openspec-ddd/helpers/closure.py --root . inputs --change CHANGE
python3 openspec/schemas/openspec-ddd/helpers/closure.py --root . fingerprint PATH [PATH ...]
```

For an archived change, `--change` accepts its project-relative
`openspec/changes/archive/YYYY-MM-DD-CHANGE` path. Old archived receipts are historical
snapshots: later legitimate baseline changes can make revalidation stale. Gate the
change being closed, not every archive against today's baseline.

The receipt has these fields (see `templates/integration.json` for a pending starter):

| Field | Required content |
| --- | --- |
| `version`, `change` | Receipt format `1`; active change name without archive date. |
| `evidence` | Nonempty change-relative review/evidence file, normally `verification.md`. |
| `inputs` | `{path, sha256}` for **every** file in the change except the receipt itself. Paths here are change-relative. This includes `.openspec.yaml` if present, all artifacts, drafts and evidence. |
| `requirements` | `status`, `reason`, `files`. Every delta has `{source, target, sha256}`; source is change-relative and target is its exact `openspec/specs/.../spec.md`. The hash is of the final merged main spec, not the delta. Optional `action: retire` instead requires an absent main spec and `sha256: null`. |
| `companions` | `status`, `reason`, `files`. Each row has `{action, source, target, sha256}`; action is `publish`, `reuse` or `remove`. Publish requires a snapshotted change-local source; reuse/remove use `source: null`. Targets are project-relative. Remove requires an absent target and `sha256: null`; other actions hash the final maintained target. A rename is remove plus publish. |
| `reconciliation` | `status`, `reason`, `files`, `references`. Files are `{path, sha256}` for affected reviewed/updated maintained consumers, implementation maps, indexes or navigation. References are explicit project-relative durable file paths checked for existence; not Markdown URLs/anchors or code symbols. |

Each section uses `complete`, `not-needed` (empty scope with a reviewed reason), or
`pending`. The check rejects pending/failed states. With no deltas, requirements
must be `not-needed` with a reason; use the installed CLI's supported no-spec route
rather than making fake deltas. Inputs catch later edits/additions/removals; the
helper does not parse `.openspec.yaml` or prove native CLI readiness.

Publish means the authorized reviewed content was reconciled into the target.
It does **not** imply byte-for-byte copying of a whole draft over a newer baseline.
Final fingerprints are evidence of the reviewed result, not permission to overwrite it.

A configuration/API contract outside `spec.md` is a companion publication target.
Supporting sections inside a main `spec.md` are not separate companion files: map the
section edits in design, reconcile them after the requirement merge, and record the
final file under `reconciliation.files`. If that file also has a delta, its
`requirements.files` row must fingerprint the same final content. Never put a main
`spec.md` in `companions.files` or invent a requirement delta for supporting prose.
Review affected obsolete keys/meanings as well as links; historical examples may be
intentional. The existing receipt format needs no new fields for this distinction.

Main-spec retirement needs the installed CLI's supported retirement operation and
actual authorization. A receipt row with `action: retire` verifies absence, not that
the deletion was semantically justified. Relocation uses the reviewed retirement
and addition mappings; this helper does not implement a second spec merge engine.

### Language and glossary evidence

Use the same receipt format for language work. A separately maintained model or
language definition is a companion; definitions inside `spec.md` follow requirement
merge/supporting-section reconciliation above. A glossary's own file is a companion
when explicitly published from a draft, or a `reconciliation.files` index when reviewed
or updated in place. Choose its mapped action, not a new receipt section. Index-only
outside-tree edits follow existing Apply documentation rules; stage links requiring
unpublished definitions. Definitions retain model/spec protection at any location.

List the durable definition files under `reconciliation.references`; check their
actual Markdown links and section anchors with project tooling or review. The helper
does not parse glossary rows, validate anchors or compare domain/process meaning.
Use the baseline plus selected change proposals during Apply. At integration review
concurrent terminology changes, affected code/tests/current docs, scoped translations
and intentional historical/external aliases before taking final snapshots.

### What the check does

It verifies known receipt keys/states, full change-input and delta coverage, finished
Apply tasks, fresh hashes, existing publication/reuse targets, removed targets,
explicit durable-reference existence, and the existing catalog/ADR structural checks.
When a catalog exists, affected merged main specs must be registered; unrelated
legacy omissions remain reported rather than expanding this change.
Unsafe/escaping paths and stale snapshots fail with exit code 1. Outputs are JSON.
All paths use canonical relative forward-slash spelling. Fingerprints are lowercase
SHA-256. `inputs` prints the full change-relative input array for the receipt; it
does not mark any stage complete. `fingerprint` reports project-relative targets
for requirement, companion and reconciliation rows. Finalize evidence **before** taking snapshots.
Keep the checker output in CI logs or outside the change; appending it to snapshotted
evidence invalidates the receipt and requires fresh review/snapshots.

### What remains a reviewed project obligation

The helper does not execute recorded commands, prove tests passed, parse Markdown
links/anchors, check code symbols, establish authorization, or prove a semantic merge.
It cannot infer an omitted companion or undisclosed consumer from prose. Review the
receipt against impact/design/model/ADR mappings, including exact supporting sections
and configuration/API contracts; record that coverage review and
actual semantic/link/anchor/symbol checks in `verification.md`. Catalog omissions are
reported by the existing helper, never automatically registered; this closure check
also rejects omissions among this change's affected merged main specs. Use stack-specific
architecture tests for code conformance and documentation tooling for real link checks.
There are no arbitrary commands or automatic writes hidden in the receipt.

### Making it a gate

The schema's Apply instructions prepare the handoff; its config template adds archive
guidance; adopted agent instructions cover standalone sync. These are prompt-level
obligations, **not a native OpenSpec archive hook**. Use this explicit integration order:

1. With appropriate authorization, reconcile and sync requirement deltas.
2. Explicitly publish required protected companions and fix dependent references/maps/catalog.
3. Finish actual reviews, write fresh receipt snapshots, run the closure helper.
4. Only after success perform the final archive move using the installed CLI's supported
   already-synced/skip-sync path; do not blindly reapply non-idempotent deltas.

A project wrapper or required CI check must invoke the helper for hard enforcement.
A bare native archive command is not intercepted. The helper never authorizes sync,
publication, archive, shared-store writes or deployment. Do not force Apply to publish
protected content merely to make an all-stages CI job green; run closure after integration.

## Ownership graph

```sh
python3 openspec/schemas/openspec-ddd/helpers/ddd.py check
python3 openspec/schemas/openspec-ddd/helpers/ddd.py context owner.alias
python3 openspec/schemas/openspec-ddd/helpers/ddd.py impact owner.alias
```

The existing `ddd.py` requires a catalog. It validates its references and dependency
graph, lists prerequisite context, and reports consumers for review. Unlisted main
specs are reported, not automatically registered. It does not validate actual
architecture, behavioral conformance, or changes.

## Optional catalog and ADR metadata

```sh
python3 openspec/schemas/openspec-ddd/helpers/check.py --root .
python3 openspec/schemas/openspec-ddd/helpers/check.py --catalog openspec/catalog.json --decisions architectural-decisions
python3 openspec/schemas/openspec-ddd/helpers/check.py --status Proposed --status Accepted --status Superseded
```

`check.py` reuses the unchanged catalog validator when `openspec/catalog.json`
exists. `--catalog` explicitly requires the selected project-relative file.
No catalog is a valid, explicitly reported skip; it does not require dummy owners.

By default, individual records are discovered in existing scoped
`architectural-decisions/` directories beneath `openspec/specs/` and
`openspec/system-architecture/`, plus individual records referenced by the catalog.
Neither directory is required. Repeated `--decisions` selects project-relative ADR
files/directories instead of default directory discovery; catalog references remain
checked. Native change directories are not scanned by default. Explicit directories
can therefore select proposed records without treating them as maintained decisions.
Indexes, README files, assessments, and template examples are not individual records.

Individual records use only the bundle's canonical prose format (no legacy bold
metadata, em-dash headings, or alternative `decisions/` directory discovery):

```markdown
# ADR-SCOPE-001: Decision title

Status: Proposed
Date: Unknown
Scope: Shared system responsibility
```

The ID/title and one nonempty `Status`, `Date`, and `Scope` field are required.
Statuses remain project-defined unless repeated `--status` supplies an allowlist.
Dates may preserve unknown history; scopes are human-readable responsibility names,
not compulsory catalog aliases. Duplicate IDs within a directory/scope are rejected.
Actual local Markdown links under `Supersedes` and `Superseded by` must reference
existing project-local files. No lifecycle transitions, reciprocal relationships,
approval authority, or accepted dates are inferred.

## Shared ADR reading API

`model.py` is the canonical read-only ADR reader for validators and project-owned
renderers. It has no catalog copy or dependency; catalog and ownership-graph logic
remain in `ddd.py` and its existing `Catalog` API.

- `read_adr(path: Path, root: Path) -> AdrRecord` reads one record.
- `decisions(root: Path, *, decision_paths=(), references=()) -> list[AdrRecord]`
  uses the default scoped discovery above unless explicit paths are supplied;
  `references` adds individual record references.
- Frozen `AdrRecord` exposes project-relative `path`, exact original source `text`,
  `id`/`title`, and `status`/`date`/`scope` convenience values (`str` or `None`).
  `field_values(name)` returns a tuple of all values for that metadata field.

Recognition ignores comments, fenced code, and indented code without altering
`text`. Raw Markdown link targets in `Supersedes` and `Superseded by` are extracted,
not resolved or checked for existence by the parser. Incomplete fields remain as
`None` or tuples for diagnostics. Reading may report genuine Markdown syntax
errors or unreadable/unsafe file paths; it does not validate required fields,
status vocabulary, date format, scope ownership, uniqueness, or approval.

Validation is an explicit preflight, not an implicit parser operation:
`check.validate_decisions(root, records, *, statuses=())` checks required fields,
scoped duplicate IDs, local supersession-file existence, and an optional status
allowlist. It returns a JSON-compatible list of validated metadata dictionaries
with the existing CLI record shape, without original source text.

A custom project-owned renderer can read once and validate the same records before
using original Markdown (custom grouping and navigation remain project-specific):

```python
from pathlib import Path
import sys

root = Path("/path/to/project")
helpers = Path("/path/to/installed/schema/helpers")
sys.path.insert(0, str(helpers.resolve()))  # Import the installed helpers, not a root model.py.
from check import model, validate_decisions

records = model.decisions(root)
metadata = validate_decisions(root, records)  # Explicit preflight; failures stop rendering.
for record in records:
    print(record.path, record.id, record.title)
    # Pass record.text unchanged to the project's Markdown renderer.
```

Stricter rules such as globally unique IDs, `date.fromisoformat`, scope allowlists
or catalog lookups, complete catalog coverage, and spec-ID comments belong in
project checks, not bundle defaults. Rendering models introduce no second lifecycle.
Changing an adopted source format requires a project-owned migration; these helpers
never migrate or rewrite records.

Both checking CLI tools emit JSON and exit nonzero on structural errors. They never update
records, catalogs, architecture indexes, specs, or native change state. OpenSpec owns
spec/change validation (`openspec validate --all --strict --no-interactive`).
The optional shared documentation pack's `docs-check.py` can orchestrate these
checks through the generic `check_project(root, *, catalog=None, decision_paths=(),
statuses=())` API, with source/build/HTML checks for the selected documentation
components. It does not depend on arc42 being selected; these DDD helpers have no
builder dependency and work without any books.
Structural success is not decision approval, code conformance, or delivery acceptance.
