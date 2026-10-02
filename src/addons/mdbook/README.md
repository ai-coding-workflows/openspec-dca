# mdBook architecture addon

This optional addon publishes `openspec/system-architecture/` directly. Its
`README.md` is the editable handbook entry point, and `SUMMARY.md` is the mdBook
navigation. The template includes Mermaid browser assets under `theme/` and
configures the `mdbook-mermaid` preprocessor. The OpenSpec DDD schema works
without this addon.

From this repository's root, in a project that already has `openspec/`:

```sh
cp src/addons/mdbook/book.toml /path/to/project/
mkdir -p /path/to/project/theme
cp src/addons/mdbook/theme/mermaid.min.js /path/to/project/theme/
cp src/addons/mdbook/theme/mermaid-init.js /path/to/project/theme/
mkdir -p /path/to/project/openspec/system-architecture
cp src/addons/mdbook/openspec/system-architecture/SUMMARY.md /path/to/project/openspec/system-architecture/
```

If the project has no architecture entry point yet, copy the stub:

```sh
cp src/addons/mdbook/openspec/system-architecture/README.md /path/to/project/openspec/system-architecture/
```

Merge instead of overwriting any existing `book.toml`, `SUMMARY.md`, or
architecture or theme files. Install mdBook and `mdbook-mermaid` on PATH (the
repository tests use mdBook 0.5.4 and mdbook-mermaid 0.17.1), then
run `mdbook build` in the project root for static HTML in `build/book/`, or
`mdbook serve` for a live preview. Add `build/` to the project's `.gitignore`.

Edit the architecture pages in `openspec/system-architecture/` and list published
chapters in its `SUMMARY.md`. Keep detailed models, local views, and decisions with
their OpenSpec owners; include selected material from those sources when publication
needs it. Files outside the mdBook source directory are not automatically published
as linked pages. The [architecture chapter](../../../docs/04-architecture-documentation.md)
explains the ownership model.

Use ordinary Mermaid fences in architecture pages:

````markdown
```mermaid
flowchart LR
    Client --> Service
```
````

`mdbook build` preprocesses the diagram and includes both local JavaScript files in
its HTML output. Distribute the entire `build/book/` directory, including those
assets. No CDN or separate `mdbook-mermaid install` step is needed for this template.
The repository handbook references these same source assets; update them here when
upgrading the Mermaid integration and retain their license notices.

The addon integration test copies the template into a temporary project, adds a
Mermaid diagram, runs the real mdBook build, and checks the processed diagram and
packaged script references. Run it with `mdbook` and `mdbook-mermaid` on PATH:

```sh
python3 -m unittest discover -s tests -p test_mdbook_addon.py -v
```
