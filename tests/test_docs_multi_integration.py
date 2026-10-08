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
TOOLS_AVAILABLE = all(shutil.which(tool) for tool in ('mdbook', 'mdbook-mermaid'))


@unittest.skipUnless(TOOLS_AVAILABLE and os.name == 'posix',
                     'Native multi-book integration requires mdbook, mdbook-mermaid and POSIX')
class MultiBookIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'scripts/md-book-builder', self.root / 'scripts/md-book-builder',
                        ignore=shutil.ignore_patterns('__pycache__', '.venv', '.cache'))
        self.script = self.root / 'scripts/md-book-builder/book.py'
        self.configs = {}
        for config, title, source, output in (
                ('book.toml', 'Architecture', 'architecture', 'build/main/site'),
                ('book.user.toml', 'User Guide', 'user-guide', 'build/user/site')):
            directory = self.root / source
            directory.mkdir()
            (directory / 'SUMMARY.md').write_text('# Summary\n\n- [Intro](intro.md)\n')
            (directory / 'intro.md').write_text(f'# {title}\n\nOriginal content.\n')
            path = self.root / config
            path.write_text(f'[book]\ntitle="{title}"\nsrc="{source}"\n'
                            f'[build]\nbuild-dir="{output}"\n')
            self.configs[path] = path.read_bytes()

    def test_builds_and_exports_both_without_replacing_configs(self):
        result = subprocess.run([sys.executable, str(self.script), '--root', str(self.root), 'build'],
                                cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for output, title in (('build/main/site', 'Architecture'), ('build/user/site', 'User Guide')):
            directory = self.root / output
            self.assertIn(title, (directory / 'intro.html').read_text())
            self.assertTrue(list(directory.glob('*.md')))
        for path, contents in self.configs.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_export_only_uses_original_configs_without_html_build(self):
        result = subprocess.run([sys.executable, str(self.script), '--root', str(self.root),
                                 'export', '--format', 'typst'],
                                cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for output, title in (('build/main/site', 'Architecture'), ('build/user/site', 'User Guide')):
            directory = self.root / output
            self.assertIn(title, (directory / f'{title}.typ').read_text())
            self.assertFalse((directory / 'intro.html').exists())
        for path, contents in self.configs.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_multiple_formats_build_and_repeated_cli_override(self):
        (self.root / 'book-builder.toml').write_text(
            '[books.handbook]\nconfig="book.toml"\nexport-formats=["markdown", "typst"]\n'
            '[books.user]\nconfig="book.user.toml"\nexport-format="typst"\n')
        result = subprocess.run([sys.executable, str(self.script), '--root', str(self.root), 'build'],
                                cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        main = self.root / 'build/main/site'
        user = self.root / 'build/user/site'
        self.assertTrue((main / 'intro.html').is_file())
        self.assertTrue((main / 'Architecture.md').is_file())
        self.assertTrue((main / 'Architecture.typ').is_file())
        self.assertTrue((user / 'User Guide.typ').is_file())
        self.assertFalse((user / 'User Guide.md').exists())
        override = subprocess.run([sys.executable, str(self.script), '--root', str(self.root), 'export',
                                   '--format', 'markdown', '--format', 'typst'],
                                  cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(override.returncode, 0, override.stdout + override.stderr)
        self.assertTrue((user / 'User Guide.md').is_file())
        for path, contents in self.configs.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_builder_list_and_configured_format_control_real_build(self):
        (self.root / 'book-builder.toml').write_text(
            '[books.user]\nconfig="book.user.toml"\nexport-format="typst"\nserve=false\n')
        result = subprocess.run([sys.executable, str(self.script), '--root', str(self.root), 'build'],
                                cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = self.root / 'build/user/site'
        self.assertTrue((output / 'intro.html').is_file())
        self.assertTrue((output / 'User Guide.typ').is_file())
        self.assertFalse((output / 'User Guide.md').exists())
        self.assertFalse((self.root / 'build/main/site').exists())
        override = subprocess.run([sys.executable, str(self.script), '--root', str(self.root),
                                    'export', '--format', 'markdown'],
                                  cwd=ROOT, text=True, capture_output=True, timeout=30)
        self.assertEqual(override.returncode, 0, override.stdout + override.stderr)
        self.assertTrue((output / 'User Guide.md').is_file())
        for path, contents in self.configs.items():
            self.assertEqual(path.read_bytes(), contents)
        self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))

    def test_alternate_top_level_output_does_not_delete_runtime(self):
        config = self.root / 'book.user.toml'
        config.write_text(config.read_text().replace('build/user/site', 'user-book'))
        result = subprocess.run([sys.executable, str(self.script), '--root', str(self.root),
                                 '--book', str(config), 'build'],
                                cwd=ROOT, text=True, capture_output=True, timeout=60)
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

    def test_general_serve_filters_but_explicit_disabled_book_can_be_previewed(self):
        (self.root / 'book-builder.toml').write_text(
            '[books.handbook]\nconfig="book.toml"\nserve=true\n'
            '[books.user]\nconfig="book.user.toml"\nserve=false\n')
        cases = (([], 'book.toml', 'book.user.toml'),
                 (['--book', 'user'], 'book.user.toml', 'book.toml'))
        for index, (options, expected, excluded) in enumerate(cases):
            with self.subTest(options=options):
                self.assert_single_preview(index, options, expected, excluded)

    def assert_single_preview(self, index, options, expected, excluded):
        log = self.root / f'filtered-serve-{index}.log'
        with log.open('w') as stream:
            process = subprocess.Popen([sys.executable, str(self.script), '--root', str(self.root),
                                        *options, '--no-open', 'serve'],
                                       cwd=ROOT, stdout=stream, stderr=stream, start_new_session=True)
            try:
                self.wait_for(lambda: 'Serving documentation at http' in log.read_text(), process, log)
                text = log.read_text()
                self.assertIn(f'Processing {expected}', text)
                self.assertNotIn(f'Processing {excluded}\n', text)
                line = next(line for line in text.splitlines() if line.startswith('Serving documentation at '))
                url = line.removeprefix('Serving documentation at ')
                with urllib.request.urlopen(url, timeout=2) as response:
                    self.assertEqual(response.status, 200)
                process.send_signal(signal.SIGINT)
                self.assertEqual(process.wait(timeout=15), 130, log.read_text())
                self.assertFalse(list(self.root.glob('build/**/mdbook-runtime-*')))
                with self.assertRaises(OSError):
                    urllib.request.urlopen(url, timeout=1)
            finally:
                if process.poll() is None:
                    process.send_signal(signal.SIGINT)
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()

    def test_serves_both_reloads_and_cleans_up_on_interrupt(self):
        log = self.root / 'serve.log'
        with log.open('w') as stream:
            process = subprocess.Popen([sys.executable, str(self.script), '--root', str(self.root),
                                        '--no-open', 'serve'],
                                       cwd=ROOT, stdout=stream, stderr=stream, start_new_session=True)
            try:
                def urls():
                    return [line.split(': ', 1)[1] for line in log.read_text().splitlines()
                            if line.startswith(('book.toml: http', 'book.user.toml: http'))]
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
                config = self.root / 'book.user.toml'
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
