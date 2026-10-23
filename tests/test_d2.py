"""Optional D2 dependency checks and native rendering when tools are available."""
from pathlib import Path
import shutil
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
import d2


class D2Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = self.root / 'book.toml'
        self.config.write_text('[book]\ntitle="D2"\n')

    def test_disabled_does_not_probe_tools(self):
        with patch.object(d2.shutil, 'which') as which:
            d2.prepare(self.config, enabled=False)
        which.assert_not_called()

    def test_missing_preprocessor_is_downloaded_into_cache(self):
        with patch.object(d2.shutil, 'which', side_effect=[None, '/bin/d2']), \
                patch.object(d2, 'install', return_value=self.root / 'cached/mdbook-d2') as install:
            environment = d2.prepare(self.config, enabled=True, cache=self.root / 'cache')
        install.assert_called_once_with(self.root / 'cache', 'mdbook-d2', allow_install=True)
        self.assertEqual(json.loads(environment['MDBOOK_PREPROCESSOR__D2__COMMAND']),
                         str(self.root / 'cached/mdbook-d2'))

    def test_configured_binary_is_checked_from_book_root(self):
        self.config.write_text('[preprocessor.d2]\npath="tools/custom-d2"\n')
        with patch.object(d2.shutil, 'which', side_effect=['/bin/mdbook-d2', '/bin/custom']) as which:
            environment = d2.prepare(self.config, enabled=True)
        self.assertEqual(json.loads(environment['MDBOOK_PREPROCESSOR__D2__PATH']),
                         str(Path('/bin/custom').resolve()))
        self.assertEqual(which.call_args.args[0], str(self.root / 'tools/custom-d2'))

    def test_missing_default_compiler_is_downloaded(self):
        with patch.object(d2.shutil, 'which', side_effect=['/bin/mdbook-d2', None]), \
                patch.object(d2, 'install', return_value=self.root / 'cached/d2') as install:
            d2.prepare(self.config, enabled=True, cache=self.root / 'cache')
        install.assert_called_once_with(self.root / 'cache', 'd2', allow_install=True)

    def test_missing_custom_compiler_is_not_replaced(self):
        self.config.write_text('[preprocessor.d2]\npath="tools/custom-d2"\n')
        with patch.object(d2.shutil, 'which', side_effect=['/bin/mdbook-d2', None]), \
                patch.object(d2, 'install') as install:
            with self.assertRaisesRegex(RuntimeError, 'D2 executable not found'):
                d2.prepare(self.config, enabled=True)
        install.assert_not_called()

    def test_docker_does_not_require_host_tools(self):
        with patch.object(d2.shutil, 'which') as which:
            d2.prepare(self.config, enabled=True, docker_mode=True)
        which.assert_not_called()

    def test_external_file_mode_is_rejected_before_source_writes(self):
        self.config.write_text('[preprocessor.d2]\ninline=false\n')
        for docker in (False, True):
            with self.subTest(docker=docker), self.assertRaisesRegex(ValueError, 'book sources'):
                d2.prepare(self.config, enabled=True, docker_mode=docker)

    def test_real_html_render_and_invalid_diagram_when_available(self):
        if not all(shutil.which(name) for name in ('mdbook', 'mdbook-d2', 'd2')):
            self.skipTest('Provide mdbook, mdbook-d2 0.3.9 and d2 on PATH for rendering integration')
        (self.root / 'book-builder.toml').write_text(
            '[books.test]\nconfig="book.toml"\nd2=true\n')
        source = self.root / 'src'
        source.mkdir()
        (source / 'SUMMARY.md').write_text('# Summary\n\n- [Diagram](diagram.md)\n')
        chapter = source / 'diagram.md'
        original = '# Diagram\n\n```d2\nreader -> book\n```\n'
        chapter.write_text(original)
        command = [sys.executable, str(ROOT / 'scripts/md-book-builder/book.py'),
                   '--root', str(self.root), 'build', '--format', 'markdown', '--format', 'typst']
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (self.root / 'book/diagram.html').read_text()
        self.assertIn('<svg', html)
        self.assertNotIn('class="language-d2"', html)
        self.assertEqual(chapter.read_text(), original)
        self.assertEqual(sorted(p.name for p in source.iterdir()), ['SUMMARY.md', 'diagram.md'])
        self.assertIn('```d2', (self.root / 'book/D2.md').read_text())
        self.assertIn('reader -> book', (self.root / 'book/D2.typ').read_text())
        chapter.write_text('# Broken\n\n```d2\na: {\n```\n')
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class D2DownloadTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.cache = Path(temporary.name) / 'cache with spaces'
        import runpy
        self.api = runpy.run_path(str(ROOT / 'scripts/md-book-builder/download-latest-mdbook.py'))

    def test_platform_assets(self):
        for system, machine, d2_asset, preprocessor in (
            ('linux', 'x86_64', 'linux-amd64.tar.gz', 'x86_64-unknown-linux-musl.tar.gz'),
            ('linux', 'aarch64', 'linux-arm64.tar.gz', 'aarch64-unknown-linux-musl.tar.gz'),
            ('darwin', 'arm64', 'macos-arm64.tar.gz', 'aarch64-apple-darwin.tar.gz'),
            ('win32', 'AMD64', 'windows-amd64.tar.gz', 'x86_64-pc-windows-msvc.zip'),
            ('win32', 'ARM64', 'windows-arm64.tar.gz', 'aarch64-pc-windows-msvc.zip')):
            with self.subTest(system=system, machine=machine), \
                    patch.object(d2.sys, 'platform', system), \
                    patch.object(d2.platform, 'machine', return_value=machine):
                self.assertEqual(d2.asset_name('d2', 'v0.7.1')[0], 'd2-v0.7.1-' + d2_asset)
                self.assertEqual(d2.asset_name('mdbook-d2', 'v0.3.9')[0], 'mdbook-d2-' + preprocessor)
                self.assertEqual(d2.asset_name('d2', 'v0.7.1')[1], 'd2.exe' if system == 'win32' else 'd2')
                manifest = json.loads(d2.MANIFEST.read_text())
                for name in ('d2', 'mdbook-d2'):
                    asset = d2.asset_name(name, manifest[name]['version'])[0]
                    self.assertRegex(manifest[name]['assets'][asset], r'^[0-9a-f]{64}$')

    def test_checked_download_cache_reuse_and_corruption_repair(self):
        import hashlib
        archive = b'archive'
        tool = {'d2': {'repository': 'd2lang/d2', 'version': 'v0.7.1',
                      'assets': {'test.tar.gz': hashlib.sha256(archive).hexdigest()}}}
        manifest = self.cache.parent / 'toolchain.json'
        manifest.write_text(json.dumps(tool))
        request = unittest.mock.Mock(return_value=archive)
        api = {'request_bytes': request, 'extract_binary': unittest.mock.Mock(return_value=b'executable')}
        with patch.object(d2, 'MANIFEST', manifest), \
                patch.object(d2, 'asset_name', return_value=('test.tar.gz', 'd2')), \
                patch.object(d2.runpy, 'run_path', return_value=api):
            binary = d2.install(self.cache, 'd2')
            self.assertTrue(d2.valid_binary(binary))
            self.assertEqual(d2.install(self.cache, 'd2', allow_install=False), binary)
            request.assert_called_once_with('https://github.com/d2lang/d2/releases/download/v0.7.1/test.tar.gz')
            binary.write_bytes(b'corrupt')
            with self.assertRaisesRegex(RuntimeError, '--no-install'):
                d2.install(self.cache, 'd2', allow_install=False)
            d2.install(self.cache, 'd2')
            self.assertEqual(request.call_count, 2)
            self.assertTrue(d2.valid_binary(binary))

    def test_wrong_checksum_is_not_extracted_or_published(self):
        manifest = self.cache.parent / 'toolchain.json'
        manifest.write_text(json.dumps({'d2': {'repository': 'd2lang/d2', 'version': 'v0.7.1',
                                             'assets': {'test.tar.gz': '0' * 64}}}))
        extract = unittest.mock.Mock()
        with patch.object(d2, 'MANIFEST', manifest), \
                patch.object(d2, 'asset_name', return_value=('test.tar.gz', 'd2')), \
                patch.object(d2.runpy, 'run_path', return_value={
                    'request_bytes': unittest.mock.Mock(return_value=b'bad'), 'extract_binary': extract}):
            with self.assertRaisesRegex(RuntimeError, 'SHA-256 mismatch'):
                d2.install(self.cache, 'd2')
        extract.assert_not_called()
        self.assertFalse([p for p in self.cache.rglob('d2') if p.is_file()])

    def test_safe_extraction_of_nested_executable(self):
        import io
        import tarfile
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w:gz') as archive:
            member = tarfile.TarInfo('d2-v0.7.1/bin/d2')
            member.size = 6
            archive.addfile(member, io.BytesIO(b'binary'))
        self.assertEqual(self.api['extract_binary'](stream.getvalue(), 'tar.gz', 'd2'), b'binary')
