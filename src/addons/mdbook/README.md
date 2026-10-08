# mdBook architecture addon

This optional addon publishes `openspec/system-architecture/` directly. Its
`README.md` is the editable handbook entry point, and `SUMMARY.md` is the mdBook
navigation. The template configures the `mdbook-mermaid` preprocessor but does
not vendor browser JavaScript. The reusable builder provisions those assets; raw
mdBook users need explicit setup. The OpenSpec DDD schema works without this addon.

From this repository's root, in a project that already has `openspec/`:

```sh
cp src/addons/mdbook/book.toml /path/to/project/
mkdir -p /path/to/project/openspec/system-architecture
cp src/addons/mdbook/openspec/system-architecture/SUMMARY.md /path/to/project/openspec/system-architecture/
```

If the project has no architecture entry point yet, copy the stub:

```sh
cp src/addons/mdbook/openspec/system-architecture/README.md /path/to/project/openspec/system-architecture/
```

Merge instead of overwriting any existing `book.toml`, `SUMMARY.md`, architecture,
or theme files. Add `build/` to the project's `.gitignore`.

### Reusable builder (managed setup)

Copy the reusable `scripts/md-book-builder/` bundle anywhere inside the project,
keeping its resources together, then build or preview:

```sh
python3 /path/to/project/tools/documentation/md-book-builder/book.py --root /path/to/project build
python3 /path/to/project/tools/documentation/md-book-builder/book.py --root /path/to/project serve
```

The builder autodetects the native Mermaid table. Optional per-book `mermaid = true`
in `book-builder.toml` also provisions a missing standard preprocessor; `false`
disables managed setup without deleting existing author configuration. The same
options apply to svgbob. Custom commands remain author-managed and are not replaced
or shadowed by provisioned standard binaries.

Managed Mermaid setup permanently updates native configuration with relative
`additional-js` references. Assets come from the chosen executable's `install`
command only in a scratch mini-book, then are hash-checked under
`<builder>/.cache/scripts/mermaid/<identity>/`. Docker uses its actual pinned image
binary, not the host binary. Owned references refresh per binary identity; missing
standard-filename references can be repaired. Valid author assets, custom commands,
and comments stay intact; unsupported impacted inline/dotted TOML forms error before
writes. Maintained Markdown is untouched. See the
[builder guide](../../../scripts/book.md) for relocation, toolchain, and staged paths.

### Raw mdBook (manual setup)

Install mdBook and `mdbook-mermaid` on PATH (the repository tests use mdBook 0.5.4
and mdbook-mermaid 0.17.1). Intentionally install browser assets/configuration into
the project before using raw mdBook:

```sh
mdbook-mermaid install /path/to/project
cd /path/to/project
mdbook build
# Or: mdbook serve
```

This manual command can modify project configuration and add source assets; review
its changes. The copied addon alone is not a self-contained raw-native Mermaid site.

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

After managed or manual setup, mdBook preprocesses the diagram and includes local
JavaScript in its HTML output. Distribute the entire `build/book/` directory,
including those assets. The repository handbook uses generated builder-owned cache
assets too, not JavaScript sources from this addon.

The addon integration test copies the template and managed builder into a temporary
project, adds a Mermaid diagram, runs the real managed build, and checks the
processed diagram and packaged assets. It verifies managed provisioning, not that
the unprepared template works with raw `mdbook build`. Run it with `mdbook` and `mdbook-mermaid` on PATH:

```sh
python3 -m unittest discover -s tests -p test_mdbook_addon.py -v
```
