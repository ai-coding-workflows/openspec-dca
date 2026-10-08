"""Root discovery for canonical and standalone schema helpers."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT / "src/schemas/ddd/helpers"


class SchemaHelperRootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.cwd = self.base / "outside"
        self.cwd.mkdir()
        spec = importlib.util.spec_from_file_location("helper_project_root", HELPERS / "project_root.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.resolve = module.resolve_project_root

    def test_explicit_root_must_be_existing_directory(self):
        self.assertEqual(self.resolve(self.cwd, cwd=self.base), self.cwd)
        for path in (self.base / "missing", HELPERS / "ddd.py"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "project directory"):
                self.resolve(path, cwd=self.cwd)
        self.assertEqual(self.resolve("outside", cwd=self.base), self.cwd)

    def test_installed_root_precedes_cwd_and_has_no_fixed_depth(self):
        (self.cwd / "book.toml").touch()
        project = self.base / "application"
        helper = project / "openspec/schemas/arbitrary/nested/tools/helpers/ddd.py"
        helper.parent.mkdir(parents=True)
        helper.touch()
        self.assertEqual(self.resolve(helper_file=helper, cwd=self.cwd), project)
        nested = helper.parent / "openspec/tools/check.py"
        nested.parent.mkdir(parents=True)
        nested.touch()
        (nested.parent.parent / 'config.yaml').touch()
        self.assertEqual(self.resolve(helper_file=nested, cwd=self.cwd), helper.parent)

    def test_schema_named_openspec_is_not_mistaken_for_project_boundary(self):
        project = self.base / 'application'
        helper = project / 'openspec/schemas/openspec/helpers/check.py'
        helper.parent.mkdir(parents=True)
        helper.touch()
        self.assertEqual(self.resolve(helper_file=helper, cwd=self.cwd), project)

    def test_nearest_cwd_markers_and_canonical_source_fallback(self):
        source = self.base / "source"
        helper = source / "src/schemas/ddd/helpers/check.py"
        helper.parent.mkdir(parents=True)
        helper.touch()
        (source / "book.toml").touch()
        self.assertEqual(self.resolve(helper_file=helper, cwd=self.cwd), source)
        for marker in ("openspec", "book-builder.toml", "book.toml"):
            with self.subTest(marker=marker):
                target = self.cwd / marker
                target.mkdir() if marker == "openspec" else target.touch()
                deep = self.cwd / "one/two"
                deep.mkdir(parents=True, exist_ok=True)
                self.assertEqual(self.resolve(helper_file=helper, cwd=deep), self.cwd)
                target.rmdir() if marker == "openspec" else target.unlink()

    def test_unmarked_standalone_falls_back_to_cwd(self):
        helper = self.base / "tools/check.py"
        helper.parent.mkdir()
        helper.touch()
        self.assertEqual(self.resolve(helper_file=helper, cwd=self.cwd), self.cwd)
        self.assertEqual(self.resolve(cwd=self.cwd), self.cwd)

    def test_distributed_commands_without_books_are_read_only_from_outside(self):
        project = self.base / "project"
        helper = project / "openspec/schemas/custom/deep/helpers"
        shutil.copytree(HELPERS, helper, ignore=shutil.ignore_patterns("__pycache__"))
        spec_file = project / "openspec/specs/sample/spec.md"
        spec_file.parent.mkdir(parents=True)
        spec_file.write_text("# Sample\n")
        (project / "inventory.json").write_text(json.dumps({"schema_version": 1, "specs": [
            {"id": "sample", "path": "openspec/specs/sample/spec.md", "depends_on": []}]}))
        records = project / "records"
        records.mkdir()
        (records / "adr-1.md").write_text("# ADR-001: Sample\nStatus: Observed\nDate: Unknown\nScope: Team\n")
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        for script, args in (("ddd.py", ["--catalog", "inventory.json", "check"]),
                             ("ddd.py", ["--catalog", "inventory.json", "context", "sample"]),
                             ("ddd.py", ["--catalog", "inventory.json", "impact", "sample"]),
                             ("check.py", ["--catalog", "inventory.json", "--decisions", "records"])):
            with self.subTest(script=script, args=args):
                result = subprocess.run([sys.executable, str(helper / script), *args],
                                        cwd=self.cwd, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                json.loads(result.stdout)
        after = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_invalid_explicit_root_preserves_cli_errors(self):
        for script in ("ddd.py", "check.py"):
            result = subprocess.run([sys.executable, str(HELPERS / script), "--root",
                                     str(self.base / "missing"), *(["check"] if script == "ddd.py" else [])],
                                    cwd=self.cwd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            if script == "check.py":
                self.assertEqual(json.loads(result.stdout)["status"], "error")
            else:
                self.assertIn("Error:", result.stderr)
