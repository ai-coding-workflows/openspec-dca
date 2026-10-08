"""Unified export dispatch and native Python execution without uv."""

from contextlib import nullcontext
import importlib.util
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
spec = importlib.util.spec_from_file_location('export_docs_runner', ROOT / 'scripts/md-book-builder/book.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class DocsExportTests(unittest.TestCase):
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
        for name, title, output in (('book.toml', 'Main', 'build/main'),
                                    ('book.user.toml', 'User', 'build/user')):
            (self.root / name).write_text(f'[book]\ntitle="{title}"\nsrc="docs"\n'
                                          f'[build]\nbuild-dir="{output}"\n')
        (self.root / 'docs-books.toml').write_text('[books]\nuser="book.user.toml"\n')

    def invoke(self, *args):
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(sys, 'argv', ['docs.py', *args]):
            return runner.main()

    def test_export_selects_alias_and_forwards_format_and_template(self):
        with patch.object(runner, 'run', return_value=0) as run, \
                patch.object(runner.shutil, 'which', side_effect=AssertionError('No tools needed')):
            self.assertEqual(self.invoke('--book', 'user', 'export', '--format', 'typst',
                                         '--template', 'templates/print.typ'), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[:2], [sys.executable, str(runner.EXPORTER_SCRIPT)])
        self.assertIn('typst', command)
        self.assertIn('templates/print.typ', command)
        self.assertEqual(command[-1], str(self.root / 'book.user.toml'))

    def test_default_export_processes_all_books_and_continues_on_failure(self):
        with patch.object(runner, 'run', side_effect=[2, 0]) as run:
            self.assertEqual(self.invoke('export'), 2)
        self.assertEqual([call.args[0][-1] for call in run.call_args_list],
                         [str(self.root / 'book.toml'), str(self.root / 'book.user.toml')])

    def test_native_and_docker_build_export_with_current_python_without_uv(self):
        paths = runner.read_book_paths(self.root / 'book.toml')
        def which(name):
            return None if name == 'uv' else '/tools/' + name
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=which) as lookup, \
                patch.object(runner, 'prepare_svgbob', return_value=None), \
                patch.object(runner, 'run', return_value=0) as run:
            for command in (runner.native_command, runner.docker_command):
                with self.subTest(mode=command.__name__):
                    self.assertEqual(command('build', paths, None, False), 0)
                    self.assertEqual(run.call_args.args[0][0], sys.executable)
                    self.assertEqual(run.call_args.args[0][1], str(runner.EXPORTER_SCRIPT))
                    self.assertEqual(run.call_args.args[0][-1], str(paths.config_file))
            self.assertNotIn(('uv',), [call.args for call in lookup.call_args_list])

    def test_export_options_are_rejected_for_serve(self):
        for args in (('serve', '--format', 'pdf'), ('serve', '--template', 'print.typ')):
            with self.subTest(args=args), self.assertRaises(SystemExit) as error:
                self.invoke(*args)
            self.assertEqual(error.exception.code, 2)

    @unittest.skipUnless(shutil.which('mdbook') and shutil.which('mdbook-mermaid'),
                         'Common export requires the native mdBook toolchain')
    def test_real_cli_and_shell_starter_export_without_html_build(self):
        scripts = self.root / 'scripts'
        shutil.copytree(ROOT / 'scripts/md-book-builder', scripts / 'md-book-builder',
                        ignore=shutil.ignore_patterns('__pycache__', '.venv', '.cache'))
        shutil.copytree(ROOT / 'scripts/md-book', scripts / 'md-book',
                        ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT / 'scripts/book.sh', scripts / 'book.sh')
        shutil.copy2(ROOT / 'scripts/docs.sh', scripts / 'docs.sh')
        source = self.root / 'docs'
        source.mkdir()
        (source / 'SUMMARY.md').write_text('- [Intro](intro.md)\n')
        (source / 'intro.md').write_text('# Intro\n\nExported content.\n')
        commands = [[sys.executable, str(scripts / 'md-book-builder/book.py'),
                     '--root', str(self.root), 'export'],
                    [sys.executable, str(scripts / 'md-book/docs.py'),
                     '--root', str(self.root), '--book', 'user', 'export']]
        if os.name == 'posix':
            commands.extend([
                ['/bin/sh', str(scripts / 'book.sh'), '--root', str(self.root),
                 '--book', 'user', 'export', '--format', 'typst'],
                ['/bin/sh', str(scripts / 'docs.sh'), '--root', str(self.root),
                 '--book', 'user', 'export'],
            ])
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Exported content.', (self.root / 'build/main/Main.md').read_text())
        self.assertIn('Exported content.', (self.root / 'build/user/User.md').read_text())
        if os.name == 'posix':
            self.assertTrue((self.root / 'build/user/User.typ').is_file())
        self.assertFalse(list(self.root.rglob('intro.html')))
        self.assertFalse(list(self.root.rglob('mdbook-runtime-*')))

    def test_windows_starter_prefers_activated_environment(self):
        starter = (ROOT / 'scripts/book.cmd').read_text()
        self.assertLess(starter.index('if defined VIRTUAL_ENV goto use_python'),
                        starter.index('where py'))

    def builder_config(self, *, serve=False):
        config = self.root / 'book-builder.toml'
        config.write_text('[books.user]\nconfig="book.user.toml"\n'
                          f'export-format="typst"\nserve={str(serve).lower()}\n')
        return config

    def test_builder_config_controls_general_build_list_and_export_format(self):
        self.builder_config()
        with patch.object(runner, 'native_command', return_value=0) as command:
            self.assertEqual(self.invoke('build'), 0)
        command.assert_called_once()
        self.assertEqual(command.call_args.args[1].config_file, self.root / 'book.user.toml')
        self.assertEqual(command.call_args.kwargs['output_formats'], ('typst',))

    def test_builder_config_format_applies_to_exports_and_cli_override_to_builds(self):
        self.builder_config()
        with patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export'), 0)
            self.assertIn('typst', run.call_args.args[0])
            self.assertEqual(self.invoke('--book', 'book.user.toml', 'export', '--format', 'markdown'), 0)
            self.assertIn('markdown', run.call_args.args[0])
        with patch.object(runner, 'native_command', return_value=0) as command:
            self.assertEqual(self.invoke('build', '--format', 'pdf'), 0)
            self.assertEqual(command.call_args.kwargs['output_formats'], ('pdf',))

    def test_general_serve_filters_disabled_books_but_explicit_selection_overrides(self):
        self.builder_config(serve=False)
        with patch.object(runner, 'native_command', return_value=0) as command, \
                patch.object(runner, 'free_port', return_value=3000) as port:
            self.assertEqual(self.invoke('serve'), 2)
            command.assert_not_called()
            port.assert_not_called()
            self.assertEqual(self.invoke('--book', 'user', 'serve'), 0)
            self.assertEqual(command.call_args.args[1].config_file, self.root / 'book.user.toml')

    def test_explicit_builder_config_is_supported(self):
        config = self.builder_config()
        custom = self.root / 'custom-builder.toml'
        config.rename(custom)
        with patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('--config', str(custom), 'export'), 0)
        run.assert_called_once()
        self.assertIn('typst', run.call_args.args[0])

    def test_export_failure_is_not_hidden(self):
        with patch.object(runner, 'run', return_value=2):
            self.assertEqual(self.invoke('--book', 'user', 'export', '--format', 'pdf'), 2)
