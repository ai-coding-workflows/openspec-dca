"""Optional, structural DDD metadata checks; no handbook or application required."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src/schemas/ddd/helpers/check.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("ddd_metadata_check", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MetadataCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.module = load_checker()
        self.check = self.module.check_project

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def adr(self, name="openspec/specs/context/architectural-decisions/adr-001.md",
            identity="ADR-context-001", status="Proposed", date="Unknown (reconstructed)",
            scope="The operations team", extra=""):
        return self.write(name, f"# {identity}: Keep established boundaries\n\n"
                         f"Status: {status}\nDate: {date}\nScope: {scope}\n\n{extra}")

    def catalog(self, decisions=(), dependencies=()):
        self.write("openspec/specs/context/spec.md", "# Contract\n")
        self.write("openspec/catalog.json", json.dumps({"schema_version": 1, "specs": [
            {"id": "context", "path": "openspec/specs/context/spec.md",
             "depends_on": list(dependencies), "decisions": list(decisions)}]}))

    def test_checker_uses_adjacent_model_without_overwriting_existing_module_cache(self):
        foreign = object()
        bytecode = sys.dont_write_bytecode
        with patch.dict(sys.modules, {'model': foreign, '_ddd_model': foreign}):
            checker = load_checker()
            self.assertIs(sys.modules['model'], foreign)
            self.assertIs(sys.modules['_ddd_model'], foreign)
            self.assertEqual(Path(checker.model.__file__), SCRIPT.with_name('model.py'))
            self.assertEqual(sys.dont_write_bytecode, bytecode)
            self.assertEqual(checker.check_project(self.root)['status'], 'ok')

    def test_renderer_and_validator_share_the_same_parsed_records(self):
        path = self.adr(extra='<!-- preserved source -->\n\n```text\nStatus: Not metadata\n```\n')
        original = path.read_text()
        records = self.module.model.decisions(self.root)
        self.assertEqual(records[0].text, original)
        self.assertEqual(records[0].status, 'Proposed')
        validated = self.module.validate_decisions(self.root, records)
        self.assertEqual(validated, self.check(self.root)['decisions']['records'])
        self.assertNotIn('text', validated[0])
        # Validation operates on the loaded snapshot, not a second metadata parse.
        path.write_text('# Changed after reading\n')
        self.assertEqual(self.module.validate_decisions(self.root, records), validated)
        with self.assertRaises(ValueError):
            self.check(self.root)

    def test_incomplete_and_duplicate_metadata_are_reader_data_but_validation_errors(self):
        path = self.adr(extra='Status: Another value\n')
        record = self.module.model.read_adr(path, self.root)
        self.assertEqual(record.field_values('status'), ('Proposed', 'Another value'))
        self.assertIsNone(record.status)
        with self.assertRaisesRegex(ValueError, 'Status'):
            self.module.validate_decisions(self.root, [record])
        path.write_text('# ADR-X-1: Missing metadata\n')
        record = self.module.model.read_adr(path, self.root)
        self.assertIsNone(record.date)
        with self.assertRaisesRegex(ValueError, 'Status'):
            self.module.validate_decisions(self.root, [record])

    def test_reader_does_not_resolve_supersession_targets_but_validator_does(self):
        path = self.adr(extra='Superseded by: [Future](adr-missing.md)\n')
        record = self.module.model.read_adr(path, self.root)
        self.assertEqual(record.supersession_targets, ('adr-missing.md',))
        with self.assertRaisesRegex(ValueError, 'Missing supersession'):
            self.module.validate_decisions(self.root, [record])

    def test_no_metadata_is_successful_and_explicitly_skipped(self):
        result = self.check(self.root)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["catalog"]["status"], "skipped")
        self.assertEqual(result["decisions"]["status"], "skipped")
        self.assertEqual(result["decisions"]["count"], 0)
        self.assertIn("Structural", result["note"])
        json.dumps(result)

    def test_ddd_without_arc42_and_human_scope(self):
        self.adr()
        self.catalog()
        result = self.check(self.root)
        self.assertEqual(result["catalog"]["owners"], 1)
        self.assertEqual(result["decisions"]["count"], 1)
        record = result["decisions"]["records"][0]
        self.assertEqual(record["scope"], "The operations team")
        self.assertEqual(record["date"], "Unknown (reconstructed)")
        self.assertFalse((self.root / "openspec/system-architecture").exists())

    def test_system_record_without_catalog_and_freeform_status(self):
        self.adr("openspec/system-architecture/security/architectural-decisions/adr-1.md",
                 status="Observed; authority unknown", scope="System security")
        result = self.check(self.root)
        self.assertEqual(result["catalog"]["status"], "skipped")
        self.assertEqual(result["decisions"]["records"][0]["status"],
                         "Observed; authority unknown")

    def test_optional_status_allowlist(self):
        self.adr(status="Custom project status")
        self.check(self.root, statuses=("Custom project status",))
        with self.assertRaisesRegex(ValueError, "[Ss]tatus"):
            self.check(self.root, statuses=("Accepted",))

    def test_catalog_references_outside_default_discovery(self):
        adr = "openspec/changes/proposal/architectural-decisions/custom.md"
        self.adr(adr)
        index = "docs/architectural-decisions.md"
        self.write(index, "# Architectural decisions\n\nAssessment: reuse existing.\n")
        self.catalog([adr, index])
        result = self.check(self.root, decision_paths=("docs",))
        self.assertEqual([r["path"] for r in result["decisions"]["records"]], [adr])

    def test_native_changes_are_not_discovered_by_default(self):
        self.adr("openspec/changes/new/architectural-decisions/adr-bad.md", status="")
        self.assertEqual(self.check(self.root)["decisions"]["count"], 0)
        with self.assertRaisesRegex(ValueError, "Status"):
            self.check(self.root, decision_paths=("openspec/changes/new",))

    def test_catalog_validation_is_reused(self):
        self.catalog(dependencies=["missing"])
        with self.assertRaisesRegex(ValueError, "Unknown dependency"):
            self.check(self.root)

    def test_missing_catalog_and_missing_catalog_reference_fail(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check(self.root, catalog="openspec/catalog.json")
        self.catalog(["docs/missing.md"])
        with self.assertRaisesRegex(ValueError, "Missing file"):
            self.check(self.root)

    def test_nondefault_catalog(self):
        self.catalog()
        (self.root / "openspec/catalog.json").rename(self.root / "inventory.json")
        self.assertEqual(self.check(self.root)["catalog"]["status"], "skipped")
        self.assertEqual(self.check(self.root, catalog="inventory.json")["catalog"]["owners"], 1)

    def test_missing_and_empty_fields(self):
        path = self.adr()
        original = path.read_text()
        for field in ("Status", "Date", "Scope"):
            for replacement in ("", f"{field}: "):
                with self.subTest(field=field, replacement=replacement):
                    lines = [replacement if line.startswith(field + ":") else line
                             for line in original.splitlines()]
                    path.write_text("\n".join(lines))
                    with self.assertRaisesRegex(ValueError, field):
                        self.check(self.root)
        path.write_text(original)
        self.check(self.root)

    def test_invalid_title_and_explicit_nonrecord(self):
        for title in ("# ADR-context-001: ", "# ADR-: Decision", "# ADR-context-001", "# Index"):
            self.write("records/adr-1.md", title + "\nStatus: Proposed\nDate: unknown\nScope: team\n")
            with self.subTest(title=title), self.assertRaisesRegex(ValueError, "ADR"):
                self.check(self.root, decision_paths=("records/adr-1.md",))

    def test_indices_and_assessments_skipped(self):
        base = "openspec/specs/context/architectural-decisions/"
        for name in ("README.md", "index.md", "architectural-decisions.md", "assessment.md"):
            self.write(base + name, "# Architectural decisions\n\nNo ADR required.\n")
        self.adr(base + "custom-name.md")
        self.assertEqual(self.check(self.root)["decisions"]["count"], 1)

    def test_explicit_paths_override_default_discovery_and_deduplicate(self):
        self.adr(status="")  # invalid default record is outside the explicit selection
        self.adr("records/adr-1.md")
        result = self.check(self.root, decision_paths=("records", "records/adr-1.md"))
        self.assertEqual(result["decisions"]["count"], 1)
        self.assertEqual(result["decisions"]["records"][0]["path"], "records/adr-1.md")

    def test_duplicate_ids_are_scoped_to_directory_and_scope(self):
        self.adr("records/adr-1.md", scope="Team A")
        self.adr("records/adr-2.md", scope="Team B")
        self.adr("other/adr-1.md", scope="Team A")
        self.assertEqual(self.check(self.root, decision_paths=("records", "other"))["decisions"]["count"], 3)
        self.adr("records/adr-3.md", scope="Team A")
        with self.assertRaisesRegex(ValueError, "Duplicate ADR"):
            self.check(self.root, decision_paths=("records", "other"))

    def test_supersession_links_are_checked_without_lifecycle_rules(self):
        self.adr("records/adr-old.md", status="Project-specific", extra="Superseded by: [new](adr-new.md#decision)\n")
        self.adr("records/adr-new.md", identity="ADR-context-002", status="Proposed",
                 extra="Supersedes: [previous](adr-old.md) and [external](https://example.com/adr)\n")
        self.assertEqual(self.check(self.root, decision_paths=("records",))["decisions"]["count"], 2)
        self.adr("records/adr-new.md", identity="ADR-context-002",
                 extra="Supersedes: [missing](missing.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check(self.root, decision_paths=("records",))

    def test_supersession_reference_style_links(self):
        self.adr("records/adr-1.md", extra="Supersedes: [old][history]\n\n[history]: missing.md\n")
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check(self.root, decision_paths=("records",))

    def test_explicit_paths_and_symlinks_cannot_escape(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "adr-1.md").write_text("# ADR-external-001: external\n")
        (self.root / "linked.md").symlink_to(outside / "adr-1.md")
        (self.root / "linked-dir").symlink_to(outside, target_is_directory=True)
        for name in ("../outside/adr-1.md", str(outside / "adr-1.md"), "linked.md", "linked-dir"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "relative|escapes"):
                self.check(self.root, decision_paths=(name,))
        self.adr("records/adr-1.md")
        (self.root / "records/adr-linked.md").symlink_to(outside / "adr-1.md")
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.check(self.root, decision_paths=("records",))

    def test_internal_symlinks_are_contained_and_deduplicated(self):
        self.adr("records/adr-1.md")
        (self.root / "alias").symlink_to(self.root / "records", target_is_directory=True)
        (self.root / "records/loop").symlink_to(self.root / "records", target_is_directory=True)
        result = self.check(self.root, decision_paths=("alias", "records/adr-1.md"))
        self.assertEqual(result["decisions"]["count"], 1)

    def test_cli_in_copied_helper_does_not_write_bytecode_or_metadata(self):
        helper = self.root / "openspec/ddd"
        helper.mkdir(parents=True)
        for source in (SCRIPT, SCRIPT.with_name("ddd.py"), SCRIPT.with_name("model.py"),
                       SCRIPT.with_name("project_root.py")):
            (helper / source.name).write_bytes(source.read_bytes())
        self.adr()
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        result = subprocess.run([sys.executable, str(helper / "check.py")], cwd=self.root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_symlink_selected_by_adr_filename_still_requires_record_title(self):
        self.write("docs/history.md", "# History\n")
        directory = self.root / "records"
        directory.mkdir()
        (directory / "adr-1.md").symlink_to(self.root / "docs/history.md")
        with self.assertRaisesRegex(ValueError, "ADR"):
            self.check(self.root, decision_paths=("records",))

    def test_markdown_local_links_with_angle_paths_and_parentheses(self):
        self.write("records/history (old).md", "Historical decision\n")
        self.adr("records/adr-1.md", extra='Supersedes: [old](<history (old).md> "History")\n')
        self.check(self.root, decision_paths=("records",))
        self.write("records/history(old).md", "Historical decision\n")
        self.adr("records/adr-1.md", extra="Supersedes: [old](history(old).md)\n")
        self.check(self.root, decision_paths=("records",))

    def test_missing_explicit_path(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check(self.root, decision_paths=("missing",))

    def test_supersession_escape(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("history")
        self.adr("records/adr-1.md", extra="Supersedes: [history](../../outside.md)\n")
        with self.assertRaisesRegex(ValueError, "escapes"):
            self.check(self.root, decision_paths=("records",))

    def test_comments_and_code_are_not_metadata(self):
        self.write("records/adr-1.md", "# ADR-context-001: Decision\n<!--\nStatus: Proposed\n-->\n"
                   "```text\nDate: unknown\nScope: team\n```\n")
        with self.assertRaisesRegex(ValueError, "Status"):
            self.check(self.root, decision_paths=("records",))

    def test_read_only(self):
        self.adr()
        self.catalog()
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        self.check(self.root)
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_cli_success_default_root_options_and_failure(self):
        empty = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root)], cwd=self.root,
                               capture_output=True, text=True)
        self.assertEqual(empty.returncode, 0, empty.stderr)
        self.assertEqual(json.loads(empty.stdout)["catalog"]["status"], "skipped")
        self.adr("records/adr-1.md", status="Custom")
        args = [sys.executable, str(SCRIPT), "--root", str(self.root),
                "--decisions", "records", "--decisions", "records/adr-1.md",
                "--status", "Custom", "--status", "Proposed"]
        success = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(json.loads(success.stdout)["decisions"]["count"], 1)
        failure = subprocess.run(args + ["--catalog", "missing.json"], capture_output=True, text=True)
        self.assertNotEqual(failure.returncode, 0)
        self.assertEqual(json.loads(failure.stdout)["status"], "error")
        self.assertIn("Missing", json.loads(failure.stdout)["error"])


if __name__ == "__main__":
    unittest.main()
