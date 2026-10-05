"""Root discovery, batch dispatch, and preview supervision."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book'))
from book_discovery import discover_books, validate_outputs
from book_paths import read_book_paths
import book_servers

spec = importlib.util.spec_from_file_location('batch_docs_runner', ROOT / 'scripts/md-book/docs.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config(self, name, output):
        target = self.root / name
        target.write_text(f'[book]\nsrc="docs"\n[build]\nbuild-dir="{output}"\n')
        return target

    def test_root_only_and_stable_order(self):
        primary = self.config('book.toml', 'build/main/site')
        user = self.config('user.book.toml', 'build/user/site')
        admin = self.config('admin.book.toml', 'build/admin/site')
        self.config('other.toml', 'build/other/site')
        nested = self.root / 'nested'
        nested.mkdir()
        (nested / 'book.toml').write_text('[book]')
        self.assertEqual(discover_books(self.root), [primary, admin, user])
        self.assertEqual(discover_books(self.root, 'user.book.toml'), [user])

    def test_alternate_only_and_missing(self):
        with self.assertRaisesRegex(ValueError, 'No book.toml'):
            discover_books(self.root)
        user = self.config('user.book.toml', 'build/user/site')
        self.assertEqual(discover_books(self.root), [user])

    def test_conflicting_outputs_but_shared_tool_cache_allowed(self):
        primary = self.config('book.toml', 'build/main/site')
        for output in ('build/main/site', 'build/main/site/nested', 'build/main'):
            user = self.config('user.book.toml', output)
            with self.assertRaisesRegex(ValueError, 'Conflicting output'):
                validate_outputs([read_book_paths(primary), read_book_paths(user)])
        user = self.config('user.book.toml', 'build/main/other')
        validate_outputs([read_book_paths(primary), read_book_paths(user)])

    def test_build_all_continues_after_failure_and_explicit_selects_one(self):
        primary = self.config('book.toml', 'build/main/site')
        user = self.config('user.book.toml', 'build/user/site')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner, 'native_command', side_effect=[1, 0]) as command, \
                patch.object(sys, 'argv', ['docs.py', 'build']):
            self.assertEqual(runner.main(), 1)
            self.assertEqual([c.args[1].config_file for c in command.call_args_list], [primary, user])
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner, 'native_command', return_value=0) as command, \
                patch.object(sys, 'argv', ['docs.py', '--book', 'user.book.toml', 'build']):
            self.assertEqual(runner.main(), 0)
            command.assert_called_once()
            self.assertEqual(command.call_args.args[1].config_file, user)

    def test_serve_all_assigns_distinct_ports(self):
        primary = self.config('book.toml', 'build/main/site')
        user = self.config('user.book.toml', 'build/user/site')
        with patch.object(runner, 'REPOSITORY', self.root), \
                patch.object(runner, 'free_port', side_effect=[3002, 3002, 4000]), \
                patch.object(runner, 'serve_books', return_value=130) as serve, \
                patch.object(sys, 'argv', ['docs.py', '--docker', '--port', '3002', '--no-open', 'serve']):
            self.assertEqual(runner.main(), 130)
            self.assertEqual(serve.call_args.args[1:], ([primary, user], [3002, 4000]))
            self.assertEqual(serve.call_args.kwargs, {'docker': True, 'open_browser': False})

    def test_supervisor_interrupt_stops_every_child(self):
        children = [Mock(), Mock()]
        for child in children:
            child.poll.return_value = None
        response = Mock()
        response.__enter__ = Mock(return_value=Mock(status=200))
        response.__exit__ = Mock(return_value=False)
        with patch.object(book_servers.subprocess, 'Popen', side_effect=children) as launch, \
                patch.object(book_servers.urllib.request, 'urlopen', return_value=response), \
                patch.object(book_servers.time, 'sleep', side_effect=KeyboardInterrupt), \
                patch.object(book_servers, 'stop_servers') as stop:
            result = book_servers.serve_books(Path('docs.py'), [Path('book.toml'), Path('user.book.toml')],
                                              [3002, 4000], docker=True, open_browser=False)
            self.assertEqual(result, 130)
            self.assertEqual(launch.call_count, 2)
            self.assertIn('--docker', launch.call_args.args[0])
            stop.assert_called_once_with(children)

    def test_supervisor_failure_stops_started_children(self):
        child = Mock()
        child.poll.return_value = 7
        child.returncode = 7
        with patch.object(book_servers.subprocess, 'Popen', return_value=child), \
                patch.object(book_servers, 'stop_servers') as stop:
            self.assertEqual(book_servers.serve_books(Path('docs.py'), [Path('book.toml')],
                                                       [3002], docker=False, open_browser=False), 7)
            stop.assert_called_once_with([child])
