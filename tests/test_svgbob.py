import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))


class SvgbobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import svgbob
        cls.tool = svgbob

    def test_absent_configuration_does_not_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / 'book.toml'
            book.write_text('[book]\ntitle = "Test"\n')
            with mock.patch.object(self.tool, 'install') as install:
                self.assertIsNone(self.tool.prepare(book, Path(tmp)))
                install.assert_not_called()

    def test_custom_command_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / 'book.toml'
            book.write_text('[preprocessor.svgbob]\ncommand = "custom-svgbob"\n')
            with mock.patch.object(self.tool, 'install') as install:
                self.assertIsNone(self.tool.prepare(book, Path(tmp)))
                install.assert_not_called()

    def test_host_targets(self):
        for system, machine, target in (
            ('linux', 'x86_64', 'x86_64-unknown-linux-musl'),
            ('linux', 'arm64', 'aarch64-unknown-linux-musl'),
            ('win32', 'AMD64', 'x86_64-pc-windows-gnu'),
        ):
            with mock.patch.object(self.tool.sys, 'platform', system), mock.patch.object(
                self.tool.platform, 'machine', return_value=machine
            ):
                self.assertEqual(self.tool.host_target()[0], target)
        with mock.patch.object(self.tool.sys, 'platform', 'darwin'):
            with self.assertRaisesRegex(RuntimeError, 'macOS'):
                self.tool.host_target()

    def test_cleanup_after_build_failure(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            if command[1] == 'start':
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0, stdout='')
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.tool.shutil, 'which', return_value='/usr/bin/docker'
        ), mock.patch.object(self.tool.subprocess, 'run', side_effect=run):
            with self.assertRaises(subprocess.CalledProcessError):
                self.tool.install(Path(tmp), 'x86_64-unknown-linux-musl', 'linux/amd64')
        self.assertTrue(any(c[1:3] == ['rm', '--force'] for c in calls))
        self.assertTrue(any(c[1:3] == ['image', 'rm'] for c in calls))

    def test_cached_binary_avoids_docker(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = self.tool.destination(Path(tmp), 'x86_64-unknown-linux-musl')
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b'binary')
            with mock.patch.object(self.tool, 'valid_binary', return_value=True), mock.patch.object(
                self.tool.subprocess, 'run'
            ) as run:
                self.assertEqual(self.tool.install(Path(tmp), 'x86_64-unknown-linux-musl', 'linux/amd64'), binary)
                run.assert_not_called()

    def test_enabled_configuration_uses_path_without_docker(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / 'book.toml'
            book.write_text('[preprocessor.svgbob]\n')
            with mock.patch.object(self.tool.shutil, 'which', return_value='/tools/mdbook-svgbob'), mock.patch.object(
                self.tool, 'install'
            ) as install:
                self.assertEqual(self.tool.prepare(book, Path(tmp)), Path('/tools/mdbook-svgbob'))
                install.assert_not_called()

    def test_failed_container_exit_does_not_copy_binary(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, stdout='1' if command[1] == 'inspect' else '')
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.tool.shutil, 'which', return_value='/usr/bin/docker'
        ), mock.patch.object(self.tool.subprocess, 'run', side_effect=run):
            with self.assertRaisesRegex(RuntimeError, 'compilation failed'):
                self.tool.install(Path(tmp), 'x86_64-unknown-linux-musl', 'linux/amd64')
        self.assertFalse(any(c[1] == 'cp' for c in calls))
        self.assertTrue(any(c[1:3] == ['image', 'rm'] for c in calls))

    def test_success_publishes_verified_executable_and_cleans_up(self):
        calls = []
        def run(command, **kwargs):
            calls.append(command)
            if command[1] == 'cp':
                Path(command[-1]).write_bytes(b'executable')
            return subprocess.CompletedProcess(command, 0, stdout='0' if command[1] == 'inspect' else '')
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.tool.shutil, 'which', return_value='/usr/bin/docker'
        ), mock.patch.object(self.tool.subprocess, 'run', side_effect=run):
            binary = self.tool.install(Path(tmp), 'x86_64-unknown-linux-musl', 'linux/amd64')
            self.assertTrue(self.tool.valid_binary(binary))
            binary.write_bytes(b'corrupt')
            self.assertFalse(self.tool.valid_binary(binary))
        self.assertTrue(any(c[1:3] == ['rm', '--force'] for c in calls))
        self.assertTrue(any(c[1:3] == ['image', 'rm'] for c in calls))

    def test_real_preprocessor_renders_bob_fence_when_available(self):
        mdbook = shutil.which('mdbook')
        cache = ROOT / 'scripts/md-book-builder/.cache/native-tools'
        try:
            binary = self.tool.destination(cache, self.tool.host_target()[0])
        except RuntimeError:
            binary = None
        if not mdbook or not (shutil.which('mdbook-svgbob') or (binary and self.tool.valid_binary(binary))):
            self.skipTest('Provide mdbook and a PATH or cached svgbob binary for rendering integration')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'book.toml').write_text('[book]\ntitle = "Svgbob test"\n[preprocessor.svgbob]\n')
            (root / 'src/SUMMARY.md').write_text('# Summary\n\n- [Diagram](diagram.md)\n')
            (root / 'src/diagram.md').write_text('# Diagram\n\n```bob\n+-----+\n| Test|\n+-----+\n```\n')
            executable = self.tool.prepare(root / 'book.toml', cache)
            env = dict(os.environ, PATH=str(executable.parent) + os.pathsep + os.environ.get('PATH', ''))
            result = subprocess.run([mdbook, 'build'], cwd=root, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (root / 'book/diagram.html').read_text()
            self.assertIn('<svg', html)
            self.assertNotIn('class="language-bob"', html)
