"""Universal, read-only source and rendered book reference checks."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BUILDER = Path(__file__).resolve().parents[1] / "scripts/md-book-builder"
sys.path.insert(0, str(BUILDER))
spec = importlib.util.spec_from_file_location("universal_book_check", BUILDER / "check.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class BookChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "docs"
        self.src.mkdir()

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def validate(self, **kwargs):
        checks.validate_sources(self.root, [self.src], **kwargs)

    def test_source_config_and_default(self):
        config = self.put("book.toml", '[book]\nsrc = "docs"\n')
        paths = checks.read_book_paths(config)
        self.assertEqual(checks.source_directory(paths), self.src)
        config.write_text('[book]\ntitle = "Test"\n')
        self.assertEqual(checks.source_directory(paths), self.root / "src")

    def test_missing_source(self):
        with self.assertRaisesRegex(ValueError, "[Ss]ource.*missing|[Ss]ource.*not found"):
            checks.validate_sources(self.root, [self.root / "absent"])

    def test_valid_include_selections_including_fences(self):
        self.put("sample.txt", "one\n// ANCHOR: demo\ntwo\n// ANCHOR_END: demo\nlast\n")
        for selector in ("", ":1", ":1:3", ":2:", "::3", ":demo"):
            with self.subTest(selector=selector):
                self.put("docs/page.md", '```rust\n{{#include ../sample.txt' + selector + '}}\n```\n')
                self.validate()

    def test_invalid_include_selectors(self):
        self.put("sample.txt", "// ANCHOR: demo-long\ntext\n// ANCHOR_END: demo-long\n")
        for selector in (":0", ":9", ":3:1", ":1:9", ":demo", ":1:2:3"):
            with self.subTest(selector=selector):
                self.put("docs/page.md", '{{#include ../sample.txt' + selector + '}}')
                with self.assertRaises(ValueError):
                    self.validate()

    def test_anchor_names_match_whole_tokens(self):
        self.put("sample.txt", "// ANCHOR: demo.long\ntext\n// ANCHOR_END: demo.long\n")
        self.put("docs/page.md", "{{#include ../sample.txt:demo}}")
        with self.assertRaises(ValueError):
            self.validate()
        self.put("docs/page.md", "{{#include ../sample.txt:demo.long}}")
        self.validate()

    def test_unmatched_anchor_markers(self):
        self.put("docs/page.md", "{{#include ../sample.txt:demo}}")
        for content in ("ANCHOR: demo\nx", "ANCHOR_END: demo", "ANCHOR: demo\nANCHOR_END: other"):
            self.put("sample.txt", content)
            with self.assertRaises(ValueError):
                self.validate()

    def test_includes_recurse_and_detect_cycles(self):
        self.put("docs/page.md", "{{#include ../first.txt}}")
        self.put("first.txt", "{{#include second.txt}}")
        self.put("second.txt", "{{#include first.txt}}")
        with self.assertRaisesRegex(ValueError, "[Cc]ycl"):
            self.validate()
        self.put("second.txt", "{{#include absent.txt}}")
        with self.assertRaises(ValueError):
            self.validate()
        self.put("second.txt", "text")
        self.validate()

    def test_code_protection_and_quoted_links(self):
        self.put("asset space.png", "image")
        self.put("outside.md", "# Outside")
        self.put("docs/page.md", '''```md
[bad](missing.md)
````
`[bad](missing.md)` and ``[bad](missing.md)``
[good](../outside.md#not-checked "optional title")
![image](<../asset%20space.png> 'title')
[web](https://invalid.example/not-fetched) [email](mailto:x@example.com)
''')
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            self.validate()
        self.put("docs/page.md", '[bad](<missing file.md> "title")')
        with self.assertRaises(ValueError):
            self.validate()

    def test_reference_definitions_balanced_paths_and_root_links(self):
        self.put("target(a).md", "text")
        self.put("docs/page.md", '[good](/target(a).md "title")\n[image][pic]\n[pic]: </target(a).md> "title"')
        self.validate()
        self.put("docs/page.md", '[image][pic]\n[pic]: absent.png "title"')
        with self.assertRaises(ValueError):
            self.validate()

    def test_only_sources_and_exclusions(self):
        self.put("unrelated.md", "[bad](missing)")
        self.put("docs/page.md", "ok")
        for folder in (".git", ".venv", "venv", ".cache", "__pycache__", "generated"):
            self.put(f"docs/{folder}/bad.md", "[bad](missing)")
        self.validate(exclude_dirs=[self.src / "generated"])

    def test_local_paths_and_symlink_escapes(self):
        self.put("docs/page.md", "[bad](../../missing)")
        with self.assertRaises(ValueError):
            self.validate()
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "escape.md"
            target.write_text("[bad](missing)")
            (self.src / "escape.md").symlink_to(target)
            self.put("docs/page.md", "ok")
            self.validate()  # escaped scan entries are not followed
            self.put("docs/page.md", "{{#include escape.md}}")
            with self.assertRaises(ValueError):
                self.validate()
            self.put("docs/page.md", "[bad](escape.md)")
            with self.assertRaises(ValueError):
                self.validate()

    def test_html_anchors_root_relative_and_no_network(self):
        output = self.root / "html"
        self.put("html/index.html", '<a href="/nested/#old">x</a><img src="/asset.png"><a href="https://invalid.example">web</a>')
        self.put("html/nested/index.html", '<a name="old"></a><div id="new"></div><a href="#new">x</a>')
        self.put("html/asset.png", "asset")
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            checks.validate_html(output)
        for ref in ("/nested/#absent", "../outside.md", "/missing.png"):
            self.put("html/index.html", f'<a href="{ref}">x</a>')
            with self.assertRaises(ValueError):
                checks.validate_html(output)

    def test_no_html_and_html_symlink_escape(self):
        with self.assertRaisesRegex(ValueError, "no HTML"):
            checks.validate_html(self.root)
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "other.html"
            target.write_text("ok")
            self.put("html/index.html", '<a href="other.html">x</a>')
            (self.root / "html/other.html").symlink_to(target)
            with self.assertRaises(ValueError):
                checks.validate_html(self.root / "html")

    def test_cli_checks_sources_beside_nested_output(self):
        self.put('book.toml', '[book]\nsrc="docs"\n[build]\nbuild-dir="docs/site"\n')
        self.put('docs/page.md', '[Missing](missing.md)')
        result = subprocess.run([sys.executable, str(BUILDER / 'check.py'), '--root', str(self.root)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing.md', result.stderr)

    def test_cli_rendered_checks_existing_output_without_build(self):
        self.put("book.toml", '[book]\nsrc = "docs"\n[build]\nbuild-dir = "html"\n')
        self.put("docs/page.md", "ok")
        command = [sys.executable, str(BUILDER / "check.py"), "--root", str(self.root), "--rendered"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no HTML", result.stderr)
        self.assertFalse((self.root / "html").exists())
        self.put("html/index.html", "ok")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
