"""Exercise helpers from composed, installed schema directories."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('helper_distribution_builder', ROOT / 'scripts/schema-builder/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class HelperDistributionTests(unittest.TestCase):
    def test_all_composed_variants_include_ddd_and_only_documentation_variants_include_docs_check(self):
        for components in ([], ['arc42'], ['user-doc'], ['arc42', 'user-doc']):
            with self.subTest(components=components):
                files = builder.compose(components)
                for name in ('ddd.py', 'check.py', 'model.py', 'adr-preprocessor.py', 'project_root.py', 'README.md'):
                    self.assertIn('helpers/' + name, files)
                self.assertEqual('helpers/docs-check.py' in files, bool(components))
                if components:
                    self.assertEqual(files['helpers/README.md'].count('Helper pack: docs'), 1)
                self.assertFalse(any('__pycache__' in path or path.endswith('.pyc') for path in files))

    def test_installed_optional_renderer_protocol_and_marker_free_passthrough(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            installed = root / 'openspec/schemas/custom-name'
            builder.build(installed)
            command = [sys.executable, str(installed / 'helpers/adr-preprocessor.py')]
            for renderer, expected in (('html', 0), ('book-export', 0), ('latex', 1)):
                result = subprocess.run([*command, 'supports', renderer], cwd=outside,
                                        capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertEqual(result.stdout, '')
            source = root / 'openspec/specs/team/architectural-decisions/adr-invalid.md'
            source.parent.mkdir(parents=True)
            source.write_text('# Not an ADR\n')
            book = {'items': [{'Chapter': {'name': 'Notes', 'content': '# Notes\n',
                                          'path': 'notes.md', 'sub_items': []}}]}
            result = subprocess.run(command, cwd=outside, capture_output=True, text=True,
                                    input=json.dumps([{'root': str(root), 'config': {'book': {'src': 'docs'}}}, book]),
                                    timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), book)
            self.assertFalse((root / 'docs').exists())
            self.assertFalse((installed / 'helpers/__pycache__').exists())

    def test_legacy_stays_without_new_distributed_helpers(self):
        with tempfile.TemporaryDirectory() as directory:
            files = builder.build_legacy(Path(directory) / 'legacy')
            self.assertFalse(any(path.startswith('helpers/') for path in files))

    def test_installed_base_ddd_tools_work_from_elsewhere_without_a_book(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            installed = root / 'openspec/schemas/custom-name'
            builder.build(installed)
            (root / 'openspec/catalog.json').write_text('{"schema_version":1,"specs":[]}\n')
            for name, arguments in (('ddd.py', ['check']), ('check.py', [])):
                result = subprocess.run([sys.executable, str(installed / 'helpers' / name), *arguments],
                                        cwd=outside, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIsInstance(json.loads(result.stdout), dict)
            self.assertFalse((installed / 'helpers/__pycache__').exists())
            self.assertFalse((root / 'book.toml').exists())

    def test_installed_model_is_shared_by_renderer_and_validator_without_a_book(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            installed = root / 'openspec/schemas/custom-name'
            builder.build(installed, ['arc42', 'user-doc'])
            source = root / 'openspec/specs/team/architectural-decisions/adr-1.md'
            source.parent.mkdir(parents=True)
            text = ('# ADR-team-1: Shared source\n\nStatus: Observed\nDate: Unknown\n'
                    'Scope: The team\n\n<!-- preserve -->\n```text\nStatus: Example\n```\n')
            source.write_text(text)
            consumer = '''
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from model import decisions
from check import validate_decisions
root = Path(sys.argv[2])
records = decisions(root)
checked = validate_decisions(root, records)
assert len(records) == len(checked) == 1
assert records[0].id == checked[0]['id'] == 'ADR-team-1'
assert records[0].status == 'Observed'
assert records[0].text == (root / records[0].path).read_text()
assert 'text' not in checked[0]
assert not (root / 'openspec/catalog.json').exists()
print('Shared ADR data verified')
'''
            result = subprocess.run([sys.executable, '-c', consumer, str(installed / 'helpers'), str(root)],
                                    cwd=outside, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('Shared ADR data verified', result.stdout)
            self.assertFalse((installed / 'helpers/__pycache__').exists())

    def test_installed_docs_entry_uses_generic_builder_and_adjacent_ddd_helper(self):
        for components in (['arc42'], ['user-doc'], ['arc42', 'user-doc']):
            with self.subTest(components=components), tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
                root = Path(directory)
                installed = root / 'openspec/schemas/custom-docs'
                builder.build(installed, components)
                (root / 'notes').mkdir()
                (root / 'notes/page.md').write_text('# Notes\n')
                result = subprocess.run([sys.executable, str(installed / 'helpers/docs-check.py'),
                                         '--builder', str(ROOT / 'scripts/md-book-builder/book.py'),
                                         '--source-only', '--source', 'notes'],
                                        cwd=outside, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('sources verified', result.stdout)
                self.assertIn('"status": "skipped"', result.stdout)
                self.assertFalse((installed / 'helpers/__pycache__').exists())
                (root / 'notes/page.md').write_text('[Missing](missing.md)\n')
                failed = subprocess.run([sys.executable, str(installed / 'helpers/docs-check.py'),
                                         '--builder', str(ROOT / 'scripts/md-book-builder/book.py'),
                                         '--source-only', '--source', 'notes'],
                                        cwd=outside, capture_output=True, text=True, timeout=20)
                self.assertNotEqual(failed.returncode, 0)


if __name__ == '__main__':
    unittest.main()
