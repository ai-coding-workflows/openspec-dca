# mdBook architecture addon

This optional addon publishes `openspec/system-architecture/` directly. Its
`README.md` is the editable handbook entry point, and `SUMMARY.md` is the mdBook
navigation. The OpenSpec DDD schema works without this addon.

From this repository's root, in a project that already has `openspec/`:

```sh
cp bundle/md-book/book.toml /path/to/project/
mkdir -p /path/to/project/openspec/system-architecture
cp bundle/md-book/openspec/system-architecture/SUMMARY.md /path/to/project/openspec/system-architecture/
```

If the project has no architecture entry point yet, copy the stub:

```sh
cp bundle/md-book/openspec/system-architecture/README.md /path/to/project/openspec/system-architecture/
```

Merge instead of overwriting any existing `book.toml`, `SUMMARY.md`, or
architecture files. With [mdBook installed](https://rust-lang.github.io/mdBook/guide/installation.html),
run `mdbook build` in the project root for static HTML in `build/book/`, or
`mdbook serve` for a live preview. Add `build/` to the project's `.gitignore`.

Edit the architecture pages in `openspec/system-architecture/` and list published
chapters in its `SUMMARY.md`. Keep detailed models, local views, and decisions with
their OpenSpec owners; include selected material from those sources when publication
needs it. Files outside the mdBook source directory are not automatically published
as linked pages. The [architecture chapter](../../docs/04-architecture-documentation.md)
explains the ownership model.
