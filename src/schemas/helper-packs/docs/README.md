# Documentation checks

This optional entry point accompanies either documentation component. Both together
include it once. It orchestrates checks; source/include/HTML validation and book
building remain in the separately installed, reusable md-book-builder. No arc42
layout or mandatory book is imposed.

From the project root, after installing the composed schema and builder:

```sh
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py
python3 openspec/schemas/openspec-ddd/helpers/docs-check.py --builder tools/documentation/md-book-builder/book.py --source-only --source notes
```

`BOOK_BUILDER` can select the builder instead. The conventional
`scripts/md-book-builder/book.py` location is also discovered. Use `--root` to
select another project; installed helpers otherwise infer the enclosing project
above `openspec/`, independently of the schema's name or nesting.

Optional DDD metadata checks use the adjacent `check.py`; missing metadata is
reported as skipped. A standalone launcher can use `--ddd-helper` to explicitly
select among several installed schemas. `--skip-ddd` explicitly excludes metadata
checks. The DDD helpers also work independently without the builder.

Sources are checked first, selected books are built once with Markdown export,
and local HTML links/anchors are checked afterward. `--source-only` skips rendering;
`--openspec` adds native validation. A successful check establishes neither arc42
conformance nor code correctness, decision approval, or delivery acceptance.

## Project-specific quality gates

The base `templates/documentation-policy.md` defines three check classes. Reuse the
project's documentation profile/check commands rather than invent a new universal
configuration format. The wrapper above performs only its documented checks; it
does not parse glossary ordering, detect leaked placeholders, count page size,
validate navigation reachability exhaustively or assess audience/coherence.

Adopt explicit supported tools/review methods for additional checks. Scope published
content separately from template libraries, drafts, includes and history. Record:

| Class | Project choice | Evidence |
| --- | --- | --- |
| Deterministic gate | Rule, tool/command, source/output scope, allowed exceptions | Actual failure/pass/skip; a violated required gate blocks completion |
| Review signal | Content-specific size/growth/table/entry threshold or duplication signal | Split/consolidate or justified retention; no default hard quota |
| Content/procedure review | Readers, relevant risk, safe environment, selected examples | Inspection vs executed procedure, outcome and limits |

Measure editable units and rendered outputs appropriately; distinguish prose, code
and tables. A unified export is not itself a giant-source violation. Link checks
must account for the intended publication format, not only repository paths. Check
glossary leaves and entry-point navigation after splitting without duplicating entries.
Keep review decisions in existing verification; no mandatory second report/inventory.
Use actual CI/wrappers to enforce adopted gates. The schema does not install a gate,
automatically execute documentation examples, or grant deployment authorization.
