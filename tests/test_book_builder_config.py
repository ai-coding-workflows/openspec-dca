"""Configuration authority, metadata, and compatibility for book selection."""

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
from book_selection import BookDefinition, select_book, select_books
from book_discovery import discover_books


class BookBuilderConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.primary = self.book('book.toml')
        self.user = self.book('book.user.toml')

    def book(self, name):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[book]\n', encoding='utf-8')
        return path

    def config(self, text, name='book-builder.toml'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_authority_and_order(self):
        self.config('[books.user]\nconfig="book.user.toml"\nexport-format="pdf"\n'
                    'serve=false\n[books.handbook]\nconfig="book.toml"\n')
        expected = [BookDefinition(self.user, ('pdf',), False), BookDefinition(self.primary)]
        self.assertEqual(select_books(self.root), expected)
        self.assertEqual(select_books(self.root, action='export'), expected)
        self.assertEqual(discover_books(self.root), [self.user, self.primary])
        self.config('[books.user]\nconfig="book.user.toml"\n')
        self.assertEqual(discover_books(self.root), [self.user])
        self.assertEqual(select_book(self.root), self.primary)

    def test_absent_config_uses_root_discovery_not_legacy_mapping(self):
        admin = self.book('book.admin.toml')
        self.book('nested/book.toml')
        self.config('[books]\nuser="book.user.toml"\n', 'docs-books.toml')
        self.assertEqual(discover_books(self.root), [self.primary, admin, self.user])
        self.assertEqual(select_books(self.root, 'user'), [BookDefinition(self.user)])

    def test_metadata_for_alias_directory_and_direct_path(self):
        nested = self.book('nested/book.toml')
        mapping = self.config('[books.user]\nconfig="."\nexport-format="typst"\n'
                              'serve=false\n', 'nested/config.toml')
        expected = [BookDefinition(nested, ('typst',), False)]
        for selection in ('user', 'nested', 'nested/book.toml', str(nested)):
            with self.subTest(selection=selection):
                self.assertEqual(select_books(self.root, selection, mapping), expected)
        self.assertEqual(select_books(self.root, 'book.toml', mapping),
                         [BookDefinition(self.primary)])
        self.assertEqual(select_book(self.root, 'user', mapping), nested)

    def test_feature_policies_inherit_for_custom_mapping_paths(self):
        nested = self.book('nested/book.toml')
        mapping = self.config('[books.user]\nconfig="."\nmermaid=false\nsvgbob=true\n',
                              'nested/custom.toml')
        for selection in (None, 'user', 'nested', str(nested)):
            with self.subTest(selection=selection):
                record = select_books(self.root, selection, mapping)[0]
                self.assertIs(record.mermaid, False)
                self.assertIs(record.svgbob, True)
        record = select_books(self.root, 'book.toml', mapping)[0]
        self.assertIsNone(record.mermaid)
        self.assertIsNone(record.svgbob)

    def test_feature_policy_requires_boolean(self):
        for feature in ('mermaid', 'svgbob'):
            for value in ('1', '"false"', '[]', '{}'):
                with self.subTest(feature=feature, value=value):
                    self.config(f'[books.main]\nconfig="book.toml"\n{feature}={value}\n')
                    with self.assertRaisesRegex(ValueError, feature + '.*boolean'):
                        select_books(self.root)

    def test_serve_filter_and_explicit_override(self):
        self.config('[books.user]\nconfig="book.user.toml"\nserve=false\n'
                    '[books.handbook]\nconfig="book.toml"\n')
        self.assertEqual(select_books(self.root, action='serve'), [BookDefinition(self.primary)])
        for selection in ('user', 'book.user.toml'):
            self.assertEqual(select_books(self.root, selection, action='serve'),
                             [BookDefinition(self.user, serve=False)])
        self.config('[books.user]\nconfig="book.user.toml"\nserve=false\n')
        self.assertEqual(select_books(self.root, action='serve'), [])

    def test_legacy_strings_and_duplicate_aliases(self):
        mapping = self.config('[books]\none="book.toml"\ntwo="book.toml"\n', 'aliases.toml')
        for alias in ('one', 'two'):
            self.assertEqual(select_books(self.root, alias, mapping), [BookDefinition(self.primary)])
        self.assertEqual(select_books(self.root, mapping=mapping),
                         [BookDefinition(self.primary), BookDefinition(self.primary)])

    def test_legacy_direct_selection_does_not_validate_unrelated_aliases(self):
        self.config('[books]\nbad=""\n', 'docs-books.toml')
        self.assertEqual(select_book(self.root, 'book.toml'), self.primary)
        with self.assertRaises(ValueError):
            select_book(self.root, 'bad')

    def test_custom_metadata_and_defaults(self):
        self.config('[custom]\nthing=true\n[books.handbook]\nconfig="book.toml"\n'
                    'template="ignored.typ"\ncustom={number=42}\n')
        record = select_books(self.root)[0]
        self.assertEqual(record, BookDefinition(self.primary, ('markdown',), True))
        with self.assertRaises(FrozenInstanceError):
            record.serve = False

    def test_invalid_known_fields_and_books(self):
        invalid = [
            '', '[custom]\nx=1', '[books]', 'books=[]', 'books="wrong"',
            '[books.user]\nserve=true', '[books]\nuser=42',
            '[books.user]\nconfig=42', '[books.user]\nconfig=""',
            '[books.user]\nconfig="missing/book.toml"',
        ]
        for field, values in {'serve': ['1', '"false"', '[]'],
                              'export-format': ['false', '42', '"html"', '""']}.items():
            invalid.extend('[books.user]\nconfig="book.toml"\n' + field + '=' + value
                           for value in values)
        for text in invalid:
            with self.subTest(text=text):
                self.config(text)
                with self.assertRaises(ValueError):
                    select_books(self.root)

    def test_missing_explicit_mapping_and_invalid_toml(self):
        for selection in (None, 'book.toml'):
            with self.assertRaisesRegex(ValueError, 'mapping not found'):
                select_books(self.root, selection, Path('missing.toml'))
        self.config('[books')
        with self.assertRaises(ValueError):
            select_books(self.root)

    def test_outside_repository_and_invalid_name(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / 'book.toml'
            outside.write_text('[book]\n')
            for selection in (str(outside),):
                with self.assertRaisesRegex(ValueError, 'inside the repository'):
                    select_books(self.root, selection)
            self.config('[books.user]\nconfig=' + repr(str(outside)) + '\n')
            with self.assertRaisesRegex(ValueError, 'inside the repository'):
                select_books(self.root)
        self.book('alternate.toml')
        self.config('[books.user]\nconfig="alternate.toml"\n')
        with self.assertRaisesRegex(ValueError, 'named book.toml'):
            select_books(self.root)

    def test_no_discovered_books(self):
        self.primary.unlink()
        self.user.unlink()
        with self.assertRaisesRegex(ValueError, 'No book.toml'):
            select_books(self.root)


if __name__ == '__main__':
    unittest.main()
