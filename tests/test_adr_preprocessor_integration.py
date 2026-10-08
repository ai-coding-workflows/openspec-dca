"""Optional ADR rendering through real native mdBook and builder capture.

Only temporary adopting projects are modified; no generated chapters are written
into their maintained Markdown tree. No native tooling is downloaded here.
"""
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import posixpath
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / 'scripts/md-book-builder'
HELPERS = ROOT / 'src/schemas/ddd/helpers'
CACHED_MDBOOK = (BUILDER / '.cache/native-tools/mdbook/'
                 'x86_64-unknown-linux-musl/v0.5.4/mdbook')
TEAM = Path('openspec/specs/team/architectural-decisions')
SECURITY = Path('openspec/system-architecture/security/architectural-decisions')


def native_mdbook():
    candidates = [CACHED_MDBOOK]
    installed = shutil.which('mdbook')
    if installed:
        candidates.append(Path(installed))
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            result = subprocess.run([str(candidate), '--version'], capture_output=True,
                                    text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0 and result.stdout.strip() == 'mdbook v0.5.4':
            return candidate.resolve()
    return None


class Html(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.images = []
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs['src'])


class AdrPreprocessorIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mdbook = native_mdbook()
        if cls.mdbook is None:
            raise unittest.SkipTest('Native mdBook 0.5.4 required (cached or on PATH)')

    def setUp(self):
        # Deliberately fail, rather than skip, when the implementation is absent.
        self.assertTrue((HELPERS / 'adr-preprocessor.py').is_file(),
                        'Missing schema helper adr-preprocessor.py')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = os.environ.copy()
        self.env['PATH'] = str(self.mdbook.parent) + os.pathsep + self.env.get('PATH', '')
        # Do not suppress bytecode here: the installed helper must prevent it.
        self.env.pop('PYTHONDONTWRITEBYTECODE', None)
        for key in list(self.env):
            if key.startswith('MDBOOK_'):
                del self.env[key]

    def fixture(self, name):
        root = Path(self.temp.name) / name
        helpers = root / 'openspec/schemas/custom-name/helpers'
        shutil.copytree(HELPERS, helpers,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        docs = root / 'docs'
        (docs / 'nested').mkdir(parents=True)
        (docs / 'img').mkdir()
        (docs / 'img/logo.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"></svg>\n',
            encoding='utf-8')
        (docs / 'SUMMARY.md').write_text(
            '# Summary\n\n- [Home](index.md)\n- [Decisions](nested/decisions.md)\n'
            '- [Existing sibling](nested/sibling.md)\n', encoding='utf-8')
        (docs / 'index.md').write_text('# Home\n\nMaintained home text.\n', encoding='utf-8')
        (docs / 'nested/decisions.md').write_text(
            '# Decisions\n\nHost introduction stays.\n\n{{#adr-index}}\n', encoding='utf-8')
        (docs / 'nested/sibling.md').write_text(
            '# Existing sibling\n\nSibling survives generated navigation.\n', encoding='utf-8')
        for directory in (TEAM, SECURITY):
            (root / directory).mkdir(parents=True)
        asset = posixpath.relpath('docs/img/logo.svg', TEAM.as_posix())
        other = posixpath.relpath((SECURITY / 'ADR-S-2.md').as_posix(), TEAM.as_posix())
        (root / TEAM / 'ADR-A-1.md').write_text(
            '# ADR-A-1: Team boundary\n\nStatus: Accepted\nDate: Unknown\n'
            'Scope: The team and its collaborating people\n\n## Context\n\n'
            'Original team context is preserved.\n\n'
            f'[Security decision]({other})\n\n![Local logo]({asset})\n\n'
            '## Decision\n\nKeep a stable boundary.\n', encoding='utf-8')
        (root / SECURITY / 'ADR-S-2.md').write_text(
            '# ADR-S-2: Security boundary\n\nStatus: Proposed\nDate: Unknown\n'
            'Scope: Security across collaborating services\n\n## Context\n\n'
            'Original security context is preserved.\n\n## Decision\n\n'
            'Use an explicit security boundary.\n', encoding='utf-8')
        command = f'"{sys.executable}" "openspec/schemas/custom-name/helpers/adr-preprocessor.py"'
        (root / 'book.toml').write_text(
            '[book]\ntitle = "ADR integration"\nsrc = "docs"\n'
            '[build]\nbuild-dir = "site"\n'
            '[preprocessor.adr]\ncommand = ' + json.dumps(command) + '\n', encoding='utf-8')
        return root

    def snapshot(self, root):
        return {path.relative_to(root): path.read_bytes() for path in root.rglob('*')
                if path.is_file() and (path.suffix == '.md' or path.name == 'book.toml')
                and not path.is_relative_to(root / 'site')}

    def invoke(self, root, command):
        return subprocess.run(command, cwd=root, env=self.env, capture_output=True,
                              text=True, timeout=90)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_unchanged(self, root, before):
        self.assertEqual(self.snapshot(root), before)
        self.assertFalse((root / 'docs/nested/adr').exists())
        self.assertFalse(list((root / 'openspec/schemas/custom-name/helpers').rglob('__pycache__')))

    def test_native_html_virtual_tree_links_and_local_asset(self):
        for name in ('project', 'project with spaces'):
            with self.subTest(project=name):
                root = self.fixture(name)
                before = self.snapshot(root)
                self.assert_success(self.invoke(root, [str(self.mdbook), 'build']))
                # Separate interpreter avoids collision with other tests' check/model modules.
                self.assert_success(self.invoke(root, [sys.executable, str(BUILDER / 'check.py'),
                                                      '--root', str(root), '--rendered']))
                site = root / 'site'
                host = site / 'nested/decisions.html'
                index = Html(host.read_text(encoding='utf-8'))
                for directory, anchor, title, status, scope in (
                    (TEAM, 'adr-a-1', 'Team boundary', 'Accepted',
                     'The team and its collaborating people'),
                    (SECURITY, 'adr-s-2', 'Security boundary', 'Proposed',
                     'Security across collaborating services'),
                ):
                    page = site / 'nested/adr' / directory / 'index.html'
                    self.assertTrue(page.is_file(), page)
                    text = page.read_text(encoding='utf-8')
                    self.assertIn(anchor, Html(text).ids)
                    self.assertRegex(text, r'<h2\b[^>]*>.*?ADR-[AS]-[12]:')
                    for value in (title, status, scope, 'Unknown', 'Original'):
                        self.assertIn(value, text)
                    expected = posixpath.relpath(page.relative_to(site).as_posix(), 'nested')
                    self.assertTrue(any(urlsplit(link).path == expected
                                        and urlsplit(link).fragment == anchor for link in index.links))
                team_page = site / 'nested/adr' / TEAM / 'index.html'
                team_html = Html(team_page.read_text(encoding='utf-8'))
                self.assertTrue(any(urlsplit(link).fragment == 'adr-s-2' for link in team_html.links))
                self.assertTrue(any((team_page.parent / unquote(urlsplit(image).path)).resolve()
                                    == (site / 'img/logo.svg').resolve() for image in team_html.images))
                self.assertIn('Sibling survives', (site / 'nested/sibling.html').read_text())
                # mdBook 0.5 emits sidebar navigation into JavaScript, not static HTML.
                sidebars = list(site.glob('toc*.js'))
                self.assertTrue(sidebars)
                sidebar = '\n'.join(path.read_text(encoding='utf-8') for path in sidebars)
                self.assertIn('nested/sibling.html', sidebar)
                self.assertIn('nested/adr/openspec/specs/team/architectural-decisions/index.html', sidebar)
                self.assert_unchanged(root, before)

    def test_generic_markdown_export_captures_preprocessed_virtual_chapters(self):
        root = self.fixture('export project with spaces')
        before = self.snapshot(root)
        self.assert_success(self.invoke(root, [sys.executable, str(BUILDER / 'book.py'),
                                              'export', '--root', str(root),
                                              '--format', 'markdown', '--no-install']))
        exports = list((root / 'site').glob('*.md'))
        self.assertEqual(len(exports), 1, exports)
        text = exports[0].read_text(encoding='utf-8')
        for value in ('Team boundary', 'Security boundary', 'Original team context',
                      'Original security context', 'Sibling survives', 'Host introduction', 'Source'):
            self.assertIn(value, text)
        self.assertNotIn('{{#adr-index}}', text)
        self.assertRegex(text, r'\[Security decision\]\(#[^)]+--adr-s-2\)')
        self.assertRegex(text, r'\]\(#[^)]+--adr-a-1\)')
        self.assertNotIn('ADR-S-2.md)', text)
        self.assert_unchanged(root, before)

    def test_multiple_markers_fail_native_build_and_capture_without_fallback(self):
        root = self.fixture('invalid project')
        host = root / 'docs/nested/decisions.md'
        host.write_text(host.read_text() + '\n{{#adr-index}}\n', encoding='utf-8')
        before = self.snapshot(root)
        commands = ([str(self.mdbook), 'build'],
                    [sys.executable, str(BUILDER / 'book.py'), 'export', '--root', str(root),
                     '--format', 'markdown', '--no-install'])
        for command in commands:
            with self.subTest(command=command):
                result = self.invoke(root, command)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('adr-index', result.stdout + result.stderr)
                self.assertFalse(list((root / 'site').glob('*.md')))
                self.assert_unchanged(root, before)


if __name__ == '__main__':
    unittest.main()
