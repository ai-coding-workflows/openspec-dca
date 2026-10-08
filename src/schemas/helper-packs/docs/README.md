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
