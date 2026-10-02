#!/usr/bin/env python3
"""Compose repository-owned OpenSpec schema sources using only Python's stdlib."""

import argparse
import hashlib
import itertools
import tempfile
import json
import re
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "src/schemas"
DEFAULT_OUTPUT = ROOT / "build/schemas"
HOOK = re.compile(r"^([ ]*)\{\{hook:([a-z0-9]+(?:[.-][a-z0-9]+)*)\}\}[ ]*(?:\n|$)", re.MULTILINE)
MARKER = re.compile(r"\{\{/?(?:hook|slot)")
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def source_path(root, relative):
    """Resolve manifest paths without permitting access outside their package."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe source path: {relative}")
    result = (root / path).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError(f"Source escapes package: {relative}")
    if not result.is_file():
        raise ValueError(f"Missing source file: {relative}")
    return result


def read_files(directory):
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink not supported: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = path.read_text(encoding="utf-8")
    return result


def validate_manifest(manifest, name):
    if not isinstance(manifest, dict) or set(manifest) != {"description", "requires", "contributions"}:
        raise ValueError(f"Invalid manifest fields: {name}")
    if not isinstance(manifest["description"], str) or not manifest["description"].strip():
        raise ValueError(f"Invalid description: {name}")
    requires = manifest["requires"]
    if (not isinstance(requires, list)
            or any(not isinstance(item, str) or not IDENTIFIER.fullmatch(item) for item in requires)
            or len(requires) != len(set(requires))):
        raise ValueError(f"Invalid requires: {name}")
    contributions = manifest["contributions"]
    if not isinstance(contributions, dict) or any(
            not isinstance(key, str) or not isinstance(value, str) or not value
            for key, value in contributions.items()):
        raise ValueError(f"Invalid contributions: {name}")


def compose(components=(), sources=SOURCES):
    """Append component blocks in explicit order; preserve base text and native graph."""
    files = read_files(sources / "ddd/files")
    if "schema.yaml" not in files:
        raise ValueError("DDD base has no schema.yaml")
    hooks = set()
    for path, content in files.items():
        if MARKER.search(HOOK.sub("", content)):
            raise ValueError(f"Malformed or inline extension hook: {path}")
        hooks.update(match[2] for match in HOOK.finditer(content))

    contributions = {hook: [] for hook in hooks}
    selected = set()
    for name in components:
        if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
            raise ValueError(f"Invalid component name: {name}")
        if name in selected:
            raise ValueError(f"Component selected twice: {name}")
        package = sources / "components" / name
        if package.is_symlink():
            raise ValueError(f"Symlink not supported: {package}")
        if not (package / "component.json").is_file():
            raise ValueError(f"Unknown component: {name}")
        manifest = json.loads(source_path(package, "component.json").read_text(encoding="utf-8"))
        validate_manifest(manifest, name)
        for required in manifest["requires"]:
            if required not in selected:
                raise ValueError(f"{name} requires an earlier component: {required}")
        for hook, fragment in manifest["contributions"].items():
            if hook not in hooks:
                raise ValueError(f"Unknown extension hook: {hook}")
            content = source_path(package, fragment).read_text(encoding="utf-8")
            if MARKER.search(content):
                raise ValueError(f"Component fragments must be final text: {fragment}")
            # Authors supply whole blocks, independent of their YAML/Markdown embedding.
            content = textwrap.dedent(content).strip("\n")
            if not content.strip():
                raise ValueError(f"Empty contribution: {name}/{fragment}")
            contributions[hook].append(content)
        for path, content in read_files(package / "files").items():
            if path in files:
                raise ValueError(f"Components conflict on output file: {path}")
            if MARKER.search(content):
                raise ValueError(f"Component files must be final text: {path}")
            files[path] = content
        selected.add(name)

    # Detect file/directory collisions before build creates any output.
    for path in files:
        if any(parent.as_posix() in files for parent in Path(path).parents):
            raise ValueError(f"Components conflict on output file: {path}")

    def render(match):
        blocks = contributions[match[2]]
        if not blocks:
            return ""
        content = "\n\n".join(blocks)
        return "\n" + textwrap.indent(content, match[1]) + "\n\n"

    return {path: HOOK.sub(render, content) for path, content in sorted(files.items())}


def build(output, components=(), sources=SOURCES):
    """Build only into a new directory; never merge into installed/customized schemas."""
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists; choose a new directory: {output}")
    # Finish composition before creating output so configuration errors leave no files.
    files = compose(components, sources)
    write_files(output, files)
    return files


def combinations(sources=SOURCES):
    """Discover components, validate dependencies, and enumerate valid subsets."""
    manifests = {}
    for package in sorted((sources / "components").iterdir()):
        if not (package / "component.json").is_file():
            continue
        if package.is_symlink() or not IDENTIFIER.fullmatch(package.name):
            raise ValueError(f"Invalid component directory: {package}")
        manifest = json.loads((package / "component.json").read_text())
        validate_manifest(manifest, package.name)
        manifests[package.name] = manifest
    for name, manifest in manifests.items():
        for dependency in manifest["requires"]:
            if dependency not in manifests:
                raise ValueError(f"Unknown dependency: {name} requires {dependency}")
    ordered = []
    pending = set(manifests)
    while pending:
        ready = sorted(name for name in pending
                       if set(manifests[name]["requires"]).issubset(ordered))
        if not ready:
            raise ValueError("Component dependency cycle")
        ordered.extend(ready)
        pending.difference_update(ready)
    return [list(selected)
            for size in range(len(ordered) + 1)
            for selected in itertools.combinations(ordered, size)
            if all(set(manifests[name]["requires"]).issubset(selected) for name in selected)]


def write_files(output, files):
    output.mkdir(parents=True)
    for relative, content in files.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


def build_legacy(output, sources=SOURCES):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists; choose a new directory: {output}")
    files = read_files(sources / "legacy/openspec-ddd")
    if "schema.yaml" not in files:
        raise ValueError("Legacy schema has no schema.yaml")
    write_files(output, files)
    return files


def fingerprints(files):
    return {name: hashlib.sha256(content.encode("utf-8")).hexdigest()
            for name, content in files.items()}


def build_all(output=DEFAULT_OUTPUT, sources=SOURCES):
    """Stage the matrix; replace only a verified, builder-owned output tree."""
    output = Path(output)
    marker = ".schema-build.json"
    if output.is_symlink():
        raise ValueError("Refusing symlink output")
    if output.exists():
        if not (output / marker).is_file():
            raise ValueError(f"Refusing unowned output: {output}")
        previous = json.loads((output / marker).read_text())
        actual = read_files(output)
        actual.pop(marker)
        if not isinstance(previous, dict):
            raise ValueError(f"Invalid ownership manifest: {output}")
        expected_dirs = {parent for name in actual for parent in Path(name).parents if parent != Path(".")}
        actual_dirs = {path.relative_to(output) for path in output.rglob("*") if path.is_dir()}
        if actual_dirs != expected_dirs:
            raise ValueError(f"Refusing unowned directories: {output}")
        if previous.get("generator") != "openspec-ddd-schema-builder" or previous.get("files") != fingerprints(actual):
            raise ValueError(f"Refusing modified or unowned output: {output}")
    # Compose everything first: one bad variant must leave previous output intact.
    variants = []
    for selected in combinations(sources):
        name = "+".join(["ddd", *selected])
        variants.append((name, "composed", selected, compose(selected, sources)))
    legacy = read_files(sources / "legacy/openspec-ddd")
    if "schema.yaml" not in legacy:
        raise ValueError("Legacy schema has no schema.yaml")
    variants.append(("legacy", "legacy", [], legacy))
    entries = [{"variant": name, "kind": kind, "components": selected,
                "path": name}
               for name, kind, selected, files in variants]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".schema-build-", dir=output.parent) as temporary:
        staging = Path(temporary) / "schemas"
        staging.mkdir()
        for name, kind, selected, files in variants:
            write_files(staging / name, files)
        (staging / "index.json").write_text(json.dumps(entries, indent=2) + "\n")
        (staging / "README.md").write_text(
            "# Generated schemas\n\nDo not edit generated files. Install one listed directory as "
            "`openspec/schemas/openspec-ddd/`.\n\n"
            "| Variant | Components | Schema directory |\n| --- | --- | --- |\n" +
            "".join(f"| {e['variant']} | {', '.join(e['components']) or e['kind']} | "
                    f"`{e['path']}` |\n" for e in entries))
        (staging / marker).write_text(json.dumps({
            "generator": "openspec-ddd-schema-builder",
            "files": fingerprints(read_files(staging))}, indent=2) + "\n")
        backup = Path(temporary) / "previous"
        if output.exists():
            output.rename(backup)
        try:
            staging.rename(output)
        except OSError:
            if backup.exists():
                backup.rename(output)
            raise
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--component", action="append", default=[],
                           help="Build one selection; repeat in dependency order")
    selection.add_argument("--base", action="store_true", help="Build DDD without components")
    selection.add_argument("--legacy", action="store_true", help="Build the five-artifact legacy schema")
    parser.add_argument("--output", type=Path,
                        help="New directory for one schema; without a selection, matrix directory (default build/schemas)")
    args = parser.parse_args()
    try:
        if args.component or args.legacy or args.base:
            if args.output is None:
                parser.error("A single schema requires --output")
            files = build_legacy(args.output) if args.legacy else build(args.output, args.component)
            print(f"Built {len(files)} files in {args.output}")
        else:
            entries = build_all(args.output or DEFAULT_OUTPUT)
            print(f"Built {len(entries)} variants in {args.output or DEFAULT_OUTPUT}")
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"Build failed: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
