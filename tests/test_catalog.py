import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/helpers/ddd/ddd.py"
spec = importlib.util.spec_from_file_location("ddd", MODULE)
ddd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ddd)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(ROOT / "examples/equipment-lending", self.root,
                        ignore=shutil.ignore_patterns("build"))
        self.path = self.root / "openspec/catalog.json"
        self.data = json.loads(self.path.read_text())

    def load(self):
        self.path.write_text(json.dumps(self.data))
        return ddd.Catalog(self.root)

    def test_context_in_dependency_order_with_architecture(self):
        result = self.load().context(["lending.return"])
        self.assertEqual(result["owners"], ["lending.domain", "lending.loan-store", "lending.return"])
        self.assertTrue(any(x.endswith("architecture/runtime.md") for x in result["files"]))

    def test_transitive_consumers_are_distinct_from_scope(self):
        result = self.load().impact(["lending.domain"])
        self.assertEqual(result["changed_owners"], ["lending.domain"])
        self.assertEqual(set(result["consumers_to_review"]),
                         {"lending.loan-store", "lending.return", "lending.http", "lending.database"})

    def test_resolve_id_file_and_directory(self):
        catalog = self.load()
        path = self.data["specs"][2]["path"]
        for value in ("lending.return", path, str(Path(path).parent), str(self.root / path)):
            self.assertEqual(catalog.resolve(value), "lending.return")
        with self.assertRaisesRegex(ValueError, "Unknown catalog owner"):
            catalog.resolve("missing")

    def test_duplicate_ids_and_paths_are_rejected(self):
        self.data["specs"].append(dict(self.data["specs"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate owner id"):
            self.load()
        self.data["specs"][-1]["id"] = "another"
        with self.assertRaisesRegex(ValueError, "Duplicate owner path"):
            self.load()

    def test_unknown_dependency_and_cycle_are_rejected(self):
        self.data["specs"][0]["depends_on"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "Unknown dependency"):
            self.load()
        self.data["specs"][0]["depends_on"] = ["lending.return"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.load()

    def test_missing_and_escaping_references_are_rejected(self):
        self.data["specs"][0]["architecture"] = ["missing.md"]
        with self.assertRaisesRegex(ValueError, "Missing file"):
            self.load()
        self.data["specs"][0]["architecture"] = ["../outside.md"]
        with self.assertRaisesRegex(ValueError, "escapes project"):
            self.load()

    def test_symlink_cannot_escape_project(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside")
        (self.root / "linked.md").symlink_to(outside)
        self.data["specs"][0]["architecture"] = ["linked.md"]
        with self.assertRaisesRegex(ValueError, "escapes project"):
            self.load()

    def test_unlisted_specs_are_visible(self):
        self.data["specs"].pop()
        result = self.load().check()
        self.assertEqual(len(result["unlisted_main_specs"]), 1)
        self.assertIn("adapters/out/database/spec.md", result["unlisted_main_specs"][0])

    def test_invalid_catalog_types_are_rejected(self):
        for value in (None, [], {"schema_version": 1, "specs": {}},
                      {"schema_version": 1, "specs": ["bad"]}):
            self.data = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.load()

    def test_catalog_operations_are_read_only(self):
        catalog = self.load()
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        catalog.check()
        catalog.context(["lending.return"])
        catalog.impact(["lending.domain"])
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
