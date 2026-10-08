"""Subprocess coverage for relocated and legacy exporter entry points."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = PROJECT_ROOT / "scripts/md-book-builder/exporter/export_book.py"
LEGACY = PROJECT_ROOT / "scripts/book-exporter/export_book.py"


class ExporterCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        self.config = self.root / "book.toml"
        self.config.write_text(
            '[book]\ntitle = "Compatibility Guide"\nsrc = "src"\n'
            '[build]\nbuild-dir = "output"\n',
            encoding="utf-8",
        )
        (self.root / "src/SUMMARY.md").write_text(
            "[Intro](intro.md)\n", encoding="utf-8"
        )
        (self.root / "src/intro.md").write_text(
            "# Intro\n\nHello **world**.\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def run_export(self, script, output_format, *, missing_typst=False):
        # Python 3.11+ must work with no site packages or PYTHONPATH, even when
        # launched outside the repository. 3.10 retains its tomli fallback.
        isolation = ["-I", "-S"] if sys.version_info >= (3, 11) else []
        command = [sys.executable, *isolation, str(script), str(self.config),
                   "--format", output_format]
        if missing_typst:
            # Block only the optional binding so this also exercises Python
            # 3.10 with tomli installed, independent of installed PDF packages.
            code = """
import importlib.abc
import runpy
import sys
class MissingTypst(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'typst':
            raise ModuleNotFoundError("No module named 'typst'")
sys.meta_path.insert(0, MissingTypst())
script = sys.argv.pop(1)
runpy.run_path(script, run_name='__main__')
"""
            command = [sys.executable, "-c", code, str(script), str(self.config),
                       "--format", output_format]
        return subprocess.run(
            command, cwd=self.root, text=True, capture_output=True, check=False,
        )

    def test_old_and_new_cli_export_markdown_and_typst_without_packages(self):
        for script in (CANONICAL, LEGACY):
            for output_format, suffix in (("markdown", ".md"), ("typst", ".typ")):
                with self.subTest(script=script, output_format=output_format):
                    result = self.run_export(script, output_format)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    output = self.root / "output" / ("Compatibility Guide" + suffix)
                    self.assertEqual(result.stdout.strip(), str(output))
                    content = output.read_text(encoding="utf-8")
                    self.assertIn("Intro", content)
                    self.assertIn("world", content)
                    output.unlink()

    def test_missing_pdf_binding_has_actionable_hint_at_both_paths(self):
        for script in (CANONICAL, LEGACY):
            with self.subTest(script=script):
                result = self.run_export(script, "pdf", missing_typst=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("python3 -m venv .venv", result.stderr)
                self.assertIn(
                    "python -m pip install -r scripts/md-book-builder/exporter/requirements-pdf.txt",
                    result.stderr,
                )
                self.assertNotIn("uv run", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse((self.root / "output/Compatibility Guide.pdf").exists())
                self.assertTrue((self.root / "output/Compatibility Guide.typ").is_file())

    def test_legacy_imports_alias_all_apis_and_dataclasses(self):
        code = f"""
import dataclasses
import importlib
import pickle
import sys
from pathlib import Path
sys.path.insert(0, {str(LEGACY.parent)!r})
legacy = importlib.import_module('export_book')
converter = importlib.import_module('markdown_to_typst')
canonical = importlib.import_module('exporter.export_book')
canonical_converter = importlib.import_module('exporter.markdown_to_typst')
assert legacy is canonical
assert converter is canonical_converter
for name in vars(canonical):
    assert getattr(legacy, name) is getattr(canonical, name)
from export_book import BookConfig, Chapter, dataclass, export_pdf, _load_template
assert dataclasses.is_dataclass(BookConfig)
assert dataclasses.is_dataclass(Chapter)
chapter = Chapter(Path('chapter.md'), 'Chapter', 'chapter')
assert pickle.loads(pickle.dumps(chapter)) == chapter
assert _load_template(Path('.'), None)
"""
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=self.root,
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pdf_requirement_is_pinned_and_templates_are_only_canonical(self):
        requirements = CANONICAL.parent / "requirements-pdf.txt"
        self.assertEqual(requirements.read_text(encoding="utf-8").splitlines(),
                         ['typst==0.15.0', 'tomli==2.2.1; python_version < "3.11"'])
        self.assertTrue((CANONICAL.parent / "templates/default.typ").is_file())
        self.assertTrue((CANONICAL.parent / "templates/modern-guide.typ").is_file())
        self.assertFalse((LEGACY.parent / "templates").exists())
        self.assertFalse((LEGACY.parent / "pyproject.toml").exists())
        self.assertFalse((LEGACY.parent / "uv.lock").exists())


if __name__ == "__main__":
    unittest.main()
