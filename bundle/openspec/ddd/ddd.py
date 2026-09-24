#!/usr/bin/env python3
"""Read-only contract inventory, prerequisite context, and consumer impact for OpenSpec."""
import argparse
import json
import sys
from pathlib import Path


class Catalog:
    def __init__(self, root, catalog="openspec/catalog.json"):
        self.root = Path(root).resolve()
        data = json.loads(self.file(catalog).read_text())
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Catalog must have schema_version: 1")
        if not isinstance(data.get("specs"), list):
            raise ValueError("Catalog specs must be an array")
        self.entries = {}
        self.paths = {}
        for row in data["specs"]:
            if not isinstance(row, dict):
                raise ValueError("Every catalog entry must be an object")
            spec_id = row.get("id")
            if not isinstance(spec_id, str) or not spec_id.strip():
                raise ValueError("Every owner needs a nonempty id")
            if spec_id in self.entries:
                raise ValueError(f"Duplicate owner id: {spec_id}")
            path = self.file(row.get("path"))
            if path.name != "spec.md" or not path.is_relative_to(self.root / "openspec/specs"):
                raise ValueError(f"Owner {spec_id} must reference openspec/specs/**/spec.md")
            if path in self.paths:
                raise ValueError(f"Duplicate owner path: {row['path']}")
            deps = row.get("depends_on", [])
            if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
                raise ValueError(f"Invalid depends_on for {spec_id}")
            if len(set(deps)) != len(deps):
                raise ValueError(f"Duplicate dependency for {spec_id}")
            for field in ("contracts", "architecture", "decisions"):
                values = row.get(field, [])
                if not isinstance(values, list):
                    raise ValueError(f"{field} must be an array for {spec_id}")
                for value in values:
                    self.file(value)
            self.entries[spec_id] = dict(row, depends_on=deps)
            self.paths[path] = spec_id
        for spec_id, row in self.entries.items():
            for dep in row["depends_on"]:
                if dep not in self.entries:
                    raise ValueError(f"Unknown dependency {dep} for {spec_id}")
        self.ordered = self.order(self.entries)

    def file(self, name):
        if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
            raise ValueError(f"Catalog paths must be nonempty project-relative paths: {name!r}")
        path = (self.root / name).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"Path escapes project: {name}")
        if not path.is_file():
            raise ValueError(f"Missing file: {name}")
        return path

    def resolve(self, value):
        if value in self.entries:
            return value
        path = (self.root / value).resolve()
        if path.is_dir():
            path = (path / "spec.md").resolve()
        if path in self.paths:
            return self.paths[path]
        raise ValueError(f"Unknown catalog owner or spec path: {value}")

    def order(self, ids):
        result, visiting, visited = [], set(), set()

        def visit(spec_id):
            if spec_id in visiting:
                raise ValueError(f"Contract dependency cycle at {spec_id}")
            if spec_id in visited:
                return
            visiting.add(spec_id)
            for dep in self.entries[spec_id]["depends_on"]:
                visit(dep)
            visiting.remove(spec_id)
            visited.add(spec_id)
            result.append(spec_id)

        for spec_id in ids:
            visit(spec_id)
        return result

    def context(self, ids):
        ordered = self.order(ids)
        files = []
        for spec_id in ordered:
            row = self.entries[spec_id]
            for field in ("path", "contracts", "architecture", "decisions"):
                values = [row[field]] if field == "path" else row.get(field, [])
                for value in values:
                    if value not in files:
                        files.append(value)
        return {"owners": ordered, "files": files}

    def impact(self, ids):
        found = set(ids)
        while True:
            consumers = {key for key, row in self.entries.items()
                         if found.intersection(row["depends_on"])}
            if consumers.issubset(found):
                break
            found |= consumers
        return {
            "changed_owners": list(dict.fromkeys(ids)),
            "consumers_to_review": [key for key in self.ordered if key in found and key not in ids],
            "note": "Review set, not automatic edit scope. Check external consumers and composition too.",
        }

    def check(self):
        unlisted = sorted(str(path.relative_to(self.root))
                          for path in (self.root / "openspec/specs").rglob("spec.md")
                          if path.resolve() not in self.paths)
        return {"owners": len(self.entries), "unlisted_main_specs": unlisted,
                "note": "Structural check only; dependency completeness and conformance need review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root (default: current directory)")
    parser.add_argument("--catalog", default="openspec/catalog.json", help="Project-relative catalog path")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    for name in ("context", "impact"):
        commands.add_parser(name).add_argument("owners", nargs="+", help="Catalog IDs or main spec paths")
    args = parser.parse_args()
    try:
        catalog = Catalog(args.root, args.catalog)
        if args.command == "check":
            result = catalog.check()
        else:
            ids = [catalog.resolve(value) for value in args.owners]
            result = getattr(catalog, args.command)(ids)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, RecursionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
