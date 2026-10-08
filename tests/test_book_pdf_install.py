"""The common CLI isolates PDF dependencies without affecting other exports."""

from contextlib import nullcontext
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
spec = importlib.util.spec_from_file_location('pdf_install_runner', ROOT / 'scripts/md-book-builder/book.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PdfInstallDispatchTests(unittest.TestCase):
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
        self.config = self.root / 'book.toml'
        self.config.write_text('[book]\ntitle="PDF Guide"\nsrc="src"\n'
                               '[build]\nbuild-dir="build/site"\n')
        self.managed_python = self.root / 'managed/bin/python'

    def invoke(self, *args):
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(sys, 'argv', ['book.py', *args]):
            return runner.main()

    def test_pdf_uses_exclusively_managed_python(self):
        with patch.object(runner, 'ensure_pdf_python', create=True, return_value=self.managed_python) as prepare, \
                patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export', '--format', 'pdf'), 0)
        prepare.assert_called_once_with(runner.SCRIPT_DIR, allow_install=True)
        self.assertEqual(run.call_args.args[0][0], str(self.managed_python))

    def test_no_install_allows_managed_cache_reuse(self):
        with patch.object(runner, 'ensure_pdf_python', create=True, return_value=self.managed_python) as prepare, \
                patch.object(runner, 'run', return_value=0):
            self.assertEqual(self.invoke('export', '--format', 'pdf', '--no-install'), 0)
        prepare.assert_called_once_with(runner.SCRIPT_DIR, allow_install=False)

    def test_markdown_and_typst_never_prepare_pdf_environment(self):
        with patch.object(runner, 'ensure_pdf_python', create=True) as prepare, \
                patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export', '--format', 'markdown', '--format', 'typst'), 0)
        prepare.assert_not_called()
        self.assertTrue(all(call.args[0][0] == sys.executable for call in run.call_args_list))

    def test_setup_failure_is_reported_and_other_formats_continue(self):
        def failure(*args, **kwargs):
            raise runner.PdfEnvironmentError('PDF setup failed')
        with patch.object(runner, 'ensure_pdf_python', create=True, side_effect=failure), \
                patch.object(runner, 'run', return_value=0) as run:
            self.assertEqual(self.invoke('export', '--format', 'pdf', '--format', 'markdown'), 2)
        run.assert_called_once()
        self.assertIn('markdown', run.call_args.args[0])

    def test_builds_forward_no_install_to_pdf_setup(self):
        paths = runner.read_book_paths(self.config)
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None), \
                patch.object(runner, 'ensure_pdf_python', create=True, return_value=self.managed_python) as prepare, \
                patch.object(runner, 'run', return_value=0):
            for command in (runner.native_command, runner.docker_command):
                with self.subTest(mode=command.__name__):
                    self.assertEqual(command('build', paths, None, False,
                                             output_formats=('pdf',), allow_install=False), 0)
                    self.assertEqual(prepare.call_args.kwargs, {'allow_install': False})
