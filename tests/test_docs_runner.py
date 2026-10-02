"""Book selection and dispatch for both docs starters."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book'))
from book_paths import read_book_paths
from book_selection import select_book

spec = importlib.util.spec_from_file_location('docs_runner', ROOT / 'scripts/md-book/docs.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class DocsRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.book = self.root / 'architecture book'
        self.book.mkdir()
        (self.book / 'book.toml').write_text('[book]\nsrc="docs"\n[build]\nbuild-dir="build/site"\n')
        (self.root / 'docs-books.toml').write_text('[books]\nar42="architecture book"\nuser="architecture book/book.toml"\n')

    def test_default_alias_directory_and_file(self):
        self.assertEqual(select_book(self.root), self.root / 'book.toml')
        for value in ('ar42', 'user', 'architecture book', 'architecture book/book.toml'):
            self.assertEqual(select_book(self.root, value), self.book / 'book.toml')

    def test_mapping_paths_are_relative_to_mapping(self):
        mapping = self.book / 'mapping.toml'
        mapping.write_text('[books]\nar42="."\n')
        self.assertEqual(select_book(self.root, 'ar42', mapping), self.book / 'book.toml')

    def test_bad_selection_and_mapping(self):
        for value in ('missing', '../book.toml'):
            with self.assertRaises(ValueError):
                select_book(self.root, value)
        with self.assertRaisesRegex(ValueError, 'mapping not found'):
            select_book(self.root, 'ar42', self.root / 'missing.toml')
        mapping = self.root / 'docs-books.toml'
        for contents in ('books=[]', '[books]\nar42=42', '[books]\nar42=""'):
            mapping.write_text(contents)
            with self.assertRaises(ValueError):
                select_book(self.root, 'ar42')
        alternate = self.book / 'alternate.toml'
        alternate.write_text('[book]')
        with self.assertRaisesRegex(ValueError, 'named book.toml'):
            select_book(self.root, str(alternate))

    def test_main_dispatches_alias_and_default(self):
        (self.root / 'book.toml').write_text('[book]\nsrc="docs"\n')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner, 'native_command', return_value=0) as native:
            for options, expected in (([], self.root), (['--book', 'ar42'], self.book), (['-b', 'ar42'], self.book)):
                with patch.object(sys, 'argv', ['docs.py', *options, 'build']):
                    self.assertEqual(runner.main(), 0)
                self.assertEqual(native.call_args.args[1].repository, expected)

    def test_native_build_and_serve_use_selected_root(self):
        paths = read_book_paths(self.book / 'book.toml')
        with patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None) as prepare, \
                patch.object(runner, 'run', return_value=0) as run, \
                patch.object(runner, 'serve_process', return_value=0) as serve:
            self.assertEqual(runner.native_command('build', paths, None, False), 0)
            self.assertEqual(run.call_args_list[0].kwargs['cwd'], self.book)
            self.assertEqual(run.call_args_list[1].args[0][-1], str(self.book / 'book.toml'))
            prepare.assert_called_with(self.book / 'book.toml', paths.output_root / 'native-tools')
            self.assertEqual(runner.native_command('serve', paths, 3000, False), 0)
            self.assertEqual(serve.call_args.kwargs['cwd'], self.book)

    def test_docker_uses_selected_root_and_export(self):
        paths = read_book_paths(self.book / 'book.toml')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None), \
                patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(runner.docker_command('build', paths, None, False), 0)
            env = run.call_args_list[0].kwargs['env']
            self.assertEqual(env['DOCS_BOOK_ROOT'], '/book/architecture book')
            self.assertEqual(env['DOCS_BOOK_BUILD_PATH'], 'architecture book/build/site')
            self.assertEqual(run.call_args_list[-1].args[0][-1], str(self.book / 'book.toml'))
