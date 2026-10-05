"""Exercise multi-book execution with real native tools in temporary repositories."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TOOLS_AVAILABLE = all(shutil.which(tool) for tool in ('mdbook', 'mdbook-mermaid', 'uv'))


@unittest.skipUnless(TOOLS_AVAILABLE and os.name == 'posix',
                     'Native multi-book integration requires mdbook, mdbook-mermaid, uv and POSIX')
class MultiBookIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for tool in ('md-book', 'book-exporter'):
            shutil.copytree(ROOT / 'scripts' / tool, self.root / 'scripts' / tool,
                            ignore=shutil.ignore_patterns('__pycache__', '.venv'))
        self.script = self.root / 'scripts/md-book/docs.py'
        self.configs = {}
        for config, title, source, output in (
                ('book.toml', 'Architecture', 'architecture', 'build/main/site'),
                ('user.book.toml', 'User Guide', 'user-guide', 'build/user/site')):
            directory = self.root / source
            directory.mkdir()
            (directory / 'SUMMARY.md').write_text('# Summary\n\n- [Intro](intro.md)\n')
            (directory / 'intro.md').write_text(f'# {title}\n\nOriginal content.\n')
            path = self.root / config
            path.write_text(f'[book]\ntitle="{title}"\nsrc="{source}"\n'
                            f'[build]\nbuild-dir="{output}"\n')
            self.configs[path] = path.read_bytes()

    def test_builds_and_exports_both_without_replacing_configs(self):
        result = subprocess.run([sys.executable, str(self.script), 'build'],
                                text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for output, title in (('build/main/site', 'Architecture'), ('build/user/site', 'User Guide')):
            directory = self.root / output
            self.assertIn(title, (directory / 'intro.html').read_text())
            self.assertTrue(list(directory.glob('*.md')))
        for path, contents in self.configs.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_alternate_top_level_output_does_not_delete_runtime(self):
        config = self.root / 'user.book.toml'
        config.write_text(config.read_text().replace('build/user/site', 'user-book'))
        result = subprocess.run([sys.executable, str(self.script), '--book', str(config), 'build'],
                                text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('User Guide', (self.root / 'user-book/intro.html').read_text())
        self.assertFalse(list(self.root.glob('mdbook-runtime-*')))

    def wait_for(self, predicate, process, log):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            self.assertIsNone(process.poll(), log.read_text())
            if predicate():
                return
            time.sleep(0.1)
        self.fail(log.read_text())

    def test_serves_both_reloads_and_cleans_up_on_interrupt(self):
        log = self.root / 'serve.log'
        with log.open('w') as stream:
            process = subprocess.Popen([sys.executable, str(self.script), '--no-open', 'serve'],
                                       stdout=stream, stderr=stream, start_new_session=True)
            try:
                def urls():
                    return [line.split(': ', 1)[1] for line in log.read_text().splitlines()
                            if line.startswith(('book.toml: http', 'user.book.toml: http'))]
                self.wait_for(lambda: len(urls()) == 2, process, log)
                sites = urls()
                self.assertEqual(len(set(sites)), 2)
                for site in sites:
                    with urllib.request.urlopen(site, timeout=2) as response:
                        self.assertEqual(response.status, 200)
                (self.root / 'user-guide/intro.md').write_text('# User Guide\n\nUpdated preview text.\n')

                def updated():
                    try:
                        with urllib.request.urlopen(sites[1] + 'intro.html', timeout=2) as response:
                            return 'Updated preview text' in response.read().decode()
                    except (OSError, urllib.error.HTTPError):
                        return False  # Rebuilding temporarily removes the old HTML.

                self.wait_for(updated, process, log)
                config = self.root / 'user.book.toml'
                config.write_text(config.read_text().replace('User Guide', 'Revised Guide'))

                def config_updated():
                    try:
                        with urllib.request.urlopen(sites[1] + 'intro.html', timeout=2) as response:
                            return 'Revised Guide' in response.read().decode()
                    except OSError:
                        return False

                self.wait_for(config_updated, process, log)
                process.send_signal(signal.SIGINT)
                self.assertEqual(process.wait(timeout=15), 130, log.read_text())
                self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))
                for site in sites:
                    with self.assertRaises(OSError):
                        urllib.request.urlopen(site, timeout=1)
            finally:
                if process.poll() is None:
                    process.send_signal(signal.SIGINT)
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
