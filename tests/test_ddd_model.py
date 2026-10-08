"""Catalog-neutral ADR parsing and safe selection contracts."""
import importlib.util
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "src/schemas/ddd/helpers/model.py"


def load_model():
    spec = importlib.util.spec_from_file_location("_ddd_model_tests", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdrModelTests(unittest.TestCase):
    def setUp(self):
        self.model = load_model()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, name, text="# ADR-1: Decision\nStatus: Anything\nDate: Unknown\nScope: Free prose\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def test_discovery_reads_each_source_once_even_with_repeated_catalog_references(self):
        path = self.file('openspec/specs/team/architectural-decisions/adr-one.md')
        reads = []
        original = Path.read_bytes

        def read(source):
            reads.append(source)
            return original(source)

        with patch.object(Path, 'read_bytes', read):
            records = self.model.decisions(self.root, references=[path.relative_to(self.root)] * 2)
        self.assertEqual(len(records), 1)
        self.assertEqual(reads.count(path), 1)

    def test_canonical_frozen_record_and_freeform_metadata(self):
        path = self.file("adr-one.md", "# ADR-alpha: Human decision ###\nsTaTuS:  Awaiting discussion  \nDate: whenever possible\nScope: The whole system\n")
        record = self.model.read_adr(path, self.root)
        self.assertEqual((record.path, record.id, record.title), ("adr-one.md", "ADR-alpha", "Human decision"))
        self.assertEqual((record.status, record.date, record.scope), ("Awaiting discussion", "whenever possible", "The whole system"))
        self.assertEqual(record.field_values("STATUS"), ("Awaiting discussion  ",))
        self.assertEqual(record.field_values("absent"), ())
        with self.assertRaises(FrozenInstanceError):
            record.id = "other"

    def test_missing_empty_duplicate_fields_are_data_not_validation(self):
        record = self.model.read_adr(self.file("adr-empty.md", "Status: \nStatus: Accepted\nDate:\n"), self.root)
        self.assertIsNone(record.id)
        self.assertIsNone(record.title)
        self.assertEqual(record.field_values("status"), ("", "Accepted"))
        self.assertEqual(record.field_values("date"), ("",))
        self.assertEqual(record.field_values("scope"), ())
        self.assertEqual((record.status, record.date, record.scope), (None, None, None))

    def test_original_crlf_comments_and_examples_retained_but_not_parsed(self):
        text = ("<!--\r\n# ADR-fake: Comment\r\nStatus: fake\r\n-->\r\n"
                "```md\r\n# ADR-fake: Fence\r\nDate: fake\r\n```\r\n"
                "~~~\r\nScope: fake\r\n~~~\r\n"
                "    Status: fake\r\n\tDate: fake\r\n"
                "# ADR-real: Actual\r\nStatus: Proposed\r\nDate: unknown\r\nScope: global\r\n")
        record = self.model.read_adr(self.file("adr-real.md", text), self.root)
        self.assertEqual(record.text, text)
        self.assertEqual((record.id, record.status, record.date, record.scope), ("ADR-real", "Proposed", "unknown", "global"))

    def test_supersession_destinations_are_raw_and_do_not_require_files(self):
        text = ("# ADR-1: Links\nSupersedes: [local](missing(a).md#x) [angle](<missing space.md> \"Title\")\n"
                "- [external](https://example.org/adr) [fragment](#x)\n"
                "- [by reference][  OTHER label ] [shortcut] ![image](ignored.md)\n"
                "Superseded by: [collapsed][]\n\n"
                "[other label]: ../elsewhere.md \"Title\"\n[shortcut]: <shortcut.md>\n[collapsed]: successor.md\n")
        record = self.model.read_adr(self.file("adr-links.md", text), self.root)
        self.assertEqual(record.supersession_targets, ("missing(a).md#x", "missing space.md", "https://example.org/adr", "#x", "../elsewhere.md", "shortcut.md", "successor.md"))

    def test_undefined_explicit_reference_errors_but_plain_prose_does_not(self):
        path = self.file("adr-links.md", "Supersedes: [old][undefined]\n")
        with self.assertRaisesRegex(ValueError, "Undefined"):
            self.model.read_adr(path, self.root)
        path.write_text("Supersedes: none [historical prose]\n", encoding="utf-8")
        self.assertEqual(self.model.read_adr(path, self.root).supersession_targets, ())

    def test_default_discovery_and_explicit_replacement_plus_references(self):
        names = ["openspec/specs/z/architectural-decisions/adr-z.md", "openspec/system-architecture/architectural-decisions/a.md"]
        for name in names:
            self.file(name)
        for name in ("openspec/changes/x/architectural-decisions/adr-change.md", "openspec/specs/z/decisions/adr-legacy.md", "openspec/specs/adr-outside.md", "custom/adr-custom.md"):
            self.file(name)
        for name in ("readme", "index", "assessment", "assessments", "architectural-decisions", "adr-index", "adr-assessment", "adr-assessments"):
            self.file(f"openspec/specs/z/architectural-decisions/{name}.md")
        self.file("openspec/specs/z/architectural-decisions/template.md", "```\n# ADR-fake: Template\n```\n")
        self.assertEqual([r.path for r in self.model.decisions(self.root)], sorted(names))
        records = self.model.decisions(self.root, decision_paths=("custom",), references=(names[0], "openspec/specs/z/architectural-decisions/index.md"))
        self.assertEqual([r.path for r in records], sorted(["custom/adr-custom.md", names[0]]))
        with self.assertRaises(ValueError):
            self.model.decisions(self.root, references=("missing.md",))
        with self.assertRaises(ValueError):
            self.model.decisions(self.root, decision_paths=("openspec/specs/z/architectural-decisions/index.md",))

    def test_explicit_adr_symlink_keeps_alias_selection(self):
        target = self.file("custom/index.md", "Status: Proposed\n")
        alias = self.root / "custom/adr-alias.md"
        alias.symlink_to(target)
        records = self.model.decisions(self.root, decision_paths=("custom",))
        self.assertEqual([r.path for r in records], ["custom/index.md"])
        self.assertEqual(len(self.model.decisions(self.root, decision_paths=("custom/adr-alias.md",))), 1)

    def test_internal_symlink_cycles_deduplicate_and_escapes_fail(self):
        self.file("custom/adr-a.md")
        (self.root / "custom/loop").symlink_to(self.root / "custom", target_is_directory=True)
        self.assertEqual(len(self.model.decisions(self.root, decision_paths=("custom",))), 1)
        with tempfile.TemporaryDirectory() as outside:
            foreign = Path(outside) / "adr-outside.md"
            foreign.write_text("# ADR-x: Outside\n", encoding="utf-8")
            link = self.root / "custom/adr-escape.md"
            link.symlink_to(foreign)
            with self.assertRaisesRegex(ValueError, "escapes"):
                self.model.read_adr(link, self.root)
            with self.assertRaisesRegex(ValueError, "escapes"):
                self.model.decisions(self.root, decision_paths=("custom",))
            link.unlink()
            (self.root / "custom/escape").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "escapes"):
                self.model.decisions(self.root, decision_paths=("custom",))

    def test_path_guards_and_sequence_guards(self):
        for name in ("", "/tmp", "../outside"):
            with self.assertRaises(ValueError):
                self.model.project_path(self.root, name)
        with self.assertRaises(ValueError):
            self.model.read_adr(self.root, self.root)
        for kwargs in ({"decision_paths": "custom"}, {"references": "custom"}):
            with self.assertRaises(ValueError):
                self.model.decisions(self.root, **kwargs)

    def test_model_imports_standalone_without_catalog_or_book_modules(self):
        standalone = self.root / "model.py"
        standalone.write_bytes(SOURCE.read_bytes())
        spec = importlib.util.spec_from_file_location("_standalone_adr_model", standalone)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.read_adr(self.file("adr-one.md"), self.root).id, "ADR-1")

    def test_discovery_does_not_validate_identity_or_catalog(self):
        self.file("custom/adr-one.md")
        self.file("custom/adr-two.md")
        self.file("openspec/catalog.json", "not JSON")
        records = self.model.decisions(self.root, decision_paths=("custom",))
        self.assertEqual([record.id for record in records], ["ADR-1", "ADR-1"])

    def test_raw_absolute_and_file_url_targets_are_not_validated_by_reader(self):
        path = self.file("adr-links.md", "Supersedes: [absolute](/absent.md) [file](file:///absent.md)\n")
        self.assertEqual(self.model.read_adr(path, self.root).supersession_targets,
                         ("/absent.md", "file:///absent.md"))

    def test_old_heading_and_bold_metadata_are_not_supported(self):
        record = self.model.read_adr(self.file("adr-old.md", "# ADR-1 — Old heading\n**Status:** Accepted\n**Date:** today\n**Scope:** system\n"), self.root)
        self.assertEqual((record.id, record.title, record.status, record.date, record.scope), (None, None, None, None, None))


if __name__ == "__main__":
    unittest.main()
