"""Additive composition regressions and native CLI checks for v3 components."""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("schema_builder", ROOT / "scripts/schema-builder/build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
CLI = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec")


class SchemaBuilderTests(unittest.TestCase):
    def test_variant_directly_contains_schema_and_templates(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schemas"
            entries = builder.build_all(output)
            for entry in entries:
                variant = output / entry["path"]
                self.assertEqual(entry["path"], entry["variant"])
                self.assertTrue((variant / "schema.yaml").is_file())
                self.assertTrue((variant / "templates").is_dir())
                self.assertFalse((variant / "openspec-ddd").exists())
            self.assertEqual(entries, builder.build_all(output))

    def test_matrix_is_complete_repeatable_and_preserves_unowned_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schemas"
            entries = builder.build_all(output)
            self.assertEqual(len(entries), 9)  # Eight compositions plus legacy.
            self.assertEqual(len({tuple(e["components"]) for e in entries if e["kind"] == "composed"}), 8)
            before = builder.read_files(output)
            self.assertEqual(entries, builder.build_all(output))
            self.assertEqual(before, builder.read_files(output))
            (output / "keep.txt").write_text("User file")
            with self.assertRaisesRegex(ValueError, "modified|unowned"):
                builder.build_all(output)
            self.assertEqual((output / "keep.txt").read_text(), "User file")

    def test_matrix_failure_keeps_previous_build_and_rejects_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            shutil.copytree(builder.SOURCES, sources)
            output = Path(temp) / "output"
            builder.build_all(output, sources)
            before = builder.read_files(output)
            collision = sources / "components/arc42/files/schema.yaml"
            collision.write_text("collision")
            with self.assertRaisesRegex(ValueError, "conflict"):
                builder.build_all(output, sources)
            self.assertEqual(builder.read_files(output), before)
            collision.unlink()
            schema = output / "ddd/schema.yaml"
            schema.write_text("local edits")
            with self.assertRaisesRegex(ValueError, "modified"):
                builder.build_all(output, sources)
            self.assertEqual(schema.read_text(), "local edits")

    def test_matrix_rejects_dependency_cycles(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            shutil.copytree(builder.SOURCES, sources)
            path = sources / "components/arc42/component.json"
            manifest = json.loads(path.read_text())
            manifest["requires"] = ["arc42"]
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "cycle"):
                builder.combinations(sources)

    def test_matrix_rejects_existing_unowned_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unowned"):
                builder.build_all(Path(temp))

    def test_matrix_dependencies_are_ordered_and_filter_subsets(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            shutil.copytree(builder.SOURCES, sources)
            package = sources / "components/aaa"
            package.mkdir()
            (package / "component.json").write_text(json.dumps({
                "description": "Dependent component", "requires": ["arc42"], "contributions": {}}))
            selections = builder.combinations(sources)
            self.assertEqual(len(selections), 12)
            for selected in selections:
                if "aaa" in selected:
                    self.assertLess(selected.index("arc42"), selected.index("aaa"))
            (package / "component.json").write_text(json.dumps({
                "description": "Broken", "requires": ["unknown"], "contributions": {}}))
            with self.assertRaisesRegex(ValueError, "Unknown dependency"):
                builder.combinations(sources)

    def test_components_share_hooks_without_base_changes(self):
        before = builder.read_files(builder.SOURCES / "ddd/files")
        combined = builder.compose(["arc42", "user-doc"])
        reverse = builder.compose(["user-doc", "arc42"])
        self.assertEqual(before, builder.read_files(builder.SOURCES / "ddd/files"))
        self.assertIn("templates/user-documentation/how-to.md", combined)
        self.assertIn("templates/system-architecture/README.md", combined)
        for path in ("schema.yaml", "templates/impact.md", "templates/tasks.md",
                     "templates/verification.md", "templates/agent-instructions.md"):
            with self.subTest(path=path):
                self.assertIn("arc42", combined[path])
                self.assertIn("user documentation", combined[path].lower())
                self.assertLess(combined[path].index("arc42"), combined[path].lower().index("user documentation"))
                self.assertLess(reverse[path].lower().index("user documentation"), reverse[path].index("arc42"))
        self.assertEqual(combined, builder.compose(["arc42", "user-doc"]))
        self.assertNotIn("{{hook:", "\n".join(combined.values()))

    def test_reconstruction_is_separate_from_handbook(self):
        arc42 = "\n".join(builder.compose(["arc42"]).values())
        self.assertNotIn("approved runtime plan", arc42)
        reconstruction = builder.compose(["architecture-reconstruction"])
        self.assertIn("approved runtime plan", reconstruction["templates/agent-instructions.md"])
        self.assertNotIn("templates/system-architecture/README.md", reconstruction)

    def test_ddd_is_independent_of_arc42_layout(self):
        base = builder.compose()
        self.assertFalse(any("system-architecture" in path for path in base))
        self.assertNotIn("system-architecture", "\n".join(base.values()))
        self.assertNotIn("brownfield", "\n".join(base.values()))
        self.assertNotIn("architecture-only reconstruction", "\n".join(base.values()))
        for template in ("domain-model-changes.md", "architectural-decisions.md",
                         "architectural-decision.md", "architecture.md"):
            self.assertIn(f"templates/{template}", base)
        self.assertNotIn("{{hook:", "\n".join(base.values()))

    def test_invalid_selection_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schema"
            for components in (["missing"], ["arc42", "arc42"], ["../arc42"]):
                with self.subTest(components=components), self.assertRaises(ValueError):
                    builder.build(output, components)
                self.assertFalse(output.exists())

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schema"
            builder.build(output)
            before = (output / "schema.yaml").read_bytes()
            with self.assertRaisesRegex(ValueError, "already exists"):
                builder.build(output, ["arc42"])
            self.assertEqual((output / "schema.yaml").read_bytes(), before)
            self.assertFalse((output / "templates/system-architecture").exists())

    def test_new_components_dependencies_and_conflicts(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            shutil.copytree(builder.SOURCES, sources, dirs_exist_ok=True)
            package = sources / "components/extra"
            (package / "files/templates").mkdir(parents=True)
            (package / "files/templates/extra.md").write_text("Extra support template\n")
            manifest = {"description": "Future component", "requires": ["arc42"], "contributions": {}}
            (package / "component.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "requires an earlier component"):
                builder.compose(["extra"], sources)
            self.assertIn("templates/extra.md", builder.compose(["arc42", "extra"], sources))
            (package / "files/schema.yaml").write_text("must not replace the base\n")
            with self.assertRaisesRegex(ValueError, "conflict on output file"):
                builder.compose(["arc42", "extra"], sources)
            (package / "files/schema.yaml").unlink()
            manifest["contributions"] = {"instructions.impact": "files/templates/extra.md"}
            (package / "component.json").write_text(json.dumps(manifest))
            result = builder.compose(["arc42", "extra"], sources)
            self.assertIn("Extra support template", result["schema.yaml"])
            manifest["requires"] = []
            manifest["contributions"] = {"unknown-hook": "files/templates/extra.md"}
            (package / "component.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Unknown extension hook"):
                builder.compose(["extra"], sources)

    def test_manifest_path_cannot_escape_component(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            shutil.copytree(builder.SOURCES, sources, dirs_exist_ok=True)
            manifest_path = sources / "components/arc42/component.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["contributions"]["project-guidance"] = "../outside.txt"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Unsafe source path"):
                builder.compose(["arc42"], sources)

    def test_invalid_hooks_fail_before_output_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            (sources / "ddd/files").mkdir(parents=True)
            output = Path(temp) / "output"
            for content in ("inline {{hook:project-guidance}}\n", "{{hook:bad",
                            "{{slot:old}}default{{/slot:old}}"):
                with self.subTest(content=content):
                    (sources / "ddd/files/schema.yaml").write_text(content)
                    with self.assertRaisesRegex(ValueError, "Malformed or inline"):
                        builder.build(output, sources=sources)
                    self.assertFalse(output.exists())

    def test_rendering_indents_blocks_and_separates_contributions(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            (sources / "ddd/files").mkdir(parents=True)
            (sources / "ddd/files/schema.yaml").write_text(
                "instruction: |\n  Base.\n  {{hook:instructions.apply}}\nnext: value\n")
            for name in ("first", "second"):
                package = sources / "components" / name
                package.mkdir(parents=True)
                (package / "text.txt").write_text(name + "\n\n- detail\n  continuation\n")
                (package / "component.json").write_text(json.dumps({
                    "description": name, "requires": [],
                    "contributions": {"instructions.apply": "text.txt"}}))
            self.assertEqual(builder.compose([], sources)["schema.yaml"],
                             "instruction: |\n  Base.\nnext: value\n")
            result = builder.compose(["first", "second"], sources)["schema.yaml"]
            self.assertEqual(result, "instruction: |\n  Base.\n\n  first\n\n  - detail\n"
                             "    continuation\n\n  second\n\n  - detail\n    continuation\n\nnext: value\n")
            (sources / "components/first/text.txt").write_text("{{hook:instructions.apply}}")
            with self.assertRaisesRegex(ValueError, "must be final text"):
                builder.compose(["first"], sources)

    def test_invalid_manifest_types_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            shutil.copytree(builder.SOURCES, sources, dirs_exist_ok=True)
            path = sources / "components/arc42/component.json"
            original = json.loads(path.read_text())
            for key, value in (("description", []), ("requires", "arc42"),
                               ("contributions", []), ("contributions", {"project-guidance": []})):
                with self.subTest(key=key, value=value):
                    path.write_text(json.dumps(dict(original, **{key: value})))
                    with self.assertRaises(ValueError):
                        builder.compose(["arc42"], sources)


@unittest.skipUnless(CLI, "Install OpenSpec 1.13.1 or set OPENSPEC_BIN for integration tests")
class BuiltSchemaOpenSpecTests(unittest.TestCase):
    def test_combinations_validate_and_use_native_lifecycle(self):
        self.assertEqual(subprocess.check_output([CLI, "--version"], text=True).strip(), "1.13.1")
        with tempfile.TemporaryDirectory() as matrix_temp:
            matrix = Path(matrix_temp) / "schemas"
            entries = builder.build_all(matrix)
            generated = {tuple(e["components"]): builder.read_files(matrix / e["path"])
                         for e in entries if e["kind"] == "composed"}
        for components in builder.combinations():
            with self.subTest(components=components), tempfile.TemporaryDirectory() as temp:
                project = Path(temp) / "project"
                builder.write_files(project / "openspec/schemas/openspec-ddd", generated[tuple(components)])
                (project / "openspec/config.yaml").write_text(
                    (project / "openspec/schemas/openspec-ddd/templates/config.yaml").read_text())
                env = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1",
                           OPENSPEC_NO_UPDATE_CHECK="1", XDG_CONFIG_HOME=str(Path(temp) / "config"),
                           XDG_DATA_HOME=str(Path(temp) / "data"))

                def cli(*args, as_json=False):
                    result = subprocess.run([CLI, *args], cwd=project, env=env,
                                            text=True, capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    return json.loads(result.stdout) if as_json else result.stdout

                cli("schema", "validate", "openspec-ddd")
                cli("templates", "--schema", "openspec-ddd", "--json", as_json=True)
                cli("new", "change", "docs-only")
                status = cli("status", "--change", "docs-only", "--json", as_json=True)
                self.assertEqual(len(status["artifacts"]), 7)
                self.assertEqual({a["id"] for a in status["artifacts"] if a["status"] == "ready"},
                                 {"proposal"})
                change = project / "openspec/changes/docs-only"
                metadata = change / ".openspec.yaml"
                metadata.write_text(metadata.read_text() + "skip_specs: true\n")
                for artifact in status["artifacts"]:
                    if artifact["id"] == "specs":
                        continue
                    instructions = cli("instructions", artifact["id"], "--change", "docs-only",
                                       "--json", as_json=True)
                    self.assertTrue(instructions["template"])
                    self.assertNotIn("{{hook:", instructions["instruction"])
                    if artifact["id"] == "impact":
                        for component, marker in (("arc42", "arc42"), ("user-doc", "User documentation")):
                            if component in components:
                                self.assertIn(marker.lower(), instructions["instruction"].lower())
                                self.assertIn(marker.lower(), instructions["template"].lower())
                    (change / artifact["outputPath"]).write_text(
                        "- [ ] 1.1 Review documentation\n" if artifact["id"] == "tasks"
                        else "Reasoned documentation-only assessment.\n")
                ready = cli("instructions", "apply", "--change", "docs-only", "--json", as_json=True)
                for component, marker in (("arc42", "arc42"), ("user-doc", "User documentation")):
                    if component in components:
                        self.assertIn(marker.lower(), ready["instruction"].lower())
                self.assertEqual(ready["state"], "ready")
                self.assertEqual(ready["progress"], {"total": 1, "complete": 0, "remaining": 1})


if __name__ == "__main__":
    unittest.main()
