import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
from book_paths import read_book_paths


class BookDestinationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        self.config = self.root / 'book.toml'

    def configure(self, output, source='src'):
        self.config.write_text('[book]\nsrc=' + json.dumps(str(source)) +
                               '\n[build]\nbuild-dir=' + json.dumps(str(output)) + '\n')

    def test_book_root_and_ancestor_destinations_are_rejected(self):
        for output in ('.', '..', self.root.parent):
            with self.subTest(output=output):
                self.configure(output)
                with self.assertRaisesRegex(ValueError, 'root directory'):
                    read_book_paths(self.config)

    def test_source_destination_is_rejected(self):
        self.configure('src')
        with self.assertRaisesRegex(ValueError, 'source directory'):
            read_book_paths(self.config)

    def test_absolute_source_destination_is_rejected(self):
        source = self.root.parent / 'shared-sources'
        self.configure(source, source)
        with self.assertRaisesRegex(ValueError, 'source directory'):
            read_book_paths(self.config)

    def test_native_external_output_remains_supported(self):
        output = self.root.parent / 'rendered'
        self.configure(output)
        self.assertEqual(read_book_paths(self.config).build_dir, output)


if __name__ == '__main__':
    unittest.main()
