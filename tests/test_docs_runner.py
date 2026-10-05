"""Book selection and dispatch for both docs starters."""

import importlib.util
import json
import os
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

    def alternate_paths(self):
        config = self.book / 'user.book.toml'
        config.write_text('[book]\nsrc="docs"\n[build]\nbuild-dir="build/user"\n')
        (self.book / 'docs').mkdir(exist_ok=True)
        (self.book / 'docs/chapter.md').write_text('Original chapter')
        return read_book_paths(config)

    def test_alternate_selection_and_config_identity(self):
        paths = self.alternate_paths()
        mapping = self.root / 'docs-books.toml'
        mapping.write_text('[books]\nuser="architecture book/user.book.toml"\n')
        for selection in ('user', 'architecture book/user.book.toml'):
            self.assertEqual(select_book(self.root, selection), paths.config_file)
        self.assertEqual(paths.config_file, self.book / 'user.book.toml')

    def test_staging_relative_links_and_cleanup(self):
        from book_runtime import staged_book
        paths = self.alternate_paths()
        originals = {p: p.read_bytes() for p in self.book.rglob('*') if p.is_file()}
        for docker_mode in (False, True):
            with staged_book(paths, docker_mode=docker_mode) as runtime:
                self.assertEqual(runtime.parent, paths.output_root)
                self.assertNotEqual(runtime, self.book)
                self.assertFalse((runtime / 'build').exists())
                for name in ('book.toml', 'user.book.toml', 'docs'):
                    link = runtime / name
                    self.assertTrue(link.is_symlink())
                    self.assertFalse(Path(os.readlink(link)).is_absolute())
                self.assertEqual((runtime / 'book.toml').resolve(), paths.config_file)
                self.assertEqual((runtime / 'docs/chapter.md').read_text(), 'Original chapter')
            self.assertFalse(runtime.exists())
        self.assertEqual(originals, {p: p.read_bytes() for p in originals})
        with staged_book(read_book_paths(self.book / 'book.toml')) as runtime:
            self.assertEqual(runtime, self.book)

    def test_compose_forwards_build_directory_override(self):
        compose = runner.COMPOSE_FILE.read_text()
        self.assertIn('MDBOOK_BUILD__BUILD_DIR: ${MDBOOK_BUILD__BUILD_DIR:', compose)

    def test_staging_cleans_up_on_failure(self):
        from book_runtime import staged_book
        paths = self.alternate_paths()
        with self.assertRaisesRegex(RuntimeError, 'symbolic links'):
            with patch.object(Path, 'symlink_to', side_effect=OSError('not supported')):
                with staged_book(paths):
                    self.fail('staging should fail')
        self.assertEqual(list(paths.output_root.iterdir()), [])
        with self.assertRaisesRegex(ValueError, 'command failed'):
            with staged_book(paths) as runtime:
                raise ValueError('command failed')
        self.assertFalse(runtime.exists())

    def test_alternate_commands_use_live_staging_and_original_config(self):
        paths = self.alternate_paths()
        originals = {p: p.read_bytes() for p in self.book.rglob('*') if p.is_file()}
        runtimes = []

        def check_native(command, *, cwd, env=None):
            if command[0] == '/tools/mdbook':
                runtimes.append(cwd)
                self.assertEqual((cwd / 'book.toml').resolve(), paths.config_file)
                self.assertEqual(json.loads(env['MDBOOK_BUILD__BUILD_DIR']), str(paths.build_dir))
            else:
                self.assertEqual(command[-1], str(paths.config_file))
                self.assertEqual(cwd, self.root)
                self.assertTrue(runtimes[-1].exists())
            return 0

        def check_docker(command, *, cwd, env=None):
            if command[0] == '/tools/docker':
                runtime = self.root / Path(env['DOCS_BOOK_ROOT']).relative_to('/book')
                runtimes.append(runtime)
                self.assertEqual((runtime / 'book.toml').resolve(), paths.config_file)
                self.assertEqual(json.loads(env['MDBOOK_BUILD__BUILD_DIR']), '/book/architecture book/build/user')
                self.assertEqual(cwd, self.root)
            else:
                self.assertEqual(command[-1], str(paths.config_file))
                self.assertEqual(cwd, self.root)
                self.assertTrue(runtimes[-1].exists())
            return 0

        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None) as prepare:
            for mode, check in ((runner.native_command, check_native), (runner.docker_command, check_docker)):
                with patch.object(runner, 'run', side_effect=check), \
                        patch.object(runner, 'serve_process', side_effect=lambda command, **kw: check(command, cwd=kw['cwd'], env=kw['env'])):
                    for action in ('build', 'serve'):
                        self.assertEqual(mode(action, paths, 3000, False), 0)
                        self.assertEqual(prepare.call_args.args[0], paths.config_file)
                        self.assertTrue(all(not runtime.exists() for runtime in runtimes))
        self.assertEqual(originals, {p: p.read_bytes() for p in originals})

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
