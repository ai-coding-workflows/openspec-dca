#!/usr/bin/env python3
"""Compose repository-owned OpenSpec schema sources using only Python's stdlib."""

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path


SOURCES = Path(__file__).resolve().parents[1] / "bundle/openspec/schema-builder"
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
    output.mkdir(parents=True)
    for relative, content in files.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", action="append", default=[],
                        help="Optional component; repeat in dependency order (arc42, user-docs, architecture-reconstruction)")
    parser.add_argument("--output", required=True, type=Path,
                        help="New schema directory, including its installation name openspec-ddd")
    args = parser.parse_args()
    try:
        files = build(args.output, args.component)
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"Build failed: {error}\n")
    print(f"Built DDD{' + ' + ' + '.join(args.component) if args.component else ''}: "
          f"{len(files)} files in {args.output}")


if __name__ == "__main__":
    sys.exit(main())
