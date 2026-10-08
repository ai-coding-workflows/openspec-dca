"""Real mdBook pipeline exports generated chapters without modifying sources."""

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = os.name == 'posix' and all(shutil.which(name) for name in ('mdbook', 'mdbook-mermaid'))
PREPROCESSOR = '''import json, sys
from pathlib import Path
if len(sys.argv) > 1 and sys.argv[1] == 'supports':
    sys.exit(0)
context, book = json.load(sys.stdin)
with Path(TRACE).open('a') as log:
    log.write(context['renderer'] + '\\n')
parent = book['items'][0]['Chapter']
parent['content'] = parent['content'].replace('{{#generated-index}}',
    '[Generated scope](generated/scope.md#custom-target)')
child = {'name': 'Generated Scope', 'path': 'generated/scope.md',
         'source_path': 'generated/scope.md', 'number': [1, 1],
         'parent_names': [parent['name']],
         'content': '# Generated Scope\\n\\n<a id="custom-target"></a>\\n\\nRuntime rule.\\n',
         'sub_items': [{'Chapter': {'name': 'Nested', 'path': 'generated/scope/nested.md',
             'source_path': 'generated/scope/nested.md', 'number': [1, 1, 1],
             'parent_names': [parent['name'], 'Generated Scope'],
             'content': '# Nested\\n\\nNested generated material.\\n', 'sub_items': []}}]}
parent['sub_items'].append({'Chapter': child})
json.dump(book, sys.stdout)
'''


@unittest.skipUnless(AVAILABLE, 'Preprocessor integration requires native mdBook tools and POSIX')
class PreprocessorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'scripts/md-book-builder', self.root / 'scripts/md-book-builder',
                        ignore=shutil.ignore_patterns('__pycache__', '.venv', '.cache'))
        self.runner = self.root / 'scripts/md-book-builder/book.py'
        self.source = self.root / 'docs'
        self.source.mkdir()
        (self.source / 'SUMMARY.md').write_text('- [Index](index.md)\n')
        (self.source / 'index.md').write_text('# Index\n\n{{#generated-index}}\n\n'
                                             '{{#include ../snippets/shared.md}}\n')
        (self.root / 'snippets').mkdir()
        (self.root / 'snippets/shared.md').write_text('Expanded by the native include preprocessor.\n')
        self.trace = self.root / 'preprocess.log'
        self.preprocessor = self.root / 'preprocess.py'
        self.preprocessor.write_text('TRACE = ' + repr(str(self.trace)) + '\n' + PREPROCESSOR)
        command = shlex.join([sys.executable, str(self.preprocessor)])
        self.config = self.root / 'book.generated.toml'
        self.config.write_text('[book]\ntitle="Generated Guide"\nsrc="docs"\n'
                               '[build]\nbuild-dir="build/site"\n'
                               '[preprocessor.synthetic]\ncommand=' + json.dumps(command) + '\n'
                               'before=["links"]\n')
        (self.root / 'book-builder.toml').write_text(
            '[books.guide]\nconfig="book.generated.toml"\nexport-formats=["markdown", "typst"]\n')
        self.originals = {path: path.read_bytes() for path in self.root.rglob('*')
                          if path.is_file() and 'scripts' not in path.relative_to(self.root).parts}

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(self.runner), '--root', str(self.root), *args],
                              cwd=ROOT, text=True, capture_output=True, timeout=60)

    def assert_sources_unchanged(self):
        for path, content in self.originals.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertFalse((self.source / 'generated/scope.md').exists())
        self.assertFalse(list(self.root.glob('build/**/mdbook-capture-*')))
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_export_runs_pipeline_once_and_includes_virtual_nested_chapters(self):
        result = self.invoke('export')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.trace.read_text().splitlines(), ['book-export'])
        output = self.root / 'build/site'
        for suffix in ('.md', '.typ'):
            text = (output / ('Generated Guide' + suffix)).read_text()
            self.assertIn('Runtime rule.', text)
            self.assertIn('Nested generated material.', text)
            self.assertIn('Expanded by the native include preprocessor.', text)
            self.assertLess(text.index('Runtime rule.'), text.index('Nested generated material.'))
            self.assertNotIn('{{#generated-index}}', text)
            self.assertNotIn('{{#include', text)
        typst = (output / 'Generated Guide.typ').read_text()
        self.assertIn('custom-target', typst)
        self.assertNotIn('<a id=', typst)
        self.assertFalse((output / 'index.html').exists())
        self.assert_sources_unchanged()

    def test_build_generates_html_and_exports_without_dropping_virtual_chapters(self):
        result = self.invoke('build')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.trace.read_text().splitlines(), ['book-export', 'html'])
        output = self.root / 'build/site'
        self.assertIn('Runtime rule.', (output / 'generated/scope.html').read_text())
        self.assertIn('Runtime rule.', (output / 'Generated Guide.md').read_text())
        self.assert_sources_unchanged()

    def test_export_preserves_existing_html(self):
        output = self.root / 'build/site'
        output.mkdir(parents=True)
        sentinel = output / 'index.html'
        sentinel.write_text('Preserve previous HTML')
        result = self.invoke('export')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(sentinel.read_text(), 'Preserve previous HTML')
        self.assert_sources_unchanged()

    def test_native_renderer_restriction_is_respected(self):
        self.config.write_text(self.config.read_text() + 'renderers=["html"]\n')
        result = self.invoke('export', '--format', 'markdown')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        content = (self.root / 'build/site/Generated Guide.md').read_text()
        self.assertNotIn('Runtime rule.', content)
        self.assertFalse(self.trace.exists())

    def test_missing_summary_source_is_not_created_during_export(self):
        (self.source / 'SUMMARY.md').write_text('- [Missing](missing.md)\n')
        result = self.invoke('export')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.source / 'missing.md').exists())
        self.assertFalse((self.root / 'build/site/Generated Guide.md').exists())
        self.assertFalse(list(self.root.glob('build/**/mdbook-capture-*')))

    def test_failing_preprocessor_does_not_silently_export_raw_sources(self):
        self.preprocessor.write_text("import sys\nif 'supports' not in sys.argv: sys.exit(5)\n")
        result = self.invoke('export')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'build/site/Generated Guide.md').exists())
        self.assertFalse(list(self.root.glob('build/**/mdbook-capture-*')))
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))
