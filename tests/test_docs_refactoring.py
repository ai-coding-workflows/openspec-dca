"""Regression checks for documentation runner failure and cleanup paths."""

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
spec = importlib.util.spec_from_file_location('refactored_docs', ROOT / 'scripts/md-book-builder/book.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerFailureTests(unittest.TestCase):
    def serve(self, process, **kwargs):
        with patch.object(runner.subprocess, 'Popen', return_value=process):
            return runner.serve_process(['mdbook', 'serve'], cwd=ROOT, env=None,
                                        port=3000, open_browser=False, **kwargs)

    def test_exited_server_preserves_failure_code(self):
        process = Mock(returncode=7)
        process.poll.return_value = 7
        self.assertEqual(self.serve(process), 7)
        process.terminate.assert_not_called()

    def test_readiness_timeout_escalates_to_kill(self):
        process = Mock()
        process.wait.side_effect = [subprocess.TimeoutExpired('mdbook', 5), 0]
        with patch.object(runner.time, 'monotonic', side_effect=[0, 61]):
            self.assertEqual(self.serve(process), 1)
        process.terminate.assert_called_once()
        process.kill.assert_called_once()
        self.assertEqual(process.wait.call_count, 2)

    def test_interrupt_stops_running_server(self):
        process = Mock()
        process.poll.return_value = None
        with patch.object(runner, 'wait_for_server', side_effect=KeyboardInterrupt):
            self.assertEqual(self.serve(process), 130)
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=5)

    def test_ready_server_waits_for_exit(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.return_value = 0
        response = Mock()
        response.__enter__ = Mock(return_value=SimpleNamespace(status=200))
        response.__exit__ = Mock(return_value=False)
        with patch.object(runner.urllib.request, 'urlopen', return_value=response):
            self.assertEqual(self.serve(process), 0)
        process.wait.assert_called_once_with()
        process.terminate.assert_not_called()

    def test_download_error_and_invalid_result(self):
        paths = SimpleNamespace(output_root=ROOT / 'build')
        for result, expected in ((SimpleNamespace(returncode=9, stdout='out', stderr='err'), 9),
                                 (SimpleNamespace(returncode=0, stdout='invalid', stderr=''), 1),
                                 (SimpleNamespace(returncode=0, stdout='{}', stderr=''), 1)):
            with self.subTest(result=result), patch.object(runner.subprocess, 'run', return_value=result):
                self.assertEqual(runner.download_native_tools(paths, {}, ['mdbook']), expected)

    def test_download_keeps_path_tools(self):
        paths = SimpleNamespace(output_root=ROOT / 'build', config_file=ROOT / 'book.toml')
        result = SimpleNamespace(returncode=0, stdout='log\n{"mdbook": "/cache/mdbook"}', stderr='')
        with patch.object(runner.shutil, 'which', side_effect=[None, '/path/mermaid']), \
                patch.object(runner.subprocess, 'run', return_value=result):
            commands, status = runner.native_toolchain(paths)
        self.assertEqual(status, 0)
        self.assertEqual(commands, {'mdbook': '/cache/mdbook', 'mdbook-mermaid': '/path/mermaid'})
