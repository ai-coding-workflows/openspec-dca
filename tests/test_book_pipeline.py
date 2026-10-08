"""Common exports capture mdBook once and never fall back to raw sources."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
spec = importlib.util.spec_from_file_location('pipeline_book_runner', ROOT / 'scripts/md-book-builder/book.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PipelineDispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'book.user.toml'
        self.config.write_text('[book]\ntitle="Pipeline"\nsrc="src"\n'
                               '[build]\nbuild-dir="build/user/site"\n')
        (self.root / 'src').mkdir()
        self.paths = runner.read_book_paths(self.config)
        self.calls = []
        self.contexts = []

    def run_command(self, command, *, cwd, env=None):
        self.calls.append((command, cwd, env))
        if command[0] == '/tools/mdbook' and '--dest-dir' in command:
            destination = Path(command[command.index('--dest-dir') + 1])
            self.assertEqual(list(json.loads(env['MDBOOK_OUTPUT'])), ['book-export'])
            self.assertEqual(env['MDBOOK_BUILD__CREATE_MISSING'], 'false')
            self.write_context(destination)
        elif command[0] == '/tools/docker' and '-e' in command:
            value = command[command.index('-e') + 1]
            self.assertEqual(list(json.loads(value.split('=', 1)[1])), ['book-export'])
            self.assertIn('/book-export/output', command)
            self.assertIn('MDBOOK_BUILD__CREATE_MISSING=false', command)
            self.write_context(Path(env['DOCS_EXPORT_HOST']) / 'output')
        elif command[0] == sys.executable:
            context = Path(command[command.index('--render-context') + 1])
            self.assertTrue(context.is_file())
            self.contexts.append(context)
            self.assertEqual(command[-1], str(self.config))
        return 0

    def write_context(self, destination):
        destination.mkdir(parents=True, exist_ok=True)
        (destination / 'render-context.json').write_text(json.dumps({'book': {'items': [
            {'Chapter': {'name': 'Generated', 'path': 'virtual.md',
                         'content': '# Generated', 'sub_items': []}}]}}))

    def execute(self, command, action):
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None), \
                patch.object(runner, 'run', side_effect=self.run_command):
            return command(action, self.paths, None, False, output_formats=('markdown', 'typst'))

    def assert_shared_context_cleaned(self):
        self.assertEqual(len(self.contexts), 2)
        self.assertEqual(self.contexts[0], self.contexts[1])
        self.assertFalse(self.contexts[0].exists())
        self.assertFalse(self.contexts[0].parent.parent.exists())

    def test_native_build_captures_once_and_builds_html_once(self):
        self.assertEqual(self.execute(runner.native_command, 'build'), 0)
        builds = [command for command, _, _ in self.calls if command[0] == '/tools/mdbook']
        self.assertEqual(len(builds), 2)
        self.assertEqual(sum('--dest-dir' not in command for command in builds), 1)
        self.assert_shared_context_cleaned()

    def test_export_does_not_replace_existing_html_or_original_config(self):
        self.paths.build_dir.mkdir(parents=True)
        html = self.paths.build_dir / 'existing.html'
        html.write_text('Keep existing HTML')
        original = self.config.read_bytes()
        self.assertEqual(self.execute(runner.native_command, 'export'), 0)
        builds = [command for command, _, _ in self.calls if command[0] == '/tools/mdbook']
        self.assertEqual(len(builds), 1)
        self.assertIn('--dest-dir', builds[0])
        self.assertEqual(html.read_text(), 'Keep existing HTML')
        self.assertEqual(self.config.read_bytes(), original)
        self.assert_shared_context_cleaned()

    def test_docker_export_captures_in_container_but_exports_on_host(self):
        self.assertEqual(self.execute(runner.docker_command, 'export'), 0)
        docker_calls = [command for command, _, _ in self.calls if command[0] == '/tools/docker']
        self.assertEqual(len(docker_calls), 2)  # Image build and isolated capture.
        self.assertTrue(any('-e' in command for command in docker_calls))
        self.assert_shared_context_cleaned()

    def test_docker_build_has_one_html_build_and_one_capture(self):
        self.assertEqual(self.execute(runner.docker_command, 'build'), 0)
        runs = [command for command, _, _ in self.calls if command[0] == '/tools/docker' and 'run' in command]
        self.assertEqual(len(runs), 2)
        self.assertEqual(sum('-e' not in command for command in runs), 1)
        self.assert_shared_context_cleaned()

    def test_pipeline_failure_never_runs_raw_export(self):
        with patch.object(runner.shutil, 'which', side_effect=lambda name: '/tools/' + name), \
                patch.object(runner, 'prepare_svgbob', return_value=None), \
                patch.object(runner, 'run', return_value=4) as run:
            with self.assertRaises(RuntimeError):
                runner.native_command('export', self.paths, None, False)
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][0], '/tools/mdbook')

    def test_failed_book_capture_does_not_skip_remaining_books(self):
        (self.root / 'book.toml').write_text('[book]\nsrc="src"\n[build]\nbuild-dir="build/main"\n')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(sys, 'argv', ['book.py', 'export']), \
                patch.object(runner, 'native_command', side_effect=[runner.BookCaptureError('failed'), 0]) as run:
            self.assertEqual(runner.main(), 1)
        self.assertEqual(run.call_count, 2)

    def test_docker_export_is_a_valid_cli_action(self):
        with patch.object(sys, 'argv', ['book.py', '--docker', 'export']):
            args = runner.parse_args()
        self.assertTrue(args.docker)
        self.assertEqual(args.action, 'export')
