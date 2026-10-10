#!/usr/bin/env python3
"""Build fresh project templates from canonical manifests and composed v3 schemas."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "src/project_templates"
SCHEMA_SOURCES = ROOT / "src/schemas"
DEFAULT_OUTPUT = ROOT / "build/project_templates"
SCHEMA_DESTINATION = "openspec/schemas"
MARKER = ".starter-build.json"
GENERATOR = "openspec-ddd-starter-builder"
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def load_schema_builder():
    spec = importlib.util.spec_from_file_location(
        "openspec_ddd_schema_builder", ROOT / "scripts/schema-builder/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_builder = load_schema_builder()


def load_guidance():
    spec = importlib.util.spec_from_file_location(
        "openspec_ddd_starter_guidance", Path(__file__).with_name("guidance.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guidance = load_guidance()


def relative_path(value):
    """Require normalized, portable, nonempty project-relative paths."""
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or any(ord(char) < 32 for char in value)
            or value.startswith("/")
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError(f"Unsafe relative path: {value!r}")
    return PurePosixPath(value)


def no_symlinks(path):
    path = Path(os.path.abspath(path))
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Symlink not supported: {candidate}")
    return path


def source_path(root, relative):
    path = no_symlinks(Path(root) / relative_path(relative))
    if not path.is_file():
        raise ValueError(f"Missing source file: {path}")
    return path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def add_file(files, name, data, mode=0o644):
    relative_path(name)
    if name == MARKER or name.startswith(MARKER + "/"):
        raise ValueError(f"Reserved output path: {name}")
    if name == "AGENTS.md" or name.startswith("AGENTS.md/"):
        raise ValueError("Starter agent guidance belongs in AGENTS.proposal.md")
    if name in files or any(
            name.startswith(other + "/") or other.startswith(name + "/")
            for other in files):
        raise ValueError(f"Starter files conflict on output path: {name}")
    files[name] = (data, mode)


def copy_source(files, destination, root, source):
    path = source_path(root, source)
    add_file(files, destination, path.read_bytes(), stat.S_IMODE(path.stat().st_mode))


def render_books(books):
    # JSON basic strings/arrays are also TOML strings/arrays for validated values.
    return "".join(
        f"[books.{json.dumps(alias)}]\n"
        f"config = {json.dumps(book['config'])}\n"
        f"export-formats = {json.dumps(book['export-formats'])}\n"
        f"serve = {'true' if book['serve'] else 'false'}\n\n"
        for alias, book in books.items())


def load_manifest(sources, package, *, shared=False):
    if not isinstance(package, str) or not IDENTIFIER.fullmatch(package):
        raise ValueError(f"Invalid starter package: {package!r}")
    manifest = read_json(source_path(sources, f"{package}/manifest.json"))
    if (not isinstance(manifest, dict) or not {"files", "books"}.issubset(manifest)
            or set(manifest) - {"files", "books", "tooling", "guidance"}
            or not isinstance(manifest["files"], dict)
            or not isinstance(manifest["books"], dict)):
        raise ValueError(f"Invalid starter manifest: {package}")
    if "guidance" in manifest:
        if shared:
            raise ValueError(f"Shared starter package cannot declare guidance: {package}")
        if not isinstance(manifest["guidance"], dict):
            raise ValueError(f"Invalid manifest guidance: {package}")
    return manifest


def compose(components=(), sources=SOURCES, schema_sources=SCHEMA_SOURCES, root=ROOT):
    """Return output paths mapped to (bytes, permission mode), without writing."""
    sources, schema_sources, root = map(Path, (sources, schema_sources, root))
    no_symlinks(sources)
    no_symlinks(schema_sources)
    no_symlinks(root)
    components = list(components)
    schema = schema_builder.compose(components, schema_sources)
    schema_name = "+".join(["ddd", *components])
    files, books = {}, {}
    for name, content in schema.items():
        add_file(files, f"{SCHEMA_DESTINATION}/{schema_name}/{name}", content.encode("utf-8"))
    manifests = {package: load_manifest(sources, package)
                 for package in ["base", *components]}
    config = read_json(source_path(sources, "guidance.json"))
    context = guidance.plan(config,
                            (manifest.get("guidance") for manifest in manifests.values()))
    base_schema = None

    def read_guidance(source):
        nonlocal base_schema
        if source.startswith("base:"):
            name = source[len("base:"):]
            relative_path(name)
            if base_schema is None:
                base_schema = schema_builder.compose([], schema_sources)
            if name not in base_schema:
                raise ValueError(f"Unknown base schema guidance source: {source}")
            return base_schema[name]
        return source_path(root, source).read_text(encoding="utf-8")

    # Validate declared sources even for inactive groups; rendering still omits them.
    read_guidance(config["intro"])
    for group in config["groups"]:
        if "source" in group:
            read_guidance(group["source"])
    for manifest in manifests.values():
        if "guidance" in manifest:
            read_guidance(manifest["guidance"]["source"])
    for package in context["packages"]:
        if package in manifests:
            if "guidance" in manifests[package]:
                raise ValueError(f"Shared starter package cannot declare guidance: {package}")
        else:
            manifests[package] = load_manifest(sources, package, shared=True)
    for package, manifest in manifests.items():
        for destination, source in manifest["files"].items():
            if not isinstance(source, str):
                raise ValueError(f"Invalid file source: {package}/{destination}")
            if source.startswith("schema:"):
                name = source[len("schema:"):]
                relative_path(name)
                if name not in schema:
                    raise ValueError(f"Unknown composed schema source: {source}")
                # Project copies use the installed variant name; the schema library
                # itself remains byte-identical to the schema-only composition.
                content = schema[name].replace("openspec-ddd", schema_name)
                add_file(files, destination, content.encode("utf-8"))
            else:
                copy_source(files, destination, root, source)
                data, mode = files[destination]
                if b"{{schema-name}}" in data:
                    files[destination] = (data.replace(b"{{schema-name}}", schema_name.encode("utf-8")), mode)
        for alias, book in manifest["books"].items():
            if not IDENTIFIER.fullmatch(alias):
                raise ValueError(f"Invalid book alias: {alias!r}")
            if alias in books:
                raise ValueError(f"Book alias conflict: {alias}")
            if (not isinstance(book, dict)
                    or set(book) != {"config", "export-formats", "serve"}
                    or not isinstance(book["serve"], bool)
                    or not isinstance(book["export-formats"], list)
                    or not book["export-formats"]
                    or any(not isinstance(item, str) or item not in {"markdown", "typst", "pdf"}
                           for item in book["export-formats"])
                    or len(set(book["export-formats"])) != len(book["export-formats"])):
                raise ValueError(f"Invalid book definition: {alias}")
            relative_path(book["config"])
            books[alias] = book
        if "tooling" in manifest:
            tooling = manifest["tooling"]
            if (not isinstance(tooling, dict) or set(tooling) != {"source", "destination", "files"}
                    or not isinstance(tooling["files"], list) or not tooling["files"]):
                raise ValueError("Invalid documentation tooling definition")
            relative_path(tooling["source"])
            relative_path(tooling["destination"])
            for name in tooling["files"]:
                relative_path(name)
                copy_source(files, f"{tooling['destination']}/{name}", root,
                            f"{tooling['source']}/{name}")
    for alias, book in books.items():
        if book["config"] not in files:
            raise ValueError(f"Book config is not a declared starter file: {alias}")
    if books:
        add_file(files, "book-builder.toml", render_books(books).encode("utf-8"))
    add_file(files, "AGENTS.proposal.md",
             guidance.render(context, read_guidance, schema_name).encode("utf-8"))
    return dict(sorted(files.items()))


def read_tree(directory):
    """Read binary files and modes; reject links, special files, and extra directories."""
    directory = no_symlinks(directory)
    if not directory.is_dir():
        raise ValueError(f"Output directory required: {directory}")
    files, directories = {}, set()

    def visit(parent):
        for path in sorted(parent.iterdir()):
            if path.is_symlink():
                raise ValueError(f"Symlink not supported: {path}")
            name = path.relative_to(directory).as_posix()
            if path.is_dir():
                directories.add(name)
                visit(path)
            elif path.is_file():
                relative_path(name)
                files[name] = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
            else:
                raise ValueError(f"Unsupported output file: {path}")
    visit(directory)
    expected = {parent.as_posix() for name in files for parent in PurePosixPath(name).parents
                if parent != PurePosixPath(".")}
    if directories != expected:
        raise ValueError(f"Refusing unowned directories: {directory}")
    return files


def fingerprints(files):
    return {name: {"sha256": hashlib.sha256(data).hexdigest(), "mode": mode}
            for name, (data, mode) in sorted(files.items())}


def verify_owned(output):
    actual = read_tree(output)
    if MARKER not in actual:
        raise ValueError(f"Refusing unowned output: {output}")
    previous = read_json(output / MARKER)
    actual.pop(MARKER)
    if (not isinstance(previous, dict) or previous.get("generator") != GENERATOR
            or previous.get("files") != fingerprints(actual)):
        raise ValueError(f"Refusing modified or unowned output: {output}")


def write_files(output, files):
    output.mkdir(parents=True)
    for name, (data, mode) in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)


def publish(output, files, *, replace=False):
    """Stage the complete tree, validate ownership again, then rename with rollback."""
    validated = {}
    for name, (data, mode) in files.items():
        if (not isinstance(data, bytes) or not isinstance(mode, int)
                or isinstance(mode, bool) or not 0 <= mode <= 0o7777):
            raise ValueError(f"Invalid starter payload: {name}")
        add_file(validated, name, data, mode)
    files = validated
    output = no_symlinks(output)
    if output.exists():
        if not replace:
            raise ValueError(f"Output already exists; choose a new directory: {output}")
        verify_owned(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".starter-build-", dir=output.parent) as temporary:
        staging, backup = Path(temporary) / "starters", Path(temporary) / "previous"
        write_files(staging, files)
        # Fingerprint materialized modes: chmod/stat semantics differ on Windows.
        marker = {"generator": GENERATOR, "files": fingerprints(read_tree(staging))}
        (staging / MARKER).write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
        no_symlinks(output)
        if output.exists():
            if not replace:
                raise ValueError(f"Output already exists: {output}")
            verify_owned(output)
            output.rename(backup)
        try:
            staging.rename(output)
        except OSError:
            if backup.exists():
                backup.rename(output)
            raise


def build(output, components=(), sources=SOURCES, schema_sources=SCHEMA_SOURCES, root=ROOT):
    files = compose(components, sources, schema_sources, root)
    publish(output, files)
    return files


def build_all(output=DEFAULT_OUTPUT, sources=SOURCES, schema_sources=SCHEMA_SOURCES, root=ROOT):
    files, entries = {}, []
    for selected in schema_builder.combinations(Path(schema_sources)):
        name = "+".join(["ddd", *selected])
        starter = compose(selected, sources, schema_sources, root)
        for relative, (data, mode) in starter.items():
            add_file(files, f"{name}/{relative}", data, mode)
        entries.append({"variant": name, "kind": "composed", "components": selected,
                        "path": name, "schema": name})
    add_file(files, "index.json", (json.dumps(entries, indent=2) + "\n").encode("utf-8"))
    readme = ("# Generated project templates\n\nDo not edit generated output. Use one template "
              "for a fresh project, not as an installer or an upgrade overlay.\n\n"
              "| Variant | Components | Directory |\n| --- | --- | --- |\n" +
              "".join(f"| {entry['variant']} | {', '.join(entry['components']) or 'DDD base'} | "
                      f"`{entry['path']}` |\n" for entry in entries))
    add_file(files, "README.md", readme.encode("utf-8"))
    publish(output, files, replace=True)
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--base", action="store_true", help="Build DDD alone")
    selection.add_argument("--component", action="append", default=[],
                           help="Repeat in dependency order")
    parser.add_argument("--output", type=Path, help="New single-starter directory, or matrix output")
    args = parser.parse_args(argv)
    if (args.base or args.component) and args.output is None:
        parser.error("A single starter requires --output")
    try:
        if args.base or args.component:
            files = build(args.output, args.component)
            print(f"Built {len(files)} files in {args.output}")
        else:
            entries = build_all(args.output or DEFAULT_OUTPUT)
            print(f"Built {len(entries)} project templates in {args.output or DEFAULT_OUTPUT}")
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"Build failed: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
