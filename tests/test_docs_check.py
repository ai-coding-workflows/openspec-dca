import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'src/schemas/helper-packs/docs/docs-check.py'


class DocsCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location('project_docs_check', SCRIPT)
        self.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.tool)

    def book(self, name='book.toml', source='text', output='build/site'):
        (self.root / source).mkdir(exist_ok=True)
        (self.root / source / 'SUMMARY.md').write_text('- [Page](page.md)\n')
        (self.root / source / 'page.md').write_text('# Page\n')
        (self.root / name).write_text(f'[book]\nsrc="{source}"\n[build]\nbuild-dir="{output}"\n')

    def helper(self):
        shutil.copytree(ROOT / 'src/schemas/ddd/helpers', self.root / 'openspec/ddd',
                        ignore=shutil.ignore_patterns('__pycache__'))

    def test_source_only_without_books_or_ddd_is_read_only(self):
        with patch.object(self.tool, 'run_step') as run:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only']), 0)
        run.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_configured_book_sources_are_checked_before_build(self):
        self.book()
        (self.root / 'text/page.md').write_text('[Broken](missing.md)\n')
        with patch.object(self.tool, 'run_step') as run:
            self.assertEqual(self.tool.main(['--root', str(self.root)]), 1)
        run.assert_not_called()

    def test_explicit_sources_work_without_a_book(self):
        (self.root / 'notes').mkdir()
        (self.root / 'notes/page.md').write_text('[Broken](missing.md)\n')
        self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only', '--source', 'notes']), 1)

    def test_source_only_does_not_build_or_validate_html(self):
        self.book()
        with patch.object(self.tool, 'run_step') as run, patch.object(self.tool.references, 'validate_html') as html:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only']), 0)
        run.assert_not_called()
        html.assert_not_called()

    def test_ddd_validation_is_optional_and_precedes_build(self):
        self.book()
        self.helper()
        with patch.object(self.tool, 'run_step', return_value=7) as run:
            self.assertEqual(self.tool.main(['--root', str(self.root)]), 7)
        self.assertEqual(len(run.call_args_list), 1)
        self.assertIn(str(self.root / 'openspec/ddd/check.py'), run.call_args.args[0])

    def test_multiple_books_build_once_then_check_every_output(self):
        self.book()
        self.book('book.user.toml', 'user-text', 'build/user')
        with patch.object(self.tool, 'run_step', return_value=0) as run, patch.object(self.tool.references, 'validate_html') as html:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--docker']), 0)
        command = run.call_args.args[0]
        self.assertIn('--docker', command)
        self.assertEqual(command[1], str(ROOT / 'scripts/md-book-builder/book.py'))
        self.assertEqual(command[command.index('--root') + 1], str(self.root))
        self.assertEqual(command[-3:], ['build', '--format', 'markdown'])
        self.assertEqual([call.args[0] for call in html.call_args_list],
                         [self.root / 'build/site', self.root / 'build/user'])

    def test_relocated_builder_override_imports_and_builds_selected_library(self):
        self.book()
        builder = self.root / 'tools/docs/md-book-builder'
        shutil.copytree(ROOT / 'scripts/md-book-builder', builder,
                        ignore=shutil.ignore_patterns('.cache', '.venv', '__pycache__'))
        with patch.object(self.tool, 'run_step', return_value=0) as run:
            # The selected checker reports a distinct success marker, proving its import.
            with (builder / 'check.py').open('a') as target:
                target.write('\nvalidate_html = lambda output: print("relocated HTML checker")\n')
            self.assertEqual(self.tool.main(['--root', str(self.root), '--builder',
                                             str(builder / 'book.py')]), 0)
        self.assertEqual(run.call_args.args[0][1], str(builder / 'book.py'))
        self.assertEqual(Path(self.tool.references.__file__), builder / 'check.py')
        self.assertEqual(run.call_args.args[0][2:4], ['--root', str(self.root)])

    def test_relocated_docs_checker_subprocess_with_explicit_builder(self):
        self.book()
        builder = self.root / 'tools/docs/md-book-builder'
        shutil.copytree(ROOT / 'scripts/md-book-builder', builder,
                        ignore=shutil.ignore_patterns('.cache', '.venv', '__pycache__'))
        # A distinct selected API proves original-location cached modules are not reused.
        with (builder / 'book_selection.py').open('a') as target:
            target.write('\n_original_select_books = select_books\n'
                         'def select_books(*args, **kwargs):\n'
                         '    print("relocated selection API")\n'
                         '    return _original_select_books(*args, **kwargs)\n')
        checker = self.root / 'tools/docs-check.py'
        shutil.copyfile(SCRIPT, checker)
        with tempfile.TemporaryDirectory() as outside:
            result = subprocess.run([sys.executable, str(checker), '--builder',
                                     str(builder / 'book.py'), '--source-only'], cwd=outside,
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('sources verified', result.stdout)
        self.assertIn('relocated selection API', result.stdout)

    def test_build_forwards_custom_mapping(self):
        self.book()
        mapping = self.root / 'custom.toml'
        mapping.write_text('[books.main]\nconfig="book.toml"\nmermaid=false\nsvgbob=true\n')
        with patch.object(self.tool, 'run_step', return_value=0) as run, \
                patch.object(self.tool.references, 'validate_html'):
            self.assertEqual(self.tool.main(['--root', str(self.root), '--config',
                                             str(mapping), '--book', 'main']), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index('--config') + 1], str(mapping))
        self.assertEqual(command[command.index('--book') + 1], 'main')

    def test_shell_starter_builder_environment_and_forwarding(self):
        if os.name != 'posix':
            self.skipTest('POSIX shell starter')
        builder = self.root / 'tools/docs/md-book-builder'
        builder.mkdir(parents=True)
        script = builder / 'book.py'
        script.write_text('import sys; print(repr(sys.argv[1:]))\n')
        result = subprocess.run([str(ROOT / 'scripts/book.sh'), '--root', str(self.root),
                                 '--book', 'alias with space', 'build'],
                                env={**os.environ, 'BOOK_BUILDER': str(script)},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("'alias with space'", result.stdout)
        self.assertIn("'--root'", result.stdout)

    def test_builder_environment_override_for_source_only(self):
        self.book()
        with patch.dict(os.environ, {'BOOK_BUILDER': str(ROOT / 'scripts/md-book-builder/book.py')}):
            args = self.tool.parse_args(['--root', str(self.root), '--source-only'])
        self.assertEqual(args.builder, ROOT / 'scripts/md-book-builder/book.py')

    def test_installed_schema_helper_is_discovered_without_standalone_copy(self):
        destination = self.root / 'openspec/schemas/custom-schema/helpers'
        shutil.copytree(ROOT / 'src/schemas/ddd/helpers', destination,
                        ignore=shutil.ignore_patterns('__pycache__'))
        with patch.object(self.tool, 'run_step', return_value=0) as run:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only']), 0)
        self.assertEqual(run.call_args.args[0][1], str(destination / 'check.py'))

    def test_multiple_installed_schema_helpers_require_explicit_selection(self):
        for name in ('first', 'second'):
            helper = self.root / 'openspec/schemas' / name / 'helpers/check.py'
            helper.parent.mkdir(parents=True)
            helper.write_text('print("selected")\n')
        with patch.object(self.tool, 'run_step', return_value=0) as run:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only']), 1)
            run.assert_not_called()
            selected = 'openspec/schemas/second/helpers/check.py'
            self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only', '--ddd-helper', selected]), 0)
        self.assertEqual(run.call_args.args[0][1], str(self.root / selected))

    def test_distributed_docs_helper_infers_root_and_uses_sibling_ddd_check(self):
        destination = self.root / 'openspec/schemas/openspec/helpers'
        shutil.copytree(ROOT / 'src/schemas/ddd/helpers', destination,
                        ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(SCRIPT, destination / 'docs-check.py')
        with tempfile.TemporaryDirectory() as outside:
            result = subprocess.run([sys.executable, str(destination / 'docs-check.py'), '--source-only',
                                     '--builder', str(ROOT / 'scripts/md-book-builder/book.py')],
                                    cwd=outside, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"status": "skipped"', result.stdout)
        self.assertFalse(list(destination.glob('__pycache__')))

    def test_missing_requested_ddd_helper_is_an_error(self):
        self.assertEqual(self.tool.main(['--root', str(self.root), '--source-only', '--catalog', 'custom.json']), 1)

    def test_native_openspec_is_explicit_and_failure_stops_build(self):
        self.book()
        with patch.object(self.tool.shutil, 'which', return_value='/tools/openspec'), \
                patch.dict('os.environ', {}, clear=True), patch.object(self.tool, 'run_step', return_value=9) as run:
            self.assertEqual(self.tool.main(['--root', str(self.root), '--openspec']), 9)
        self.assertEqual(run.call_args.args[0], ['/tools/openspec', 'validate', '--all', '--strict', '--no-interactive'])

    def test_legacy_entry_help_has_no_model_import(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/docs.py'), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--source-only', result.stdout)


if __name__ == '__main__':
    unittest.main()
