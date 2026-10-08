"""Read-only ADR mdBook rendering, independent of application policy."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('adr_test_builder', ROOT / 'scripts/schema-builder/build.py')
_builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_builder)
# Exercise the composed layout: arc42 supplies the renderer, DDD its reader/checker.
_schema = tempfile.TemporaryDirectory()
_builder.build(Path(_schema.name) / 'schema', ['arc42'])
HELPERS = Path(_schema.name) / 'schema/helpers'
SCRIPT = HELPERS / 'adr-preprocessor.py'


def load(path=SCRIPT):
    spec = importlib.util.spec_from_file_location('_test_adr_renderer', path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(spec.name)
    bytecode = sys.dont_write_bytecode
    try:
        sys.modules[spec.name] = module
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = bytecode
        if previous is None:
            sys.modules.pop(spec.name, None)
        else:
            sys.modules[spec.name] = previous
    return module


def chapter(path='architecture/index.md', content='{{#adr-index}}', number=None):
    return {'Chapter': {'name': 'Architecture', 'content': content,
                        'number': [2] if number is None else number, 'sub_items': [],
                        'path': path, 'source_path': path, 'parent_names': []}}


def chapters(items):
    for item in items:
        if isinstance(item, dict) and 'Chapter' in item:
            yield item['Chapter']
            yield from chapters(item['Chapter']['sub_items'])


class AdrPreprocessorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / 'docs'
        self.src.mkdir()
        self.renderer = load()
        self.context = {'root': str(self.root), 'renderer': 'html',
                        'config': {'book': {'src': 'docs'}}}
        self.book = {'items': [chapter(), 'Separator', {'PartTitle': 'Other'}]}
        self.resolver = patch.object(self.renderer.check, 'resolve_project_root', return_value=self.root)
        self.resolve_mock = self.resolver.start()
        self.addCleanup(self.resolver.stop)

    def adr(self, directory='team', name='adr-one.md', ident='ADR-One', scope='Any prose scope', extra=''):
        path = self.root / 'openspec/specs' / directory / 'architectural-decisions' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'# {ident}: A choice\n\nStatus: Experimental\nDate: Whenever appropriate\nScope: {scope}\n\n{extra}', encoding='utf-8')
        return path

    def run_book(self):
        return self.renderer.preprocess(self.context, self.book)

    def test_hidden_comments_and_h6_are_not_broken_by_render_transformations(self):
        hidden = '<!--\n[Hidden](missing.md) <img src="missing.svg">\n{{#include missing.md}}\n-->\n'
        text = hidden + '# Visible\n###### Keep heading\n'
        def rewrite(value):
            raise AssertionError(f'Hidden content was rewritten: {value}')
        rendered = self.renderer._render_text(text, rewrite)
        self.assertEqual(rendered, hidden + '## Visible\n###### Keep heading\n')

    def test_comment_fences_and_inline_comment_examples_remain_opaque(self):
        text = '<!--\n```md\n[Hidden](missing.md)\n-->\n# Visible\n`<!--`\n```md\n# Example\n```\n'
        rendered = self.renderer._render_text(text, lambda value: self.fail(value))
        self.assertEqual(rendered, text.replace('# Visible', '## Visible'))

    def test_quoted_marker_examples_are_not_activated_or_replaced(self):
        examples = ('`{{#adr-index}}`\n<!-- {{#adr-index}} -->\n'
                    '```md\n{{#adr-index}}\n```\n    {{#adr-index}}\n')
        host = self.book['items'][0]['Chapter']
        host['content'] = examples
        with patch.object(self.renderer.check.model, 'decisions', side_effect=AssertionError):
            self.run_book()
        self.assertEqual(host['content'], examples)
        self.adr()
        host['content'] = examples + '\n{{#adr-index}}\n'
        self.run_book()
        self.assertTrue(host['content'].startswith(examples))
        self.assertIn('| ID |', host['content'])
        self.assertEqual(host['content'].count('{{#adr-index}}'), 4)

    def test_passthrough_never_discovers_or_validates(self):
        with patch.object(self.renderer.check.model, 'decisions', side_effect=AssertionError), patch.object(self.renderer.check, 'validate_decisions', side_effect=AssertionError):
            self.book['items'][0]['Chapter']['content'] = 'No marker'
            original = copy.deepcopy(self.book)
            self.assertEqual(self.run_book(), original)
            self.context['renderer'] = 'unknown'
            self.book['items'][0]['Chapter']['content'] = '{{#adr-index}}'
            original = copy.deepcopy(self.book)
            self.assertEqual(self.run_book(), original)

    def test_single_model_snapshot_and_read_only(self):
        path = self.adr()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        model = self.renderer.check.model
        read_bytes = Path.read_bytes
        reads = []

        def read_once(file):
            reads.append(file)
            return read_bytes(file)

        with patch.object(model, 'decisions', wraps=model.decisions) as discover, patch.object(Path, 'read_bytes', read_once), patch.object(self.renderer.check, 'validate_decisions', wraps=self.renderer.check.validate_decisions) as validate, patch.object(self.renderer.check, 'Catalog', side_effect=AssertionError('No catalog')):
            result = self.run_book()
        discover.assert_called_once_with(self.root)
        validate.assert_called_once()
        self.assertEqual(reads, [path])
        self.resolve_mock.assert_called_once_with(None, helper_file=str(SCRIPT), cwd=self.context['root'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse((self.root / 'openspec/catalog.json').exists())
        text = '\n'.join(c['content'] for c in chapters(result['items']))
        self.assertIn('Whenever appropriate', text)
        self.assertIn('Any prose scope', text)
        self.assertIn(path.relative_to(self.root).as_posix(), text)

    def test_tree_native_fields_navigation_determinism(self):
        self.adr('zulu')
        self.adr('alpha')
        self.book['items'][0]['Chapter']['sub_items'] = [chapter('existing.md', 'Kept', [2, 1])]
        original = copy.deepcopy(self.book)
        result = self.run_book()
        self.assertEqual(result['items'][1:], ['Separator', {'PartTitle': 'Other'}])
        host = result['items'][0]['Chapter']
        self.assertEqual(host['sub_items'][0], original['items'][0]['Chapter']['sub_items'][0])
        tree = host['sub_items'][1]['Chapter']
        self.assertEqual(tree['name'], 'Openspec')
        self.assertEqual(tree['number'], [2, 2])
        self.assertEqual(tree['parent_names'], ['Architecture'])
        self.assertEqual(tree['path'], 'architecture/adr/openspec/index.md')
        all_generated = list(chapters(host['sub_items'][1:]))
        self.assertTrue(all(c['source_path'] is None for c in all_generated))
        self.assertIn('specs/index.md', tree['content'])
        self.assertIn('[Parent](../index.md)', all_generated[-1]['content'])
        self.book = original
        self.assertEqual(result, self.run_book())

    def test_anchor_scoped_by_directory_not_scope(self):
        self.adr('a', ident='ADR-Same')
        self.adr('b', ident='ADR-Same')
        result = self.run_book()
        self.assertNotIn('<a ', result['items'][0]['Chapter']['content'])
        self.assertEqual(sum('<a id="adr-same"></a>' in c['content'] for c in chapters(result['items'])), 2)
        self.book = {'items': [chapter()]}
        self.adr('a', name='adr-two.md', ident='ADR-same', scope='Different')
        with self.assertRaisesRegex(ValueError, 'anchor'):
            self.run_book()

    def test_unsafe_ids_and_table_escaping(self):
        self.adr(ident='ADR-Ä"x', scope='<script>|[x]`')
        result = self.run_book()
        content = result['items'][0]['Chapter']['content']
        self.assertIn('&lt;script&gt;', content)
        self.assertNotIn('<script>', content)
        self.assertIn('&#124;', content)
        self.assertIn('&#91;', content)
        self.assertIn('&#96;', content)
        self.assertRegex(content, r'#adr-[a-z0-9-]+')

    def test_heading_and_code_preservation(self):
        extra = '# Heading\n## Child\n```md\n# Example\n[x](missing.md)\n```\n~~~\n# Tilde\n~~~\n    # Indented\n    [x](missing.md)\n`[x](missing.md)`\n'
        path = self.adr(extra=extra)
        original = path.read_text()
        result = self.run_book()
        leaf = list(chapters(result['items']))[-1]['content']
        self.assertIn('## Heading\n### Child', leaf)
        self.assertIn('```md\n# Example\n[x](missing.md)\n```', leaf)
        self.assertIn('    # Indented', leaf)
        self.assertIn('`[x](missing.md)`', leaf)
        self.assertEqual(path.read_text(), original)

    def test_links_inline_reference_images_and_fragments(self):
        second = self.adr('other', ident='ADR-Two')
        asset = self.src / 'image (1).png'
        asset.write_bytes(b'image')
        page = self.src / 'guide.md'
        page.write_text('# Guide')
        first = self.adr(extra='[other](../../other/architectural-decisions/adr-one.md)\n[fragment](../../other/architectural-decisions/adr-one.md#detail)\n[guide](../../../../docs/guide.md "Title")\n![image](<../../../../docs/image (1).png> "An image")\n[ref]: ../../../../docs/guide.md \'Title\'\n[use][ref]\n[external](https://example.org/a) [data](data:image/png;base64,a) [fragment](#local)\n')
        result = self.run_book()
        leaf = next(c for c in chapters(result['items']) if '<a id="adr-one"' in c['content'])
        self.assertIn('../../other/architectural-decisions/index.md#adr-two', leaf['content'])
        self.assertIn('index.md#detail', leaf['content'])
        self.assertIn('../../../../../../guide.md "Title"', leaf['content'])
        self.assertIn('<../../../../../../image%20%281%29.png>', leaf['content'])
        self.assertIn("[ref]: ../../../../../../guide.md 'Title'", leaf['content'])
        self.assertIn('[fragment](#local)', leaf['content'])
        self.assertEqual(second.read_text().count('# ADR-Two'), 1)
        self.assertIn('[other](../../other/', first.read_text())

    def test_parenthesized_destination(self):
        asset = self.src / 'image(1).png'
        asset.write_bytes(b'image')
        self.adr(extra='![x](../../../../docs/image(1).png "title")')
        result = self.run_book()
        self.assertIn('image%281%29.png "title"', list(chapters(result['items']))[-1]['content'])

    def test_missing_outside_and_html_local_resources_fail(self):
        for extra, diagnostic in [('[x](missing.md)', 'Missing'), ('[x](../asset.png)', 'book source'), ('<img src="../asset.png">', 'HTML'), ('{{#include file.md}}', 'include')]:
            with self.subTest(extra=extra):
                self.book = {'items': [chapter()]}
                path = self.adr(extra=extra)
                (path.parent.parent / 'asset.png').write_bytes(b'asset')
                with self.assertRaisesRegex(ValueError, diagnostic):
                    self.run_book()

    def test_duplicate_marker_and_all_existing_path_collisions(self):
        self.adr()
        self.book['items'].append(chapter('other.md', '{{#adr-index}}'))
        with self.assertRaisesRegex(ValueError, 'marker'):
            self.run_book()
        self.book['items'][-1] = chapter('architecture/adr/openspec/index.md', 'Existing')
        with self.assertRaisesRegex(ValueError, 'collision'):
            self.run_book()

    def test_nested_host_empty_and_unsafe_path(self):
        outer = chapter('outer.md', 'Outer', [1])
        outer['Chapter']['sub_items'] = [chapter('nested/host.md', number=[1, 1])]
        outer['Chapter']['sub_items'][0]['Chapter']['parent_names'] = ['Outer']
        self.book = {'sections': [outer]}
        result = self.run_book()
        self.assertEqual(result['sections'][0]['Chapter']['sub_items'][0]['Chapter']['content'], 'No architecture decisions found.')
        self.book = {'items': [chapter('../bad.md')]}
        with self.assertRaisesRegex(ValueError, 'path'):
            self.run_book()

    def test_installed_helper_root_authoritative_in_staged_book(self):
        installed = self.root / 'openspec/schemas/chosen/helpers'
        installed.mkdir(parents=True)
        for name in ('adr-preprocessor.py', 'check.py', 'model.py', 'ddd.py', 'project_root.py'):
            (installed / name).write_bytes((HELPERS / name).read_bytes())
        self.adr()
        staged = self.root / 'scratch/book'
        staged.mkdir(parents=True)
        context = {**self.context, 'root': str(staged)}
        result = load(installed / 'adr-preprocessor.py').preprocess(context, copy.deepcopy(self.book))
        self.assertIn('ADR-One', result['items'][0]['Chapter']['content'])
        self.assertFalse(list(installed.rglob('__pycache__')))
        process = subprocess.run([sys.executable, str(installed / 'adr-preprocessor.py')], input=json.dumps([context, self.book]), capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout), result)
        self.assertEqual(process.stderr, '')
        self.assertFalse(list(installed.rglob('__pycache__')))

    def test_nested_number_and_parent_names(self):
        self.adr()
        outer = chapter('outer.md', 'Outer', [1])
        host = chapter('nested/host.md', number=[1, 3])
        host['Chapter']['parent_names'] = ['Outer']
        outer['Chapter']['sub_items'] = [host]
        self.book = {'items': [outer]}
        result = self.run_book()
        generated = result['items'][0]['Chapter']['sub_items'][0]['Chapter']['sub_items'][0]['Chapter']
        self.assertEqual(generated['parent_names'], ['Outer', 'Architecture'])
        self.assertEqual(generated['number'], [1, 3, 1])
        self.assertEqual(generated['path'], 'nested/adr/openspec/index.md')
        self.assertIn('[Parent](../../host.md)', generated['content'])

    def test_multiline_inline_code_and_book_src_default(self):
        default_src = self.root / 'src'
        default_src.mkdir()
        (default_src / 'guide.md').write_text('# Guide')
        self.context['config'] = {}
        self.context['renderer'] = 'book-export'
        self.adr(extra='``Example\n# Code heading\n[x](missing.md)\n``\n[actual](../../../../src/guide.md)\n')
        result = self.run_book()
        leaf = list(chapters(result['items']))[-1]['content']
        self.assertIn('``Example\n# Code heading\n[x](missing.md)\n``', leaf)
        self.assertIn('[actual](../../../../../../guide.md)', leaf)

    def test_import_restores_global_state_and_uses_adjacent_model(self):
        sentinel = object()
        original = sys.modules.get('_ddd_adr_check')
        sys.modules['_ddd_adr_check'] = sentinel
        bytecode = sys.dont_write_bytecode
        try:
            renderer = load()
            self.assertIs(sys.modules['_ddd_adr_check'], sentinel)
            self.assertEqual(sys.dont_write_bytecode, bytecode)
            self.assertEqual(Path(renderer.check.model.__file__), HELPERS / 'model.py')
        finally:
            if original is None:
                sys.modules.pop('_ddd_adr_check', None)
            else:
                sys.modules['_ddd_adr_check'] = original

    def test_path_containment_symlink_and_absolute_links(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'outside.png'
            target.write_bytes(b'asset')
            source = self.adr(extra='[escape](escape.png)')
            (source.parent / 'escape.png').symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'escapes project'):
                self.run_book()
        self.book = {'items': [chapter()]}
        self.adr(extra='[absolute](/etc/passwd)')
        with self.assertRaisesRegex(ValueError, 'relative'):
            self.run_book()

    def test_duplicate_marker_in_one_chapter_and_missing_host_path(self):
        self.book = {'items': [chapter(content='{{#adr-index}}\n{{#adr-index}}')]}
        with patch.object(self.renderer.check.model, 'decisions', side_effect=AssertionError):
            with self.assertRaisesRegex(ValueError, 'marker'):
                self.run_book()
        self.book = {'items': [chapter(path=None)]}
        with self.assertRaisesRegex(ValueError, 'path'):
            self.run_book()

    def test_cli_protocol_json_and_error(self):
        for renderer, code in [('html', 0), ('book-export', 0), ('unknown', 1)]:
            process = subprocess.run([sys.executable, str(SCRIPT), 'supports', renderer], capture_output=True, text=True)
            self.assertEqual(process.returncode, code)
            self.assertEqual(process.stdout, '')
        self.book['items'][0]['Chapter']['content'] = 'Passthrough'
        process = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps([self.context, self.book]), capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout), self.book)
        self.book['items'][0]['Chapter']['content'] = '{{#adr-index}} {{#adr-index}}'
        process = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps([self.context, self.book]), capture_output=True, text=True)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(process.stdout, '')
        self.assertTrue(process.stderr.startswith('adr-preprocessor:'))


if __name__ == '__main__':
    unittest.main()
