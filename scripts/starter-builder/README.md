# Fresh project template builder

Run from the repository root with Python 3.10+ (standard library only):

```sh
python3 build.py project_templates
python3 scripts/starter-builder/build.py
python3 scripts/starter-builder/build.py --base --output /tmp/new-ddd-project
python3 scripts/starter-builder/build.py --component arc42 --component user-doc --output /tmp/new-docs-project
```

The default builds the four v3 variants into `build/project_templates/<variant>`:
`ddd`, `ddd+arc42`, `ddd+user-doc`, and `ddd+arc42+user-doc`.
`--output` without a selection changes the matrix destination. Single selections
require `--output` pointing to a new directory. There is no legacy starter or
installer; these are fresh-project scaffolds, not overlays for existing projects.
Initialize OpenSpec's native agent integration separately with OpenSpec 1.13.1:

```sh
cd /path/to/copied-project
openspec init --tools pi --profile core --no-animation
openspec schema validate <variant>
```

Native initialization preserves the supplied `openspec/config.yaml`. Choose the
native integration for your agent instead of copying generated prompts. The root
`python3 build.py` default (`bundle`) builds schemas and project templates; `schemas` stays
schema-only, and `all` adds the handbook build and repository checks.

Every starter installs the composed schema under
`openspec/schemas/<variant>/`, matching the identifier in `build/schemas/`, and sets
`schema: <variant>` in `openspec/config.yaml`. For the combined documentation
starter, use `ddd+arc42+user-doc` in schema commands and
`openspec/schemas/ddd+arc42+user-doc/helpers/` for helper paths.
The builder imports `compose` and `combinations`
from `scripts/schema-builder/build.py` using `importlib`; it does not maintain a
second schema implementation. Installed schema bytes match the schema builder's
composition exactly, including the generic `openspec-ddd` name and references
inside reusable templates as installation defaults. Project guidance is rendered
for the chosen schema name. Schema output has the same default file modes (0644).

## Source contract

Canonical starter manifests live at:

- `src/project_templates/base/manifest.json`: always selected.
- `src/project_templates/arc42/manifest.json`: selected with arc42.
- `src/project_templates/user-doc/manifest.json`: selected with user-doc.
- `src/project_templates/documentation/manifest.json`: selected once when either or both
  documentation components activate that group or a descendant.

Each manifest requires `files` and `books` objects, including empty objects when
appropriate. Optional `guidance` associates a selected component with a group;
optional `tooling` declares an explicit reusable package. Unknown fields are errors.
Duplicate JSON keys are errors. A minimal illustrative manifest is:

```json
{
  "files": {
    "openspec/config.yaml": "schema:templates/config.yaml"
  },
  "books": {}
}
```

`files` maps output-relative paths to repository-relative canonical source files.
A `schema:` value instead addresses a file in the selected composition, allowing
project guidance/configuration to use the rendered schema sources. In these
project-file copies only, `openspec-ddd` is replaced with the selected variant.
Ordinary declared project source files may use `{{schema-name}}`, replaced with
that variant (as in the base README and arc42 book's optional helper command).
This narrow project-name rendering does not rewrite the installed schema library,
which remains byte-identical to the corresponding schema output.
Other than the installed schema and generated build metadata/book configuration/agent proposal,
all starter files must be explicitly declared in manifests. No source directory
is copied recursively. Ordinary source files may be text or binary; apart from
explicit `{{schema-name}}` placeholder rendering, bytes and permission modes are
preserved, including executable shell wrappers.

Each `books` entry maps a lowercase hyphenated alias to exactly these fields:

```json
{
  "files": {
    "book.user.toml": "src/project_templates/user-doc/book.user.toml"
  },
  "books": {
    "user": {
      "config": "book.user.toml",
      "export-formats": ["markdown", "typst", "pdf"],
      "serve": false
    }
  }
}
```

`config` must name a declared output file. `export-formats` is a nonempty list of
unique values from `markdown`, `typst`, and `pdf`; `serve` must be a JSON boolean.
The builder generates root `book-builder.toml` structurally from the merged books
when at least one book exists. Native book configurations remain canonical source
files, not generated or rewritten by this builder.

The documentation manifest may additionally declare an explicit maintained tool
payload:

```json
{
  "files": {},
  "books": {},
  "tooling": {
    "source": "scripts/md-book-builder",
    "destination": "scripts/md-book-builder",
    "files": ["book.py", "check.py"]
  }
}
```

That list is illustrative, not a complete payload. The canonical documentation
manifest must enumerate the full maintained tool payload, including required
resources and nested files. List paths are relative to `source` and `destination`;
only listed files are copied. Declare wrappers and other canonical files through
`files`. Caches, environments, and incidental files are never discovered/copied.

All file collisions fail, even for identical bytes, including collisions between
tooling, manifests, installed schema, and generated files. Book alias collisions
also fail. File/directory prefix conflicts are errors. Paths must be normalized
relative paths: absolute paths, traversal, empty/dot segments, backslashes,
colon-containing paths, and control characters are rejected. Source and output
symlinks (including ancestor symlinks) and special output files are rejected.

## Grouped agent-guidance proposal

Project templates generate **only `AGENTS.proposal.md`**, not an active `AGENTS.md`.
Review the proposal against the project's actual rules and deliberately merge
useful sections into the chosen agent instruction file. It is not a second active
policy or authorization to act. Native OpenSpec integration remains separate.

`src/project_templates/guidance.json` defines an intro source and an ordered group
list. Each group has a unique `id` and `title`, and may declare `parent`, `always`,
`source`, and `packages`. A component manifest may declare:

```json
{
  "files": {},
  "books": {},
  "guidance": {
    "group": "documentation",
    "title": "System architecture",
    "source": "src/schemas/components/arc42/fragments/project-agent-instructions.txt"
  }
}
```

Sources reference existing canonical fragments, not new copies of their policy.
The source prefix `base:` reads the unextended DDD composition, for example
`base:templates/agent-instructions.md`; it excludes selected component hooks so
those fragments are not included twice. Repository-relative sources provide
shared introductions or component fragments. Generated project guidance renders
schema-name references for the chosen variant; the installed schema remains unchanged.

The DDD group is always active. Selected component guidance activates its group
and every ancestor. Each active group's intro and shared packages occur once;
inactive groups disappear entirely. The documentation group currently owns the
shared intro and tooling package, while arc42 and user-doc supply their own leaves.
A future component can join that group or a subgroup; no arc42/user-doc-specific
selection branch is needed. Schema components still declare any needed helper
packs (for example, `helper-packs: ["docs"]`) in their schema manifest; group
membership does not silently add native schema dependencies or artifacts.
Shared packages contribute files/books/tooling, not
new guidance leaves that recursively change activation.

Group order follows the declaration list and component leaves follow selection
order; parents precede descendants. Heading levels reflect the group tree, with
source headings rebased and fenced code preserved. Duplicate IDs, unknown groups
or parents, cycles, malformed metadata, unsafe source paths, output collisions,
and excessive Markdown heading depth fail before replacing output. Composition
markers are consumed during generation, not left as empty placeholder sections.
This is a grouped block composer, not a general conditional template language.

## Safe regeneration

The matrix includes `index.json`, `README.md`, and `.starter-build.json`. Single
starter builds also include the ownership marker. It fingerprints every generated
file by SHA-256 and permission mode. Output is fully composed and staged beside
the destination before publication. Matrix regeneration replaces only a verified
builder-owned tree; it refuses changed/missing/extra files, changed file modes,
symlinks, and extra empty directories. Unowned directories are never merged or
removed. Replacement uses same-filesystem directory renames with rollback if
publication fails; this is not a locking protocol for concurrent writers.

Do not edit generated output or manually adjust its ownership marker. Change
canonical sources and regenerate. For intentional project customizations, copy a
starter to a separate project and maintain it there; this builder is not an
updater for that copy. Single-starter destinations must always be new, even when
an existing destination has a valid marker.

For isolated tests, `compose`, `build`, and `build_all` accept optional `sources`
(starter manifest root), `schema_sources` (schema source root), and `root`
(repository root for canonical file references). `build_all` also accepts an
alternate output directory; `main(argv)` supports explicit CLI arguments.
