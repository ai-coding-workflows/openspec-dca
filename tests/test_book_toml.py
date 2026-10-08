import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/md-book-builder'))
from book_toml import update_book_config
from book_paths import tomllib


class TomlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'book.toml'
        self.assets = tuple(self.root / '.cache/scripts/mermaid/new' / name
                            for name in ('mermaid.min.js', 'mermaid-init.js'))
        for asset in self.assets:
            asset.parent.mkdir(parents=True, exist_ok=True)
            asset.write_text('asset')

    def test_preserves_comments_order_and_idempotence(self):
        original = '# author\r\n[book]\r\ntitle = "Book" # keep\r\n[output.html]\r\nadditional-js = [\r\n "custom.js", # custom comment\r\n]\r\n'
        self.config.write_bytes(original.encode())
        self.assertTrue(update_book_config(self.config, mermaid=True, svgbob=True, assets=self.assets))
        result = self.config.read_bytes().decode()
        self.assertIn('# custom comment\r\n', result)
        self.assertTrue(result.startswith(original.split('[output.html]')[0]))
        self.assertEqual(tomllib.loads(result)['output']['html']['additional-js'][0], 'custom.js')
        self.assertFalse(update_book_config(self.config, mermaid=True, svgbob=True, assets=self.assets))

    def test_existing_author_assets_not_owned_by_filename(self):
        for name in ('mermaid.min.js', 'mermaid-init.js'):
            (self.root / name).write_text('author')
        self.config.write_text('[preprocessor.mermaid]\ncommand="custom"\n[output.html]\nadditional-js=["mermaid.min.js", "mermaid-init.js"]\n')
        original = self.config.read_bytes()
        self.assertFalse(update_book_config(self.config, mermaid=True, assets=self.assets))
        self.assertEqual(original, self.config.read_bytes())
        self.config.write_text('[preprocessor.mermaid]\n[output.html]\nadditional-js=["mermaid.min.js", "mermaid-init.js"]\n')
        self.assertFalse(update_book_config(self.config, mermaid=True, assets=self.assets))

    def test_author_filename_aliases_satisfy_browser_assets(self):
        for name in ('mermaid.js', 'mermaid.init.js'):
            (self.root / name).write_text('author assets')
        self.config.write_text('[preprocessor.mermaid]\n[output.html]\nadditional-js=["mermaid.js", "mermaid.init.js"]\n')
        original = self.config.read_bytes()
        self.assertFalse(update_book_config(self.config, mermaid=True, assets=self.assets))
        self.assertEqual(self.config.read_bytes(), original)
        (self.root / 'mermaid.init.js').unlink()
        update_book_config(self.config, mermaid=True, assets=self.assets)
        refs = tomllib.loads(self.config.read_text())['output']['html']['additional-js']
        self.assertEqual(refs, ['mermaid.js', self.assets[1].relative_to(self.root).as_posix()])

    def test_refresh_cache_and_broken_refs(self):
        self.config.write_text('[output.html]\nadditional-js=["custom.js", ".cache/scripts/mermaid/old/mermaid.min.js", "mermaid-init.js"]\n')
        update_book_config(self.config, mermaid=True, assets=self.assets)
        refs = tomllib.loads(self.config.read_text())['output']['html']['additional-js']
        self.assertEqual(refs, ['custom.js'] + [p.relative_to(self.root).as_posix() for p in self.assets])

    def test_legacy_builder_cache_refreshes_without_treating_author_files_as_owned(self):
        old = self.root / '.cache/scripts'
        for name in ('mermaid.min.js', 'mermaid-init.js'):
            (old / name).write_text('old binary assets')
        self.config.write_text('[output.html]\nadditional-js=[".cache/scripts/mermaid.min.js", ".cache/scripts/mermaid-init.js"]\n')
        update_book_config(self.config, mermaid=True, assets=self.assets)
        refs = tomllib.loads(self.config.read_text())['output']['html']['additional-js']
        self.assertEqual(refs, [p.relative_to(self.root).as_posix() for p in self.assets])

    def test_unsupported_structure_no_partial_write(self):
        for text in ('output = {html = {additional-js = []}}\n', '[output]\nhtml.additional-js=[]\n', 'preprocessor={mermaid={}}\n'):
            self.config.write_text(text)
            with self.assertRaises(ValueError):
                update_book_config(self.config, mermaid=True, svgbob=True, assets=self.assets)
            self.assertEqual(self.config.read_text(), text)

    def test_duplicate_managed_refs_removed_comments_retained(self):
        self.config.write_text('[output.html]\nadditional-js=[\n".cache/scripts/mermaid/old/mermaid.min.js", # old\n".cache/scripts/mermaid/older/mermaid.min.js", # duplicate\n"mermaid-init.js", # broken\n]\n')
        update_book_config(self.config, mermaid=True, assets=self.assets)
        result = self.config.read_text()
        self.assertIn('# duplicate', result)
        self.assertEqual(len(tomllib.loads(result)['output']['html']['additional-js']), 2)

    def test_concurrent_edit_not_overwritten(self):
        self.config.write_text('[book]\n')
        from book_toml import _atomic_replace
        original = self.config.read_bytes()
        self.config.write_text('# changed by author\n[book]\n')
        with self.assertRaises(RuntimeError):
            _atomic_replace(self.config, original, b'[book]\ntitle="new"\n')
        self.assertIn('# changed by author', self.config.read_text())
        self.assertEqual(list(self.root.glob('.book.toml.*')), [])

    def test_failed_replace_leaves_config_and_cleans_stage(self):
        self.config.write_text('[book]\n')
        original = self.config.read_bytes()
        with patch('book_toml.os.replace', side_effect=OSError('failed')):
            with self.assertRaises(OSError):
                update_book_config(self.config, mermaid=True, assets=self.assets)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertEqual(list(self.root.glob('.book.toml.*')), [])

    def test_flags_off_never_remove_setup(self):
        self.config.write_text('[preprocessor.mermaid]\ncommand="mdbook-mermaid"\n[preprocessor.svgbob]\n[output.html]\nadditional-js=["missing.js"]\n')
        original = self.config.read_bytes()
        self.assertFalse(update_book_config(self.config, assets=self.assets))
        self.assertEqual(self.config.read_bytes(), original)

    def test_relative_paths_spaces_and_windows_error(self):
        self.config.write_text('[book]\n')
        assets = tuple(self.root / 'space dir' / p.name for p in self.assets)
        update_book_config(self.config, mermaid=True, assets=assets)
        self.assertIn('space dir/mermaid.min.js', self.config.read_text())
        original = self.config.read_bytes()
        with patch('book_toml.os.path.relpath', side_effect=ValueError('different drives')):
            with self.assertRaises(ValueError):
                update_book_config(self.config, mermaid=True, assets=self.assets)
        self.assertEqual(original, self.config.read_bytes())
