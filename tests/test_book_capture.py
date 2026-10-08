"""Offline capture lifecycle and standalone mdBook renderer protocol checks."""

import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'scripts/md-book-builder'
sys.path.insert(0, str(BUILDER))
from book_capture import BookCaptureError, RENDERER_NAME, capture_book, capture_output
from book_paths import BookPaths


class BookCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = BookPaths(self.root, self.root / 'build/site',
                               self.root / 'build', self.root / 'book.toml')
        self.destination = None

    def launch_context(self, context):
        def launch(destination):
            self.destination = destination
            self.assertFalse(destination.exists())
            destination.mkdir()
            (destination / 'render-context.json').write_text(
                json.dumps(context, ensure_ascii=False), encoding='utf-8')
            return 0
        return launch

    def assert_cleaned(self):
        self.assertIsNotNone(self.destination)
        self.assertFalse(self.destination.parent.exists())

    def test_capture_preserves_full_context_and_lifetime(self):
        context = {'book': {'items': [{'Chapter': {'name': '日本語',
                   'content': '# processed', 'sub_items': []}}, 'Separator']},
                   'config': {'book': {'title': 'Guide'}}, 'extra': [1, 2]}
        with capture_book(self.paths, self.launch_context(context)) as captured:
            self.assertEqual(captured, self.destination / 'render-context.json')
            self.assertEqual(json.loads(captured.read_text(encoding='utf-8')), context)
            self.assertTrue(captured.exists())
            self.assertFalse(captured.is_relative_to(self.paths.build_dir))
            self.assertEqual(self.destination.parent.parent, self.paths.output_root)
        self.assert_cleaned()

    def test_minimal_tree(self):
        with capture_book(self.paths, self.launch_context({'book': {'items': []}})) as captured:
            self.assertTrue(captured.is_file())
        self.assert_cleaned()

    def test_nonzero_and_missing_context(self):
        for status, message in ((3, 'exit|status'), (0, 'missing|not found')):
            with self.subTest(status=status):
                def launch(destination):
                    self.destination = destination
                    return status
                with self.assertRaisesRegex(BookCaptureError, message):
                    with capture_book(self.paths, launch):
                        self.fail('must not yield')
                self.assert_cleaned()

    def test_malformed_context(self):
        for context in ([], {}, {'book': []}, {'book': {'items': {}}}):
            with self.subTest(context=context):
                with self.assertRaisesRegex(BookCaptureError, 'context|book.items'):
                    with capture_book(self.paths, self.launch_context(context)):
                        self.fail('must not yield')
                self.assert_cleaned()

    def test_invalid_json_and_encoding(self):
        for content in (b'{broken', b'\xff'):
            with self.subTest(content=content):
                def launch(destination):
                    self.destination = destination
                    destination.mkdir()
                    (destination / 'render-context.json').write_bytes(content)
                    return 0
                with self.assertRaisesRegex(BookCaptureError, 'context'):
                    with capture_book(self.paths, launch):
                        self.fail('must not yield')
                self.assert_cleaned()

    def test_startup_failure_is_clear_and_cleans(self):
        def launch(destination):
            self.destination = destination
            raise OSError('mdbook not available')
        with self.assertRaisesRegex(BookCaptureError, 'start|launch'):
            with capture_book(self.paths, launch):
                self.fail('must not yield')
        self.assert_cleaned()

    def test_launch_interrupt_cleans(self):
        def launch(destination):
            self.destination = destination
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            with capture_book(self.paths, launch):
                self.fail('must not yield')
        self.assert_cleaned()

    def test_consumer_exception_and_interrupt_clean(self):
        for exception in (ValueError('export failed'), KeyboardInterrupt()):
            with self.subTest(exception=type(exception)):
                with self.assertRaises(type(exception)):
                    with capture_book(self.paths, self.launch_context({'book': {'items': []}})):
                        raise exception
                self.assert_cleaned()

    def test_top_level_output_uses_sibling_and_preserves_sources(self):
        site = self.root / 'site'
        site.mkdir()
        (site / 'index.html').write_text('maintained output', encoding='utf-8')
        self.paths.config_file.write_text('maintained config', encoding='utf-8')
        source = self.root / 'chapter.md'
        source.write_text('maintained source', encoding='utf-8')
        paths = BookPaths(self.root, site, site, self.paths.config_file)
        with capture_book(paths, self.launch_context({'book': {'items': []}})) as captured:
            self.assertEqual(self.destination.parent.parent, self.root)
            self.assertFalse(captured.is_relative_to(site))
        self.assert_cleaned()
        self.assertEqual((site / 'index.html').read_text(), 'maintained output')
        self.assertEqual(source.read_text(), 'maintained source')
        self.assertEqual(paths.config_file.read_text(), 'maintained config')

    def test_output_override_quotes_command_and_replaces_outputs(self):
        command = ['/path with spaces/python', 'a\'b/capture_backend.py', '--x', '$value']
        value = json.loads(capture_output(command))
        self.assertEqual(RENDERER_NAME, 'book-export')
        self.assertEqual(value, {'book-export': {'command': shlex.join(command)}})
        self.assertEqual(shlex.split(value['book-export']['command']), command)


class CaptureBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name) / 'output'

    def run_backend(self, data):
        return subprocess.run([sys.executable, str(BUILDER / 'capture_backend.py')],
                              input=data, text=True, encoding='utf-8', capture_output=True)

    def test_unicode_and_full_context(self):
        context = {'destination': str(self.destination),
                   'book': {'items': [{'Chapter': {'name': '日本語',
                            'content': 'héllo', 'sub_items': []}}]},
                   'version': '0.5.4', 'config': {'custom': True}}
        result = self.run_backend(json.dumps(context, ensure_ascii=False))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')
        captured = self.destination / 'render-context.json'
        self.assertEqual(json.loads(captured.read_text(encoding='utf-8')), context)
        self.assertIn('日本語', captured.read_text(encoding='utf-8'))
        self.assertEqual(list(self.destination.iterdir()), [captured])

    def test_malformed_input(self):
        for data in ('invalid', '[]', '[{}, {}]', '{}',
                     '{"book":{"items":[]}}',
                     '{"book":{"items":{}},"destination":"ignored"}'):
            with self.subTest(data=data):
                result = self.run_backend(data)
                self.assertEqual(result.returncode, 2)
                self.assertIn('capture', result.stderr.lower())
                self.assertFalse(self.destination.exists())

    def test_write_failure(self):
        self.destination.write_text('not a directory', encoding='utf-8')
        result = self.run_backend(json.dumps({'book': {'items': []},
                                             'destination': str(self.destination)}))
        self.assertEqual(result.returncode, 2)
        self.assertIn('capture', result.stderr.lower())
        self.assertEqual(self.destination.read_text(), 'not a directory')


if __name__ == '__main__':
    unittest.main()
