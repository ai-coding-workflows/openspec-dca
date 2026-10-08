"""Project root discovery has no installation-depth assumption."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

BUILDER = Path(__file__).resolve().parents[1] / 'scripts/md-book-builder'
sys.path.insert(0, str(BUILDER))


class BookRootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def resolve(self, *args, **kwargs):
        from book_root import resolve_project_root
        return resolve_project_root(*args, **kwargs)

    def test_explicit_directory_needs_no_marker(self):
        self.assertEqual(self.resolve(self.root), self.root)
        with self.assertRaisesRegex(ValueError, 'directory'):
            self.resolve(self.root / 'missing')

    def test_cwd_nearest_marker_precedes_builder(self):
        (self.root / 'book.toml').write_text('[book]\n')
        nested = self.root / 'nested'
        nested.mkdir()
        (nested / 'book-builder.toml').write_text('[books]\n')
        child = nested / 'deep'
        child.mkdir()
        self.assertEqual(self.resolve(cwd=child, builder_dir=self.root), nested)

    def test_builder_fallback_and_clear_failure(self):
        builder = self.root / 'tools/docs/md-book-builder'
        builder.mkdir(parents=True)
        with tempfile.TemporaryDirectory() as outside:
            with self.assertRaisesRegex(ValueError, 'book-builder.toml.*book.toml'):
                self.resolve(cwd=outside, builder_dir=builder)
            (self.root / 'book.toml').write_text('[book]\n')
            self.assertEqual(self.resolve(cwd=outside, builder_dir=builder), self.root)

    def test_import_without_markers_does_not_discover(self):
        module = self.root / 'book_root.py'
        shutil.copyfile(BUILDER / 'book_root.py', module)
        result = subprocess.run([sys.executable, '-c', 'import book_root; print("imported")'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('imported', result.stdout)

    def test_relocated_checker_subprocess(self):
        builder = self.root / 'tools/docs/md-book-builder'
        shutil.copytree(BUILDER, builder, ignore=shutil.ignore_patterns('.cache', '.venv', '__pycache__'))
        (self.root / 'book.toml').write_text('[book]\nsrc="text"\n')
        (self.root / 'text').mkdir()
        (self.root / 'text/page.md').write_text('# Page\n')
        with tempfile.TemporaryDirectory() as outside:
            result = subprocess.run([sys.executable, str(builder / 'check.py')], cwd=outside,
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('references verified', result.stdout)


if __name__ == '__main__':
    unittest.main()
