# Optional DDD helpers

These read-only, standard-library Python 3.10+ tools work without arc42 or mdBook.
Every composed v3 schema variant includes this optional `helpers/` directory;
install it with the selected schema under `openspec/schemas/openspec-ddd/`.
The retained legacy schema is unchanged. Independently copying this whole directory
to `openspec/ddd/` remains supported, but is not the main distribution.

Without `--root`, installed helpers infer the project from the nearest ancestor
named `openspec`, regardless of schema name or directory depth, even when invoked
from outside the project. Otherwise they search the nearest current-directory
ancestor with an `openspec/` directory, `book-builder.toml`, or `book.toml`, then
helper ancestors with a book marker, finally the current directory. `--root` selects
an existing project directory explicitly. Catalog and decision arguments remain
project-relative. Keep `ddd.py`, `check.py`, `model.py`, and `project_root.py`
together; no package install or additional dependencies are needed.

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

## Optional mdBook ADR view

Every composed schema also distributes `adr-preprocessor.py`. It is inactive until
you explicitly add the following to the selected native `book.toml`, substituting
the installed schema directory and Python executable as needed:

```toml
[preprocessor.adr]
command = "python3 openspec/schemas/openspec-ddd/helpers/adr-preprocessor.py"
```

In one book chapter registered in `SUMMARY.md`, add this visible marker exactly
once, outside code examples and HTML comments:

```markdown
# ADR view

{{#adr-index}}
```

Use a dedicated book-view chapter, not a replacement for the maintained architecture
index. The preprocessor reads canonical maintained ADRs using the model's default
scoped discovery, then explicitly runs generic ADR validation. No catalog is required;
this view does not add catalog-only selections or scan changes and archives.

It replaces the marker with a title/status/scope index and adds virtual decision
pages and directory-based navigation beneath the chapter. Grouping follows the
project-relative source directory, not catalog ownership or a project's label map.
Generated page paths start with `adr/` beside the marker chapter; no generated
Markdown is written to the source tree. Existing chapter children are retained.
An empty selection produces an empty-state message. Without the marker the book
passes through unchanged, without an ADR scan.

Explicit ADR anchors derive deterministically from the ID. The same ID may occur
on different pages; collisions within one generated page, duplicate markers, and
collisions with existing chapter paths are errors. An anchor remains stable while
the ID remains unchanged; the full URL also depends on the source directory and
marker chapter location. Stable anchors identify ADRs, not every internal section:
merged section headings still use the renderer's ordinary heading anchors.

Rendered ADR headings and local Markdown links are adjusted for the generated
page while original files and `AdrRecord.text` stay unchanged. Links between
selected ADRs target the generated pages. Other local links/images must point to
existing files within the book source tree; unsupported outside-book resources
fail rather than being silently copied or rendered as broken links. Keep code
examples fenced. Raw HTML resource links and mdBook include directives are not a
substitute for supported Markdown links in this view.

The preprocessor supports native `html` and `book-export` renderers, including the
builder's native-preprocessed exports. It does not generate records, infer approval,
change statuses, or replace the durable architecture index. The generic builder
contains no ADR-generation logic. Custom renderers and stricter project checks
remain possible through the shared reading API above.

Both checking CLI tools emit JSON and exit nonzero on structural errors. They never update
records, catalogs, architecture indexes, specs, or native change state. OpenSpec owns
spec/change validation (`openspec validate --all --strict --no-interactive`).
The optional shared documentation pack's `docs-check.py` can orchestrate these
checks through the generic `check_project(root, *, catalog=None, decision_paths=(),
statuses=())` API, with source/build/HTML checks for the selected documentation
components. It does not depend on arc42 being selected; these DDD helpers have no
builder dependency and work without any books.
Structural success is not decision approval, code conformance, or delivery acceptance.
