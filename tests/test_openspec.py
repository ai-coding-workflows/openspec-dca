"""Compatibility tests; all CLI mutations are confined to disposable project copies."""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec")
CHANGE = "record-return-condition"
spec = importlib.util.spec_from_file_location("builder", ROOT / "scripts/schema-builder/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


@unittest.skipUnless(CLI, "Install OpenSpec 1.13.1 or set OPENSPEC_BIN for integration tests")
class OpenSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(ROOT / "examples/equipment-lending", self.root,
                        ignore=shutil.ignore_patterns("build"))
        builder.build_legacy(self.root / "openspec/schemas/openspec-ddd")
        shutil.copytree(ROOT / "src/schemas/ddd/helpers", self.root / "openspec/ddd")
        self.change = self.root / "openspec/changes" / CHANGE
        self.env = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1",
                        OPENSPEC_NO_UPDATE_CHECK="1", XDG_CONFIG_HOME=str(Path(self.temp.name) / "config"),
                        XDG_DATA_HOME=str(Path(self.temp.name) / "data"))

    def cli(self, *args, json_output=False):
        proc = subprocess.run([CLI, *args], cwd=self.root, env=self.env,
                              text=True, capture_output=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout) if json_output else proc.stdout

    def status(self, change=CHANGE):
        return self.cli("status", "--change", change, "--json", json_output=True)

    def apply(self):
        return self.cli("instructions", "apply", "--change", CHANGE, "--json", json_output=True)

    def test_schema_and_example_validate_strictly(self):
        self.cli("schema", "validate", "openspec-ddd")
        result = self.cli("validate", "--all", "--strict", "--no-interactive")
        self.assertIn("6 passed, 0 failed", result)

    def test_planning_complete_is_not_delivery_complete(self):
        status = self.status()
        self.assertEqual(status["schemaName"], "openspec-ddd")
        self.assertTrue(status["isPlanningComplete"])
        self.assertEqual(len(status["artifactPaths"]["specs"]["existingOutputPaths"]), 4)
        apply = self.apply()
        self.assertEqual(apply["progress"], {"total": 7, "complete": 0, "remaining": 7})
        self.assertEqual(apply["state"], "ready")
        self.assertIn("impact", apply["contextFiles"])

    def test_new_change_uses_project_schema_and_dependency_frontier(self):
        self.cli("new", "change", "second-change")
        first = self.status("second-change")
        self.assertEqual(first["schemaName"], "openspec-ddd")
        states = {x["id"]: x["status"] for x in first["artifacts"]}
        self.assertEqual(states["proposal"], "ready")
        self.assertEqual(states["impact"], "blocked")
        target = self.root / "openspec/changes/second-change"
        shutil.copy2(self.change / "proposal.md", target / "proposal.md")
        states = {x["id"]: x["status"] for x in self.status("second-change")["artifacts"]}
        self.assertEqual(states["impact"], "ready")
        self.assertEqual(states["specs"], "blocked")

    def test_missing_impact_blocks_apply_even_with_existing_tasks(self):
        (self.change / "impact.md").unlink()
        result = self.apply()
        self.assertEqual(result["state"], "blocked")
        self.assertIn("impact", result["missingArtifacts"])

    def test_instructions_include_custom_template_and_project_context(self):
        result = self.cli("instructions", "impact", "--change", CHANGE, "--json", json_output=True)
        self.assertIn("Owner and Consumer Review", result["template"])
        self.assertIn("teaching fixture", result["context"])
        self.assertIn("consumer", result["instruction"])

    def test_no_behavior_change_skips_deltas_without_blocking_apply(self):
        shutil.rmtree(self.change / "specs")
        metadata = self.change / ".openspec.yaml"
        metadata.write_text(metadata.read_text() + "skip_specs: true\n")
        (self.change / "proposal.md").write_text("## Why\nImprove architecture prose without changing behavior.\n\n## What Changes\nClarify an existing description.\n")
        status = self.status()
        self.assertEqual(next(x for x in status["artifacts"] if x["id"] == "specs")["status"], "skipped")
        self.assertEqual(self.apply()["state"], "ready")
        self.cli("validate", CHANGE, "--type", "change", "--strict", "--no-interactive")

    def test_native_pi_commands_install_without_forking(self):
        self.cli("init", "--tools", "pi", "--profile", "core", "--no-animation")
        prompts = self.root / ".pi/prompts"
        for name in ("propose", "explore", "update", "apply", "sync", "archive"):
            self.assertTrue((prompts / f"opsx-{name}.md").is_file(), name)
        self.assertEqual(self.status()["schemaName"], "openspec-ddd")

    def test_new_nested_capability_merges_with_its_purpose(self):
        self.cli("new", "change", "introduce-inspection")
        change = self.root / "openspec/changes/introduce-inspection"
        (change / "proposal.md").write_text(
            "## Why\nKeep equipment awaiting inspection out of circulation.\n\n"
            "## What Changes\nIntroduce a separate maintenance capability.\n")
        delta = change / "specs/contexts/maintenance/features/inspection/spec.md"
        delta.parent.mkdir(parents=True)
        delta.write_text(
            "## Purpose\nTrack equipment awaiting inspection before it can be offered for another loan.\n\n"
            "## ADDED Requirements\n\n### Requirement: Hold pending equipment\n"
            "Maintenance SHALL hold equipment until inspection succeeds.\n\n"
            "#### Scenario: Inspection pending\n- **WHEN** equipment is awaiting inspection\n"
            "- **THEN** it cannot be offered for another loan\n")
        self.cli("validate", "introduce-inspection", "--type", "change", "--strict", "--no-interactive")
        # Archive CLI mechanics are deliberately independent of schema/acceptance review.
        self.cli("archive", "introduce-inspection", "--yes")
        main = self.root / "openspec/specs/contexts/maintenance/features/inspection/spec.md"
        self.assertIn("Track equipment awaiting inspection", main.read_text())
        self.assertNotIn("TBD", main.read_text())
        self.cli("validate", "--all", "--strict", "--no-interactive")

    def test_archive_merges_nested_deltas_and_preserves_unrelated_content(self):
        # This tests only text merge mechanics, not the fictional application's acceptance.
        tasks = self.change / "tasks.md"
        tasks.write_text(tasks.read_text().replace("- [ ]", "- [x]"))
        main = self.root / "openspec/specs/contexts/lending"
        architecture = main / "features/return-equipment/architecture/runtime.md"
        before_architecture = architecture.read_bytes()
        before_database = (main / "adapters/out/database/spec.md").read_bytes()
        self.cli("archive", CHANGE, "--yes")
        self.assertFalse(self.change.exists())
        self.assertEqual(len(list((self.root / "openspec/changes/archive").glob(f"*-{CHANGE}"))), 1)
        domain = (main / "domain/spec.md").read_text()
        self.assertIn("Requirement: Loan identity", domain)
        self.assertIn("Requirement: Recorded return condition", domain)
        feature = (main / "features/return-equipment/spec.md").read_text()
        self.assertIn("Requirement: Reject unavailable loans", feature)
        self.assertIn("Scenario: Invalid condition", feature)
        self.assertIn("Scenario: No partial return", (main / "ports/loan-store/spec.md").read_text())
        self.assertEqual(before_architecture, architecture.read_bytes())
        self.assertEqual(before_database, (main / "adapters/out/database/spec.md").read_bytes())
        self.cli("validate", "--all", "--strict", "--no-interactive")
