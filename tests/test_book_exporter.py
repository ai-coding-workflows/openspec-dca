import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "book-exporter"))

from export_book import ExportError, export_book, export_typst  # noqa: E402
from markdown_to_typst import MarkdownToTypst  # noqa: E402


class BookExporterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "content"
        self.source.mkdir()
        self.book_toml = self.root / "book.toml"
        self.book_toml.write_text(
            '[book]\ntitle = "Combined Guide"\nsrc = "content"\n'
            '[build]\nbuild-dir = "generated/book"\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_uses_summary_order_expands_includes_and_rewrites_content(self):
        self.write(
            "content/SUMMARY.md",
            "# Contents\n\n- [Introduction](README.md)\n- [Chapter](nested/chapter.md)\n",
        )
        self.write(
            "content/README.md",
            "# Introduction\n\nSee [the chapter](nested/chapter.md).\n",
        )
        self.write(
            "content/nested/chapter.md",
            "# Chapter Two\n\nSee [the introduction](../README.md).\n\n"
            "{{#include ../../snippets/part.md}}\n\n![Diagram](diagram.png)\n",
        )
        self.write("snippets/part.md", "Included text.\n\n{{#include nested.md}}\n")
        self.write("snippets/nested.md", "Nested include.\n")

        output = export_book(self.book_toml)
        content = output.read_text(encoding="utf-8")

        self.assertEqual(output, self.root / "generated/book/Combined Guide.md")
        self.assertLess(content.index("# Introduction"), content.index("# Chapter Two"))
        self.assertIn("[the chapter](#chapter-two)", content)
        self.assertIn("[the introduction](#introduction)", content)
        self.assertIn("Included text.", content)
        self.assertIn("Nested include.", content)
        self.assertIn("Diagram", content)
        self.assertNotIn("{{#include", content)
        self.assertNotIn("![Diagram]", content)

    def test_missing_include_is_reported(self):
        self.write("content/SUMMARY.md", "[Intro](README.md)\n")
        self.write("content/README.md", "# Intro\n\n{{#include absent.md}}\n")

        with self.assertRaisesRegex(ExportError, "does not exist: absent.md"):
            export_book(self.book_toml)

    def test_include_cycle_is_reported(self):
        self.write("content/SUMMARY.md", "[Intro](README.md)\n")
        self.write("content/README.md", "# Intro\n\n{{#include ../one.md}}\n")
        self.write("one.md", "{{#include two.md}}\n")
        self.write("two.md", "{{#include one.md}}\n")

        with self.assertRaisesRegex(ExportError, "include cycle detected"):
            export_book(self.book_toml)

    def test_missing_chapter_is_reported(self):
        self.write("content/SUMMARY.md", "[Missing](missing.md)\n")

        with self.assertRaisesRegex(ExportError, "chapter listed.*missing.md"):
            export_book(self.book_toml)

    def test_typst_conversion_covers_common_blocks_and_mermaid(self):
        tick = chr(96)
        markdown = (
            "# Introduction\n\n"
            "Text with **strong**, *emphasis*, and [a link](https://example.org).\n\n"
            "## Details\n\n"
            "- [ ] Prepare\n- [x] Done\n\n"
            "| Name | State |\n| --- | --- |\n| Alpha | Ready |\n\n"
            "> Quoted text.\n\n"
            f"{tick * 3}mermaid\nflowchart TD\n  A --> B\n{tick * 3}\n"
        )

        result = MarkdownToTypst("introduction").convert(markdown)

        self.assertIn("= Introduction <chapter-introduction--introduction>", result)
        self.assertIn("#strong[strong]", result)
        self.assertIn("#emph[emphasis]", result)
        self.assertIn('#link("https://example.org")[a link]', result)
        self.assertIn("== Details <chapter-introduction--details>", result)
        self.assertIn("- [ ] Prepare", result)
        self.assertIn("- [x] Done", result)
        self.assertIn("#table(columns: 2", result)
        self.assertIn("#quote(block: true)", result)
        self.assertIn('lang: "mermaid", block: true', result)

    def test_typst_output_rewrites_cross_chapter_links_and_copies_included_images(self):
        self.write(
            "content/SUMMARY.md",
            "[Introduction](README.md)\n- [Second chapter](second.md)\n",
        )
        self.write(
            "content/README.md",
            "# Introduction\n\nSee [the details](second.md#details).\n"
            "\n{{#include ../snippets/image.md}}\n",
        )
        self.write("content/second.md", "# Second chapter\n\n## Details\n\nContent.\n")
        self.write(
            "snippets/image.md", "![A local image](../content/media/pixel.png)\n"
        )
        self.write("content/media/pixel.png", "image bytes")
        self.write(
            "simple.typ",
            "#let title = {{title}}\n{{content}}\n",
        )

        output = export_typst(self.book_toml, Path("simple.typ"))
        content = output.read_text(encoding="utf-8")
        assets = list((self.root / "generated/book").glob("Combined Guide_assets/*"))

        self.assertIn('#let title = "Combined Guide"', content)
        self.assertIn("#link(<chapter-second-chapter--details>)[the details]", content)
        self.assertIn("#image(", content)
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].read_bytes(), b"image bytes")

    def test_remote_typst_images_are_rejected(self):
        self.write("content/SUMMARY.md", "[Intro](README.md)\n")
        self.write(
            "content/README.md", "# Intro\n\n![Logo](https://example.org/logo.png)\n"
        )

        with self.assertRaisesRegex(ExportError, "remote image cannot be included"):
            export_typst(self.book_toml, Path("simple.typ"))


if __name__ == "__main__":
    unittest.main()
