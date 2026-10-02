#!/usr/bin/env python3
"""Check handbook source references and optionally built local HTML references."""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from book_paths import read_book_paths
from book_selection import select_book


def without_code(text: str) -> str:
    return re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", "", text)

class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])

def validate_html(output: Path) -> None:
    pages = {path.resolve(): Page(path.read_text()) for path in output.rglob("*.html")}
    if not pages:
        raise ValueError("Documentation build produced no HTML pages")
    for path, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path.startswith('/'):
                target = output / unquote(parsed.path).lstrip('/')
            else:
                target = path.parent / unquote(parsed.path) if parsed.path else path
            if target.is_dir():
                target = target / "index.html"
            target = target.resolve()
            if not target.is_relative_to(output.resolve()) or not target.exists():
                raise ValueError(f"Broken rendered link {link} in {path.name}")
            if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                raise ValueError(f"Missing rendered anchor {link} in {path.name}")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-b", "--book", help="book alias, directory, or book.toml path")
    parser.add_argument("--map", type=Path, help="book mapping TOML (default: docs-books.toml)")
    parser.add_argument("--rendered", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    paths = read_book_paths(select_book(root, args.book, args.map))
    source_root = paths.repository if args.book else root
    for page in source_root.rglob("*.md"):
        if page.is_relative_to(paths.output_root):
            continue
        content = without_code(page.read_text())
        references = re.findall(r"\{\{#include\s+([^}\s]+)\s*\}\}", content)
        references += re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", content)
        for ref in references:
            url = urlsplit(ref)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (page.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(root) or not target.exists():
                raise ValueError(f"Missing or external local reference {ref} in {page.relative_to(root)}")
    if args.rendered:
        validate_html(paths.build_dir)
    print("Handbook references verified" + (" (source and rendered)" if args.rendered else " (source)"))


if __name__ == "__main__":
    main()
