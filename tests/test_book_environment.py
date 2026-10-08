import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/md-book-builder'))
from book_environment import container_path, javascript_environment, capture_environment


class BookEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.builder = self.root / 'tools/documentation/md-book-builder'
        self.builder.mkdir(parents=True)
        self.book = self.root / 'handbooks/architecture'
        self.book.mkdir(parents=True)
        self.config = self.book / 'book.user.toml'

    def test_native_paths_are_original_config_relative_not_staging_relative(self):
        self.config.write_text('[output.html]\nadditional-js=["../../tools/documentation/md-book-builder/.cache/scripts/mermaid/v1/mermaid.min.js", "custom.js"]\n')
        env = javascript_environment(self.config, project_root=self.root, builder_dir=self.builder)
        self.assertEqual(json.loads(env['MDBOOK_OUTPUT'])['html']['additional-js'],
                         [str(self.builder / '.cache/scripts/mermaid/v1/mermaid.min.js'), str(self.book / 'custom.js')])

    def test_container_paths_use_builder_and_project_mounts(self):
        self.assertEqual(container_path(self.builder / '.cache/tool', self.root, self.builder), '/book-builder/.cache/tool')
        self.assertEqual(container_path(self.book / 'custom.js', self.root, self.builder), '/book/handbooks/architecture/custom.js')
        with self.assertRaises(ValueError):
            container_path(self.root.parent / 'outside.js', self.root, self.builder)

    def test_docker_javascript_override_preserves_author_scripts(self):
        self.config.write_text('[output.html]\nadditional-js=["../../tools/documentation/md-book-builder/.cache/scripts/mermaid/v1/mermaid-init.js", "custom.js"]\n')
        env = javascript_environment(self.config, project_root=self.root, builder_dir=self.builder, docker_mode=True)
        self.assertEqual(json.loads(env['MDBOOK_OUTPUT'])['html']['additional-js'],
                         ['/book-builder/.cache/scripts/mermaid/v1/mermaid-init.js', '/book/handbooks/architecture/custom.js'])

    def test_capture_removes_nested_html_overrides_without_mutating_input(self):
        original = {'MDBOOK_OUTPUT__HTML__ADDITIONAL_JS': '["cached.js"]', 'MDBOOK_OUTPUT__HTML__OTHER': 'true', 'PATH': '/tools'}
        env = capture_environment(original, '{"book-export":{}}')
        self.assertEqual(env, {'MDBOOK_OUTPUT': '{"book-export":{}}', 'MDBOOK_BUILD__CREATE_MISSING': 'false', 'PATH': '/tools'})
        self.assertIn('MDBOOK_OUTPUT__HTML__ADDITIONAL_JS', original)

    def test_unconfigured_scripts_do_not_add_html_backend(self):
        self.config.write_text('[book]\ntitle="Plain"\n')
        self.assertEqual(javascript_environment(self.config, project_root=self.root, builder_dir=self.builder), {})


if __name__ == '__main__':
    unittest.main()
