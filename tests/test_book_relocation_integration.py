"""Real native builds using a relocated builder and cache-managed diagram assets."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'scripts/md-book-builder'


class Scripts(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.sources = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'script' and values.get('src'):
            self.sources.append(values['src'])


@unittest.skipUnless(shutil.which('mdbook') and shutil.which('mdbook-mermaid'), 'Native mdBook/Mermaid required')
class RelocatedBuilderIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project with spaces'
        self.builder = self.root / 'tools/documentation/md-book-builder'
        shutil.copytree(SOURCE, self.builder, ignore=shutil.ignore_patterns('.cache', '.venv', '__pycache__'))
        (self.root / 'text').mkdir()
        (self.root / 'text/SUMMARY.md').write_text('- [Diagram](diagram.md)\n')
        (self.root / 'text/diagram.md').write_text('# Diagram\n\n```mermaid\nflowchart LR\n  A --> B\n```\n')
        self.config = self.root / 'book.architecture.toml'
        self.config.write_text('# Keep this comment\n[book]\ntitle="Managed diagrams"\nsrc="text"\n[build]\nbuild-dir="output/site"\n')
        (self.root / 'book-builder.toml').write_text('[books.diagram]\nconfig="book.architecture.toml"\nmermaid=true\nsvgbob=false\n')

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(self.builder / 'book.py'), '--root', str(self.root), *args],
                              cwd=self.root.parent, capture_output=True, text=True, timeout=90)

    def test_explicit_feature_sets_up_persistent_cache_paths_in_alternate_book(self):
        source = (self.root / 'text/diagram.md').read_bytes()
        result = self.invoke('build')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        configuration = self.config.read_text()
        self.assertTrue(configuration.startswith('# Keep this comment\n'))
        self.assertIn('[preprocessor.mermaid]', configuration)
        self.assertIn('.cache/scripts/mermaid/', configuration)
        self.assertNotIn('docs/theme', configuration)
        assets = sorted((self.builder / '.cache/scripts/mermaid').glob('*/mermaid*.js'))
        self.assertEqual(len(assets), 2)
        output = self.root / 'output/site'
        html = (output / 'diagram.html').read_text()
        scripts = [ref for ref in Scripts(html).sources if 'mermaid' in ref]
        self.assertEqual(len(scripts), 2)
        for ref in scripts:
            target = output / unquote(urlsplit(ref).path)
            self.assertTrue(target.is_file(), ref)
            self.assertIn(target.read_bytes(), [asset.read_bytes() for asset in assets])
        self.assertIn('mermaid', html)
        self.assertTrue((output / 'Managed diagrams.md').is_file())
        self.assertEqual(source, (self.root / 'text/diagram.md').read_bytes())
        second = self.invoke('build')
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(self.config.read_text(), configuration)
        self.assertFalse(list(self.root.glob('output/**/mdbook-runtime-*')))
        self.assertFalse(list(self.root.glob('output/**/mdbook-capture-*')))

    def test_builder_cache_outside_nested_canonical_book_root_has_local_browser_assets(self):
        nested = self.root / 'handbooks/architecture'
        nested.mkdir(parents=True)
        self.config.rename(nested / 'book.toml')
        self.config = nested / 'book.toml'
        shutil.move(str(self.root / 'text'), str(nested / 'text'))
        (self.root / 'book-builder.toml').write_text('[books.diagram]\nconfig="handbooks/architecture/book.toml"\nmermaid=true\nsvgbob=false\n')
        result = self.invoke('build')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('../../tools/documentation/', self.config.read_text())
        output = nested / 'output/site'
        refs = [ref for ref in Scripts((output / 'diagram.html').read_text()).sources if 'mermaid' in ref]
        self.assertEqual(len(refs), 2)
        self.assertTrue(all((output / unquote(urlsplit(ref).path)).is_file() for ref in refs))
        self.assertFalse(list((nested / 'output').glob('mdbook-runtime-*')))
        self.assertFalse(list(nested.glob('book-builder-assets-*')))

    def test_disabled_features_do_not_modify_plain_configuration(self):
        (self.root / 'book-builder.toml').write_text('[books.diagram]\nconfig="book.architecture.toml"\nmermaid=false\nsvgbob=false\n')
        original = self.config.read_bytes()
        result = self.invoke('export')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.builder / '.cache/scripts').exists())


if __name__ == '__main__':
    unittest.main()
