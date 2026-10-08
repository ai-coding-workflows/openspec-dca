"""Build the distributable mdBook template in an isolated adopting project."""

from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "src/addons/mdbook"


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
        self.has_diagram = False

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "script" and "src" in attributes:
            self.sources.append(attributes["src"])
        if "mermaid" in attributes.get("class", "").split():
            self.has_diagram = True


@unittest.skipUnless(shutil.which("mdbook") and shutil.which("mdbook-mermaid"),
                     "Install mdbook and mdbook-mermaid for addon integration tests")
class MdBookAddonTests(unittest.TestCase):
    def test_distributed_template_builds_mermaid_with_builder_cached_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            shutil.copytree(ADDON, project)
            page = project / "openspec/system-architecture/README.md"
            page.write_text(page.read_text() + "\n```mermaid\nflowchart LR\n    Client --> Service\n```\n")
            builder = project / "tools/documentation/md-book-builder"
            shutil.copytree(ROOT / "scripts/md-book-builder", builder,
                            ignore=shutil.ignore_patterns(".cache", ".venv", "__pycache__"))
            result = subprocess.run([sys.executable, str(builder / "book.py"), "--root", str(project), "build"],
                                    cwd=project, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = project / "build/book"
            html = (output / "index.html").read_text()
            parsed = Scripts()
            parsed.feed(html)
            self.assertTrue(parsed.has_diagram, "Mermaid preprocessor did not process the fence")
            self.assertIn("Client", html)
            mermaid_sources = [source for source in parsed.sources if "mermaid" in source]
            self.assertEqual(len(mermaid_sources), 2)
            expected = [next((builder / ".cache/scripts/mermaid").glob("*/" + name)).read_bytes()
                        for name in ("mermaid.min.js", "mermaid-init.js")]
            self.assertFalse((project / "theme").exists())
            self.assertIn(".cache/scripts/mermaid/", (project / "book.toml").read_text())
            actual = []
            for source in mermaid_sources:
                parsed_url = urlsplit(source)
                self.assertFalse(parsed_url.scheme or parsed_url.netloc, source)
                asset = (output / unquote(parsed_url.path)).resolve()
                self.assertTrue(asset.is_relative_to(output.resolve()), source)
                actual.append(asset.read_bytes())
            self.assertEqual(actual, expected, "Browser assets must match the selected binary's cache and load order")
