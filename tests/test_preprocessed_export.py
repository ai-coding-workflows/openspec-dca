import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/md-book-builder"))
from exporter.export_book import ExportError, export_book, export_markdown, export_typst, export_pdf


def chapter(name, content, path=None, source_path=None, children=None):
    return {"Chapter": {"name": name, "content": content, "path": path,
                        "source_path": source_path, "sub_items": children or []}}


class PreprocessedExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "content"
        self.src.mkdir()
        self.config = self.root / "book.toml"
        self.config.write_text('[book]\ntitle="Host Unicode 書"\nsrc="content"\n'
                               '[build]\nbuild-dir="out"\n', encoding="utf-8")
        self.context = self.root / "context.json"
        self.source = self.src / "real.md"
        self.source.write_text("SOURCE MUST NOT BE READ", encoding="utf-8")
        (self.src / "SUMMARY.md").write_text("[Real](real.md)", encoding="utf-8")

    def capture(self, items):
        self.context.write_text(json.dumps({"config": {"book": {"src": "/book"}},
                                            "destination": "/book/build",
                                            "book": {"items": items}}, ensure_ascii=False), encoding="utf-8")

    def tree(self):
        self.capture([
            "Separator", {"PartTitle": "Generated"},
            chapter("Parent", '# Same\n\nUnicode 書\n'
                    '[child](virtual/child.html#cell) [child start](virtual/child.md)\n'
                    '[second](other.md#same)\n{{#include absent.md}}\n', "real.md", "real.md", [
                chapter("Child", '# Same\n\n## Details\n\n'
                        '| Key | Value |\n| --- | --- |\n'
                        '| <a id=\'cell\'></a>Cell | [self](#cell) |\n\n'
                        '- <a id="list"></a>List [parent](../real.md#same)\n\n'
                        '`<a id="code"></a>`\n\n```html\n<a id="fenced"></a>\n```\n',
                        "virtual/child.md", "real.md")]),
            chapter("Other", '# Same\n\nOther content\n', "other.md"),
            chapter("Pathless", 'Pathless body [local](#spot) <a id="spot"></a>\n')])

    def test_virtual_tree_markdown_links_order_unicode_and_source_preservation(self):
        self.tree()
        original = self.source.read_bytes()
        output = export_markdown(self.config, render_context=self.context)
        text = output.read_text(encoding="utf-8")
        self.assertEqual(output, self.root / "out/Host Unicode 書.md")
        self.assertLess(text.index("Unicode 書"), text.index("Cell"))
        self.assertLess(text.index("Cell"), text.index("Other content"))
        self.assertLess(text.index("Other content"), text.index("Pathless body"))
        for expected in ('[child](#chapter-2--cell)', '[child start](#chapter-2--start)',
                         '[second](#chapter-3--same)', '[parent](#chapter-1--same)',
                         '[self](#chapter-2--cell)', '<a id="chapter-2--cell"></a>',
                         '[local](#chapter-4--spot)', '<a id="chapter-4--start"></a>'):
            self.assertIn(expected, text)
        self.assertIn('`<a id="code"></a>`', text)
        self.assertIn('<a id="fenced"></a>', text)
        self.assertIn('{{#include absent.md}}', text)
        self.assertNotIn("SOURCE MUST NOT BE READ", text)
        self.assertEqual(original, self.source.read_bytes())
        self.assertFalse((self.src / "virtual/child.md").exists())

    def test_typst_links_explicit_table_list_anchors_and_code(self):
        self.tree()
        text = export_typst(self.config, render_context=self.context).read_text(encoding="utf-8")
        for label in ('chapter-1--same', 'chapter-2--same', 'chapter-3--same',
                      'chapter-2--cell', 'chapter-2--list', 'chapter-4--start'):
            self.assertIn('<' + label + '>', text)
        self.assertIn('#link(<chapter-2--cell>)[child]', text)
        self.assertIn('[#box(width: 0pt, height: 0pt)[] <chapter-2--cell>Cell]', text)
        self.assertIn('#raw("<a id=\\"code\\"></a>")', text)
        self.assertNotIn('<chapter-2--code>', text)
        self.assertNotIn('<chapter-2--fenced>', text)

    def test_collision_ids_and_duplicate_h1_are_unique(self):
        self.capture([chapter("Test", '# Same\n\n<a id="same"></a>\n\n# Same\n'
                              '[explicit](#same)\n', "test.md")])
        md = export_book(self.config, render_context=self.context).read_text(encoding="utf-8")
        self.assertIn('<a id="chapter-1--same"></a>\n# Same', md)
        self.assertIn('<a id="chapter-1--same-1"></a>', md)
        self.assertIn('<a id="chapter-1--same-2"></a>\n# Same', md)
        self.assertIn('[explicit](#chapter-1--same-1)', md)
        typ = export_typst(self.config, render_context=self.context).read_text(encoding="utf-8")
        self.assertIn('#link(<chapter-1--same-1>)[explicit]', typ)

    def test_processed_images_use_host_source_provenance(self):
        (self.src / "images").mkdir()
        (self.src / "images/pixel.png").write_bytes(b"pixel")
        self.capture([chapter("Generated", '# Generated\n![pixel](images/pixel.png)',
                              "virtual/nonexistent.md", "real.md")])
        md = export_markdown(self.config, render_context=self.context).read_text(encoding="utf-8")
        self.assertIn('pixel', md)
        self.assertNotIn('![pixel]', md)
        self.assertFalse(list((self.root / 'out').glob('*_assets')))
        typ = export_typst(self.config, render_context=self.context)
        assets = list(typ.parent.glob("*_assets/*"))
        self.assertEqual([p.read_bytes() for p in assets], [b"pixel"])
        self.capture([chapter("Generated", '![pixel](../lost/pixel.png)', "virtual.md")])
        with self.assertRaisesRegex(ExportError, "image referenced.*does not exist"):
            export_typst(self.config, render_context=self.context)

    def test_unicode_fragment_duplicate_heading_alias_and_physical_link(self):
        self.capture([chapter("Generated", '# Unicode `書`\n\n## Details\n\n## Details\n'
                              '[unicode](#unicode-書) [duplicate](#details-1)\n'
                              '[physical](../real.html#unicode-書)\n'
                              '`[literal](../real.html#unicode-書)`\n',
                              'virtual/new.md', 'real.md')])
        md = export_markdown(self.config, render_context=self.context).read_text(encoding="utf-8")
        self.assertIn('[unicode](#chapter-1--unicode-書)', md)
        self.assertIn('[duplicate](#chapter-1--details-1)', md)
        self.assertIn('[physical](#chapter-1--unicode-書)', md)
        self.assertIn('`[literal](../real.html#unicode-書)`', md)
        typ = export_typst(self.config, render_context=self.context).read_text(encoding="utf-8")
        self.assertIn('#link(<chapter-1--unicode-書>)[physical]', typ)
        self.assertIn('== Details <chapter-1--details-1>', typ)

    def test_absolute_container_provenance_is_ignored(self):
        (self.src / 'image.png').write_bytes(b'host')
        self.capture([chapter('Generated', '![image](image.png)', 'new.md', '/book/content/new.md')])
        output = export_typst(self.config, render_context=self.context)
        self.assertIn('#image(', output.read_text(encoding='utf-8'))
        self.assertTrue(output.is_relative_to(self.root / 'out'))

    def test_duplicate_explicit_anchors_are_reported(self):
        self.capture([chapter('Duplicate', '<a id="id"></a>\n<a id=\'id\'></a>', 'new.md')])
        with self.assertRaisesRegex(ExportError, 'duplicate explicit anchor'):
            export_typst(self.config, render_context=self.context)

    def test_pdf_binding_consumes_same_tree(self):
        self.tree()
        compiled = []

        def compile(path, *, output, format):
            compiled.append(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(format, "pdf")
            Path(output).write_bytes(b"mock pdf")

        with patch.dict(sys.modules, {"typst": types.SimpleNamespace(compile=compile)}):
            output = export_pdf(self.config, render_context=self.context)
        self.assertEqual(output.read_bytes(), b"mock pdf")
        self.assertIn("Other content", compiled[0])
        self.assertIn("Pathless body", compiled[0])
        self.assertIn("<chapter-2--cell>", compiled[0])

    def test_malformed_contexts_fail_as_export_errors(self):
        invalid = [None, [], {}, {"book": []}, {"book": {"items": []}},
                   {"book": {"items": [chapter("Empty", " ")]}},
                   {"book": {"items": [chapter("X", "x", "../outside.md")]}},
                   {"book": {"items": [{"Chapter": {"name": "X", "content": 1}}]}},
                   {"book": {"items": [{"Chapter": {"name": "X", "content": "x", "sub_items": {}}}]}},
                   {"book": {"items": [chapter("X", "x", "x.md"), chapter("X", "x", "x.md")]}}]
        for value in invalid:
            with self.subTest(value=value):
                self.context.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(ExportError):
                    export_markdown(self.config, render_context=self.context)
        self.context.write_text("{bad json", encoding="utf-8")
        with self.assertRaisesRegex(ExportError, "cannot read render context"):
            export_markdown(self.config, render_context=self.context)

    def test_windows_relative_paths_and_image_provenance_are_normalized(self):
        nested = self.src / 'nested'
        nested.mkdir()
        (nested / 'original.md').write_text('Source remains unread', encoding='utf-8')
        (nested / 'asset.png').write_bytes(b'Image bytes')
        self.capture([
            chapter('Main', '# Main\n\n[Child](virtual/page.md#spot)\n', 'real.md'),
            chapter('Child', '# Child\n\n<a id="spot"></a>\n\n![Image](asset.png)\n',
                    'virtual\\page.md', 'nested\\original.md')])
        markdown = export_markdown(self.config, render_context=self.context).read_text(encoding='utf-8')
        self.assertIn('[Child](#chapter-2--spot)', markdown)
        self.assertIn('Image', markdown)
        self.assertNotIn('![Image]', markdown)
        typst = export_typst(self.config, render_context=self.context).read_text(encoding='utf-8')
        self.assertIn('#link(<chapter-2--spot>)[Child]', typst)
        self.assertEqual(len(list((self.root / 'out/Host Unicode 書_assets').glob('*.png'))), 1)

    def test_windows_drive_and_traversal_chapter_paths_are_rejected(self):
        for value in ('C:\\outside.md', 'C:outside.md', '..\\outside.md', '\\\\host\\share\\file.md'):
            with self.subTest(value=value):
                self.capture([chapter('Invalid', '# Invalid', value)])
                with self.assertRaises(ExportError):
                    export_markdown(self.config, render_context=self.context)

    def test_cli_accepts_render_context(self):
        self.tree()
        result = subprocess.run([sys.executable, str(ROOT / "scripts/md-book-builder/exporter/export_book.py"),
                                 str(self.config), "--render-context", str(self.context)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Other content", Path(result.stdout.strip()).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
