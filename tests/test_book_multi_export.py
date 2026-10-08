"""Multiple configured/CLI export formats and failure preservation."""

from contextlib import nullcontext
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
from book_selection import select_books
from book_paths import read_book_paths

spec = importlib.util.spec_from_file_location('multi_export_runner', ROOT / 'scripts/md-book-builder/book.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class MultiExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for stub in (
                patch.object(runner, 'native_toolchain', return_value=(
                    {'mdbook': '/tools/mdbook', 'mdbook-mermaid': '/tools/mdbook-mermaid'}, 0)),
                patch.object(runner, 'capture_book', return_value=nullcontext(self.root / 'capture.json'))):
            stub.start()
            self.addCleanup(stub.stop)
        pdf_runtime = patch.object(runner, 'ensure_pdf_python', return_value=self.root / 'pdf/bin/python')
        pdf_runtime.start()
        self.addCleanup(pdf_runtime.stop)
        (self.root / 'book.toml').write_text('[book]\ntitle="Guide"\nsrc="src"\n'
                                            '[build]\nbuild-dir="build/site"\n')
        source = self.root / 'src'
        source.mkdir()
        (source / 'SUMMARY.md').write_text('- [Intro](intro.md)\n')
        (source / 'intro.md').write_text('# Intro\n\nExport content.\n')

    def config(self, fields):
        (self.root / 'book-builder.toml').write_text('[books.guide]\nconfig="book.toml"\n' + fields)

    def invoke(self, *args):
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(sys, 'argv', ['book.py', *args]):
            return runner.main()

    def formats_run(self, run):
        return [call.args[0][call.args[0].index('--format') + 1]
                for call in run.call_args_list if '--format' in call.args[0]]

    def test_configured_list_preserves_order_and_deduplicates(self):
        self.config('export-formats=["markdown", "typst", "markdown", "pdf"]\n')
        self.assertEqual(select_books(self.root)[0].export_formats, ('markdown', 'typst', 'pdf'))
        with patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export'), 0)
        self.assertEqual(self.formats_run(run), ['markdown', 'typst', 'pdf'])

    def test_single_format_and_default_remain_supported(self):
        for fields, expected in (('', ('markdown',)), ('export-format="typst"\n', ('typst',))):
            with self.subTest(fields=fields):
                self.config(fields)
                self.assertEqual(select_books(self.root)[0].export_formats, expected)

    def test_invalid_lists_and_conflicting_fields_are_rejected(self):
        invalid = ('[]', '"markdown"', '[42]', '[false]', '["html"]', '["markdown", ""]')
        for formats in invalid:
            with self.subTest(formats=formats):
                self.config('export-formats=' + formats + '\n')
                with self.assertRaisesRegex(ValueError, 'export-formats'):
                    select_books(self.root)
        self.config('export-format="markdown"\nexport-formats=["pdf"]\n')
        with self.assertRaisesRegex(ValueError, 'both|together'):
            select_books(self.root)

    def test_repeated_cli_formats_replace_configuration_and_deduplicate(self):
        self.config('export-formats=["pdf"]\n')
        with patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export', '--format', 'markdown', '--format', 'typst',
                                         '--format', 'markdown'), 0)
        self.assertEqual(self.formats_run(run), ['markdown', 'typst'])

    def test_repeated_cli_formats_override_build_defaults(self):
        self.config('export-formats=["pdf"]\n')
        with patch.object(runner, 'native_command', return_value=0) as command:
            self.assertEqual(self.invoke('build', '--format', 'markdown', '--format', 'typst'), 0)
        self.assertEqual(command.call_args.kwargs['output_formats'], ('markdown', 'typst'))

    def test_failed_format_does_not_prevent_remaining_formats(self):
        self.config('export-formats=["pdf", "markdown", "typst"]\n')
        with patch.object(runner, 'run', side_effect=[2, 0, 0]) as run:
            self.assertEqual(self.invoke('export'), 2)
        self.assertEqual(self.formats_run(run), ['pdf', 'markdown', 'typst'])

    def test_native_and_docker_build_html_once_then_export_all_formats(self):
        paths = read_book_paths(self.root / 'book.toml')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None):
            for command, expected_html_calls in ((runner.native_command, 1), (runner.docker_command, 2)):
                with self.subTest(command=command.__name__), \
                        patch.object(runner, 'run', return_value=0) as run:
                    self.assertEqual(command('build', paths, None, False,
                                             output_formats=('markdown', 'typst')), 0)
                    self.assertEqual(self.formats_run(run), ['markdown', 'typst'])
                    self.assertEqual(run.call_count, expected_html_calls + 2)

    @unittest.skipUnless(shutil.which('mdbook') and shutil.which('mdbook-mermaid'),
                         'Common export requires the native mdBook toolchain')
    def test_real_export_writes_both_files_without_building_html(self):
        self.config('export-formats=["markdown", "typst"]\n')
        target = self.root / 'scripts/md-book-builder'
        shutil.copytree(ROOT / 'scripts/md-book-builder', target,
                        ignore=shutil.ignore_patterns('__pycache__', '.venv', '.cache'))
        result = subprocess.run([sys.executable, str(target / 'book.py'),
                                 '--root', str(self.root), 'export'],
                                cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for suffix in ('.md', '.typ'):
            self.assertIn('Export content.', (self.root / 'build/site' / ('Guide' + suffix)).read_text())
        self.assertFalse((self.root / 'build/site/intro.html').exists())
