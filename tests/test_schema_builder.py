"""Additive composition regressions and native CLI checks for v3 components."""

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
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
            self.assertEqual(len(entries), 5)  # Four documentation compositions plus legacy.
            self.assertEqual({tuple(e["components"]) for e in entries if e["kind"] == "composed"},
                             {(), ("arc42",), ("user-doc",), ("arc42", "user-doc")})
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
            self.assertEqual(len(selections), 6)
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
        self.assertNotIn("{{hook:", "\n".join(content for path, content in combined.items()
                                               if not path.startswith("helpers/")))

    def test_documentation_delivery_boundary_in_every_composition(self):
        selections = builder.combinations() + [["user-doc", "arc42"]]
        for components in selections:
            with self.subTest(components=components):
                files = builder.compose(components)
                normalized = {path: " ".join(text.split()) for path, text in files.items()}
                for path in ("schema.yaml", "templates/config.yaml",
                             "templates/agent-instructions.md", "templates/tasks.md"):
                    for required in (
                        "Apply updates mapped descriptive documentation outside openspec/specs/** in the development checkout.",
                        "The entire openspec/specs/** tree remains read-only during planning and Apply.",
                        "maintained model companions, ADR records, and openspec/catalog.json",
                    ):
                        self.assertTrue(required.lower() in normalized[path].lower(),
                                        f"{path}: missing {required}")
                text = " ".join(normalized.values())
                for obsolete in (
                    "Keep maintained baseline paths read-only in planning/Apply",
                    "Write and verify only the selected change's user-documentation drafts",
                    "maintained handbook writes are publication work, outside Apply checkboxes",
                    "Do not write it during Apply",
                    "Do not turn maintained publication into an Apply checkbox",
                    "including owner-local views under openspec/specs/",
                    "This includes owner-local architecture views under openspec/specs/",
                    "Apply updates these mapped descriptive views",
                    "Do not defer ordinary descriptive-documentation updates solely because sync has not happened",
                ):
                    self.assertFalse(obsolete in text, f"Obsolete policy: {obsolete}")
                if "user-doc" in components:
                    self.assertIn("User documentation Apply updates mapped maintained pages",
                                  normalized["schema.yaml"])
                    self.assertIn("A draft alone does not complete a documentation task.",
                                  normalized["templates/tasks.md"])
                if "arc42" in components:
                    self.assertIn("arc42 Apply updates mapped maintained handbook pages",
                                  normalized["schema.yaml"])
                    self.assertIn("A draft alone does not complete a handbook task.",
                                  normalized["templates/tasks.md"])

    def test_spec_tree_publication_is_separate_from_apply_delivery(self):
        for components in builder.combinations() + [["user-doc", "arc42"]]:
            with self.subTest(components=components):
                files = builder.compose(components)
                for path in ("schema.yaml", "templates/config.yaml",
                             "templates/agent-instructions.md", "templates/openspec-README.md",
                             "templates/README.md", "templates/design.md", "templates/tasks.md",
                             "templates/architecture.md", "templates/verification.md"):
                    text = " ".join(files[path].split())
                    self.assertIn("openspec/specs/**", text, path)
                    self.assertIn("change-local", text, path)
                    self.assertIn("sync/archive", text, path)
                for path in ("schema.yaml", "templates/config.yaml",
                             "templates/agent-instructions.md", "templates/tasks.md"):
                    text = " ".join(files[path].split())
                    self.assertIn("creation, edits, deletion, renaming, and indirect/generated writes", text, path)
                    self.assertIn("local architecture publication", text.lower(), path)
                tasks = " ".join(files["templates/tasks.md"].split())
                self.assertIn("Prepare and check change-local local-architecture proposals", tasks)
                self.assertIn("outside openspec/specs/**", tasks)
                evidence = " ".join(files["templates/verification.md"].split())
                self.assertIn("Local architecture publication under openspec/specs/**", evidence)
                self.assertIn("Pending", evidence)

    def test_canonical_model_clarity_preserves_native_lifecycle_in_every_composition(self):
        artifact_ids = ["proposal", "impact", "domain-model", "specs", "design",
                        "architectural-decisions", "tasks"]
        for components in builder.combinations():
            with self.subTest(components=components):
                files = builder.compose(components)
                normalized = {path: " ".join(text.split()) for path, text in files.items()}
                schema = files["schema.yaml"]
                self.assertEqual([line.removeprefix("  - id: ") for line in schema.splitlines()
                                  if line.startswith("  - id: ")], artifact_ids)
                apply = schema.split("\napply:\n", 1)[1]
                dependencies = apply.split("requires: [", 1)[1].split("]", 1)[0]
                self.assertEqual(dependencies.split(", "), artifact_ids)
                self.assertIn("tracks: tasks.md", apply)
                model_instruction = " ".join(schema.split("  - id: domain-model\n", 1)[1]
                                             .split("  - id: specs\n", 1)[0].split())
                self.assertIn("generates: domain-model-changes.md", model_instruction)
                self.assertIn("template: domain-model-changes.md", model_instruction)
                task_instruction = " ".join(schema.split("  - id: tasks\n", 1)[1]
                                            .split("\napply:\n", 1)[0].split())
                apply_instruction = " ".join(apply.split())
                model = normalized["templates/domain-model.md"]
                assessment = normalized["templates/domain-model-changes.md"]
                for required in (
                    "Optional model support template", "NOT the template for the required domain-model artifact",
                    "No additional native artifact is introduced", "a small model may remain in an identified spec section",
                    "This model explains what the concepts mean and how they relate",
                    "rather than inventing an ID", "Distinguish absence, unknown, an explicit clear, and a default",
                    "Normative obligations and scenarios remain in the owning specs",
                    "not a second editable rule set", "Do not force a state machine on a static value model",
                    "Examples demonstrate the definitions and their boundaries",
                    "they are not new requirements or executed tests", "Reuse/no-change assessments need no new model",
                    "do not promote assessment prose wholesale", "Native spec sync does not merge models",
                ):
                    self.assertIn(required, model)
                for required in (
                    "Always produce this assessment, also with skip_specs",
                    "a short explanation and actual references are enough", "omit unused sections",
                    "not the maintained model's narrative", "Define the proposed meaning once",
                    "link it instead of repeating its full contents", "do not force nonexistent entities",
                    "Changed obligations still need delta specs and removal of skip_specs",
                    "not a wholesale copy of assessment prose", "stale full draft",
                ):
                    self.assertIn(required, assessment)
                for required in (
                    "Use the domain-model.md support template only when a substantial draft helps",
                    "Never maintain two editable copies", "allowed values, absence versus unknown",
                    "valid/invalid combinations", "Explain non-applicable identity or lifecycle briefly",
                    "Model drafts must be readable without the change history or implementation",
                    "Keep normative obligations and scenarios in the owning delta specs",
                    "not a wholesale copy of assessment prose", "not a new CLI gate, artifact, or approval process",
                ):
                    self.assertIn(required, model_instruction)
                for text in (model, assessment, model_instruction, task_instruction,
                             apply_instruction, normalized["templates/tasks.md"],
                             normalized["templates/agent-instructions.md"]):
                    self.assertIn("product-informed reader", text)
                    self.assertIn("concrete example", text)
                    self.assertIn("owning requirements", text)
                    self.assertIn("handoff/evidence", text)
                for text, copy_warning in (
                    (task_instruction, "not assessment prose with publication metadata"),
                    (apply_instruction, "not a wholesale assessment copy"),
                    (normalized["templates/tasks.md"], "not a wholesale assessment copy"),
                ):
                    self.assertIn("invariant summaries", text)
                    self.assertIn("lifecycle", text)
                    self.assertIn("coherent", text)
                    self.assertIn(copy_warning, text)
                archive_guidance = " ".join(files["templates/config.yaml"].split("\n  archive:\n", 1)[1].split())
                for required in ("product-informed reader", "concrete example", "owning requirements",
                                 "coherent model", "not a wholesale assessment copy",
                                 "process metadata in assessment/handoff/evidence", "Record actual review",
                                 "not merely heading presence", "separately authorized sync/archive integration"):
                    self.assertIn(required, archive_guidance)
                agent = normalized["templates/agent-instructions.md"]
                self.assertIn("Assessments carry Before/Proposed comparisons", agent)
                self.assertIn("Model narratives explain concepts, applicable identities/relationships, values/unknowns", agent)
                self.assertIn("Do not force a new model, entity, field, state, or extra artifact for reuse/no-change", agent)
                for path in ("schema.yaml", "templates/config.yaml", "templates/tasks.md",
                             "templates/agent-instructions.md"):
                    self.assertIn("The entire openspec/specs/** tree remains read-only during planning and Apply.",
                                  normalized[path], path)
                    self.assertIn("maintained model companions, adr records, and openspec/catalog.json",
                                  normalized[path].lower(), path)
                self.assertIn("Authorization for native requirement sync alone does not authorize companion publication.",
                              apply_instruction)

    def test_arc42_system_architecture_is_explicit_apply_work(self):
        directive = "Update the affected maintained system architecture under openspec/system-architecture/** during Apply."
        for components in builder.combinations() + [["user-doc", "arc42"]]:
            with self.subTest(components=components):
                files = builder.compose(components)
                normalized = {path: " ".join(text.split()) for path, text in files.items()}
                if "arc42" not in components:
                    self.assertNotIn(directive, " ".join(normalized.values()))
                    continue
                for path in ("schema.yaml", "templates/config.yaml",
                             "templates/agent-instructions.md", "templates/tasks.md"):
                    self.assertIn(directive, normalized[path], path)
                    self.assertIn("Do not defer ordinary handbook updates to sync/archive.", normalized[path], path)
                for path in ("templates/impact.md", "templates/design.md", "templates/tasks.md",
                             "templates/verification.md", "templates/system-architecture/README.md"):
                    self.assertIn("openspec/system-architecture/", normalized[path], path)
                tasks = normalized["templates/tasks.md"]
                self.assertIn("Example Apply work: Update", tasks)
                self.assertIn("Example Apply check: Verify", tasks)
                self.assertIn("Do not add a second checklist", tasks)
                self.assertIn("Reasoned no-change", normalized["templates/impact.md"])
                self.assertIn("actual maintained handbook targets", normalized["templates/verification.md"])
                self.assertIn("Native spec sync does not perform handbook delivery", tasks)

    def test_only_real_documentation_components_are_selected(self):
        self.assertEqual(builder.combinations(),
                         [[], ["arc42"], ["user-doc"], ["arc42", "user-doc"]])
        for selection in builder.combinations():
            self.assertNotIn("approved runtime plan", "\n".join(builder.compose(selection).values()))

    def test_legacy_output_is_unchanged(self):
        expected = builder.read_files(builder.SOURCES / "legacy/openspec-ddd")
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "legacy"
            self.assertEqual(builder.build_legacy(output), expected)
            self.assertEqual(builder.read_files(output), expected)

    def test_ddd_is_independent_of_arc42_layout(self):
        # Helper executables can mention optional architecture metadata paths without
        # imposing that layout on the schema's native instructions or templates.
        base = {path: content for path, content in builder.compose().items()
                if not path.startswith("helpers/")}
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
            manifest["contributions"]["project.context"] = "../outside.txt"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Unsafe source path"):
                builder.compose(["arc42"], sources)

    def test_invalid_hooks_fail_before_output_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            (sources / "ddd/files").mkdir(parents=True)
            output = Path(temp) / "output"
            for content in ("inline {{hook:project.context}}\n", "{{hook:bad",
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

    def test_project_hooks_isolate_destinations_and_preserve_order(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            shutil.copytree(builder.SOURCES / "ddd", sources / "ddd")
            destinations = {
                "project.context": "templates/config.yaml",
                "project.agent-instructions": "templates/agent-instructions.md",
                "project.readme": "templates/openspec-README.md",
            }
            for name in ("first", "second"):
                package = sources / "components" / name
                package.mkdir(parents=True)
                contributions = {}
                for hook in destinations:
                    relative = hook + ".txt"
                    (package / relative).write_text(f"{name}:{hook}:unique\n")
                    contributions[hook] = relative
                (package / "component.json").write_text(json.dumps({
                    "description": name, "requires": [], "contributions": contributions}))
            for selected in ([], ["first"], ["second"], ["first", "second"], ["second", "first"]):
                files = builder.compose(selected, sources)
                for hook, destination in destinations.items():
                    present = [f"{name}:{hook}:unique" for name in selected]
                    for name in ("first", "second"):
                        marker = f"{name}:{hook}:unique"
                        self.assertEqual(marker in files[destination], name in selected)
                        for path, content in files.items():
                            if path != destination:
                                self.assertNotIn(marker, content)
                    if len(present) == 2:
                        self.assertLess(files[destination].index(present[0]),
                                        files[destination].index(present[1]))

    def test_retired_project_hook_has_actionable_migration_error(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            shutil.copytree(builder.SOURCES, sources)
            path = sources / "components/arc42/component.json"
            manifest = json.loads(path.read_text())
            manifest["contributions"]["project-guidance"] = "old.txt"
            (path.parent / "old.txt").write_text("Old shared guidance\n")
            path.write_text(json.dumps(manifest))
            output = Path(temp) / "output"
            with self.assertRaisesRegex(ValueError, "project-guidance.*project.context"):
                builder.build(output, ["arc42"], sources)
            self.assertFalse(output.exists())
            path.write_text(json.dumps(dict(manifest, contributions={})))
            config = sources / "ddd/files/templates/config.yaml"
            config.write_text("context: |\n  {{hook:project-guidance}}\n")
            with self.assertRaisesRegex(ValueError, "project-guidance.*project.context"):
                builder.build(output, sources=sources)
            self.assertFalse(output.exists())

    def test_operation_guidance_is_literal_ordered_string_items(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            (sources / "ddd/files/templates").mkdir(parents=True)
            (sources / "ddd/files/schema.yaml").write_text("name: test\n")
            config = ("operations:\n  apply:\n    guidance:\n      - Base apply.\n"
                      "      {{hook:operation.apply}}\n  archive:\n    guidance:\n"
                      "      - Base archive.\n      {{hook:operation.archive}}\n")
            (sources / "ddd/files/templates/config.yaml").write_text(config)
            literal = ('Rule: "quoted" # comment\n- list-looking\n&anchor *alias !tag\n'
                       '---\noperations:\n  archive: injected\n...\nUnicode: café 😀\u0085\u2028\u2029; C:\\docs\\')
            for name in ("first", "second"):
                package = sources / "components" / name
                package.mkdir(parents=True)
                (package / "text.txt").write_text(name + "\n" + literal + "\n")
                (package / "component.json").write_text(json.dumps({
                    "description": name, "requires": [], "contributions": {
                        "operation.apply": "text.txt", "operation.archive": "text.txt"}}))
            self.assertEqual(builder.compose([], sources)["templates/config.yaml"],
                             config.replace("      {{hook:operation.apply}}\n", "")
                             .replace("      {{hook:operation.archive}}\n", ""))
            for selected in (["first", "second"], ["second", "first"]):
                rendered = builder.compose(selected, sources)["templates/config.yaml"]
                quoted = [line.removeprefix("      - ") for line in rendered.splitlines()
                          if line.startswith('      - "')]
                expected = [name + "\n" + literal for name in selected]
                self.assertEqual([json.loads(item) for item in quoted], expected + expected)
                self.assertEqual(rendered.count("operations:"), 1 + 2 * len(selected))
                self.assertEqual(sum(line == "operations:" for line in rendered.splitlines()), 1)
                self.assertNotIn("{{hook:", rendered)

    def test_operation_hooks_reject_invalid_placement_before_output(self):
        valid = ("operations:\n  apply:\n    guidance:\n      - Base.\n"
                 "      {{hook:operation.apply}}\n")
        cases = [
            ("schema.yaml", valid),
            ("templates/config.yaml", valid.replace("  apply:", "  archive:")),
            ("templates/config.yaml", valid.replace("    guidance:", "    rules:")),
            ("templates/config.yaml", valid.replace("      {{hook:", "        {{hook:")),
            ("templates/config.yaml", "context: |\n  " + valid.replace("\n", "\n  ").rstrip() + "\n"),
            ("templates/config.yaml", valid.replace("    guidance:", "    guidance: []")),
            ("templates/config.yaml", valid + valid),
            ("templates/config.yaml", valid.replace("operation.apply", "operation.deploy")),
        ]
        for path, content in cases:
            with self.subTest(path=path, content=content), tempfile.TemporaryDirectory() as temp:
                sources = Path(temp) / "sources"
                (sources / "ddd/files/templates").mkdir(parents=True)
                (sources / "ddd/files/schema.yaml").write_text("name: test\n")
                (sources / "ddd/files" / path).write_text(content)
                output = Path(temp) / "output"
                with self.assertRaisesRegex(ValueError,
                                            "operation.apply.*placement|Duplicate operation hook|Unknown operation hook"):
                    builder.build(output, sources=sources)
                self.assertFalse(output.exists())

    def test_invalid_operation_fragments_leave_no_output(self):
        for text in (" \n", "{{hook:project.context}}\n"):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as temp:
                sources = Path(temp) / "sources"
                shutil.copytree(builder.SOURCES, sources)
                path = sources / "components/arc42/component.json"
                manifest = json.loads(path.read_text())
                manifest["contributions"]["operation.apply"] = "invalid.txt"
                (path.parent / "invalid.txt").write_text(text)
                path.write_text(json.dumps(manifest))
                output = Path(temp) / "output"
                with self.assertRaisesRegex(ValueError, "Empty contribution|must be final text"):
                    builder.build(output, ["arc42"], sources)
                self.assertFalse(output.exists())

    def test_invalid_manifest_types_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp)
            shutil.copytree(builder.SOURCES, sources, dirs_exist_ok=True)
            path = sources / "components/arc42/component.json"
            original = json.loads(path.read_text())
            for key, value in (("description", []), ("requires", "arc42"),
                               ("contributions", []), ("contributions", {"project.context": []})):
                with self.subTest(key=key, value=value):
                    path.write_text(json.dumps(dict(original, **{key: value})))
                    with self.assertRaises(ValueError):
                        builder.compose(["arc42"], sources)


class HelperCompositionTests(unittest.TestCase):
    """Use isolated sources: helper distribution must not depend on repository packs."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / "sources"
        self.put("ddd/files/schema.yaml", "artifacts: []\napply:\n  requires: []\n")
        self.put("ddd/files/templates/test.md", "Base\n{{hook:test}}\n")
        self.put("legacy/openspec-ddd/schema.yaml", "Historical schema\n")

    def put(self, relative, content):
        path = self.sources / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def component(self, name, packs=None):
        manifest = {"description": name, "requires": [], "contributions": {}}
        if packs is not None:
            manifest["helper-packs"] = packs
        return self.put(f"components/{name}/component.json", json.dumps(manifest))

    def assert_failure(self, selection, pattern):
        output = self.root / "output"
        with self.assertRaisesRegex(ValueError, pattern):
            builder.build(output, selection, self.sources)
        self.assertFalse(output.exists())

    def test_base_and_component_helpers_preserve_native_files_and_legacy(self):
        expected = builder.compose([], self.sources)
        self.put("ddd/helpers/ddd/ddd.py", "print('base')\n")
        self.put("ddd/helpers/README.md", "Base documentation\n")
        for name in ("arc42", "user-doc"):
            self.component(name)
            self.put(f"components/{name}/helpers/{name}/check.py", f"print('{name}')\n")
        for selection in ([], ["arc42"], ["user-doc"], ["arc42", "user-doc"]):
            with self.subTest(selection=selection):
                files = builder.compose(selection, self.sources)
                self.assertEqual({p: c for p, c in files.items() if not p.startswith("helpers/")}, expected)
                self.assertEqual(files["helpers/ddd/ddd.py"], "print('base')\n")
                for name in ("arc42", "user-doc"):
                    self.assertEqual(f"helpers/{name}/check.py" in files, name in selection)
        legacy = builder.build_legacy(self.root / "legacy", self.sources)
        self.assertEqual(legacy, {"schema.yaml": "Historical schema\n"})

    def test_shared_pack_distributed_once_at_first_request_and_readme_order(self):
        self.put("ddd/helpers/README.md", "BASE\n")
        self.put("helper-packs/docs-check/README.md", "SHARED\n")
        self.put("helper-packs/docs-check/check.py", "print('shared')\n")
        for name in ("arc42", "user-doc"):
            self.component(name, ["docs-check"])
            self.put(f"components/{name}/helpers/README.md", name + " body\n")
        for selection in (["arc42"], ["user-doc"], ["arc42", "user-doc"], ["user-doc", "arc42"]):
            with self.subTest(selection=selection):
                files = builder.compose(selection, self.sources)
                readme = files["helpers/README.md"]
                self.assertTrue(readme.startswith("BASE\n"))
                self.assertEqual(readme.count("Helper pack: docs-check"), 1)
                self.assertEqual(readme.count("SHARED"), 1)
                labels = ["Helper pack: docs-check", *[f"Component: {name}" for name in selection]]
                indices = [readme.index(label) for label in labels]
                self.assertEqual(indices, sorted(indices))
                self.assertEqual(files["helpers/check.py"], "print('shared')\n")
                self.assertEqual(files, builder.compose(selection, self.sources))

    def test_readme_exception_is_exclusive_to_helper_merge(self):
        self.put("ddd/helpers/README.md", "Base\n")
        self.component("extra")
        self.put("components/extra/files/helpers/README.md", "Not a helper contribution\n")
        self.assert_failure(["extra"], "conflict")

    def test_identical_file_collisions_between_all_providers_are_errors(self):
        for first, second in (("ddd/helpers", "components/extra/helpers"),
                              ("helper-packs/one", "helper-packs/two"),
                              ("helper-packs/one", "components/extra/helpers"),
                              ("components/first/helpers", "components/extra/helpers")):
            with self.subTest(first=first, second=second):
                paths = [self.put(f"{provider}/check.py", "identical\n") for provider in (first, second)]
                self.component("first")
                self.component("extra", ["one", "two"] if second == "helper-packs/two" else
                               ["one"] if first == "helper-packs/one" else [])
                self.assert_failure(["first", "extra"], "conflict")
                for path in paths:
                    path.unlink()

    def test_file_directory_conflicts_leave_no_output(self):
        self.component("extra")
        self.put("ddd/helpers/tool", "file\n")
        self.put("components/extra/helpers/tool/check.py", "nested\n")
        self.assert_failure(["extra"], "conflict")
        (self.sources / "ddd/helpers/tool").unlink()
        self.put("components/extra/files/helpers", "file instead of helper directory\n")
        self.assert_failure(["extra"], "conflict")

    def test_missing_pack_is_clear_and_optional_helper_directories_are_optional(self):
        self.component("extra")
        self.assertEqual(builder.compose(["extra"], self.sources), builder.compose([], self.sources))
        self.component("extra", ["missing"])
        self.assert_failure(["extra"], "Unknown helper pack: missing")

    def test_manifest_helper_packs_requires_unique_safe_identifier_list(self):
        for invalid in ("docs", {}, None, [1], ["docs", "docs"], ["../docs"],
                        ["/docs"], ["a/b"], [""], ["Bad"], ["a_b"]):
            with self.subTest(invalid=invalid):
                self.component("extra", [])
                path = self.sources / "components/extra/component.json"
                manifest = json.loads(path.read_text())
                manifest["helper-packs"] = invalid
                path.write_text(json.dumps(manifest))
                self.assert_failure(["extra"], "Invalid helper-packs")
        for mutation in ({"unknown": []}, {"description": None}, {"requires": None}, {"contributions": None}):
            self.component("extra", [])
            path = self.sources / "components/extra/component.json"
            manifest = json.loads(path.read_text())
            manifest.update(mutation)
            path.write_text(json.dumps(manifest))
            self.assert_failure(["extra"], "Invalid")
        builder.validate_manifest({"description": "Valid", "requires": [], "contributions": {},
                                   "helper-packs": []}, "extra")

    def test_helpers_exclude_only_python_cache_and_do_not_render_literal_hooks(self):
        self.component("extra", ["docs"])
        literal = "text = '{{hook:unknown}}'\n{{hook:operation.apply}}\n{{slot:literal}}\n"
        for provider in ("ddd/helpers", "components/extra/helpers", "helper-packs/docs"):
            name = provider.replace("/", "-")
            self.put(f"{provider}/{name}.py", literal)
            self.put(f"{provider}/assets/{name}.txt", "Required asset\n")
            self.put(f"{provider}/__pycache__/{name}.pyc", "cache")
            self.put(f"{provider}/nested/{name}.pyc", "cache")
            self.put(f"{provider}/nested/{name}.pyo", "cache")
        files = builder.compose(["extra"], self.sources)
        for provider in ("ddd/helpers", "components/extra/helpers", "helper-packs/docs"):
            name = provider.replace("/", "-")
            self.assertEqual(files[f"helpers/{name}.py"], literal)
            self.assertEqual(files[f"helpers/assets/{name}.txt"], "Required asset\n")
        self.assertFalse(any("__pycache__" in p or p.endswith((".pyc", ".pyo")) for p in files))

    def test_symlink_roots_directories_files_and_manifest_are_rejected(self):
        self.component("extra", ["docs"])
        self.put("helper-packs/docs/real.txt", "real")
        target = self.root / "target"
        target.mkdir()
        (target / "file.txt").write_text("outside")
        for relative, is_directory in (("ddd/helpers", True), ("components/extra/helpers", True),
                                        ("helper-packs/docs/nested", True),
                                        ("helper-packs/docs/link.txt", False)):
            with self.subTest(relative=relative):
                link = self.sources / relative
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(target if is_directory else target / "file.txt", target_is_directory=is_directory)
                self.assert_failure(["extra"], "Symlink")
                link.unlink()
        pack = self.sources / "helper-packs/docs"
        shutil.rmtree(pack)
        pack.symlink_to(target, target_is_directory=True)
        self.assert_failure(["extra"], "Symlink")
        pack.unlink()
        manifest = self.sources / "components/extra/component.json"
        original = manifest.read_text()
        manifest.unlink()
        outside = target / "component.json"
        outside.write_text(original)
        manifest.symlink_to(outside)
        self.assert_failure(["extra"], "Symlink")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            builder.read_files(manifest)

    def test_helpers_in_files_tree_remain_data_but_cannot_append_readme(self):
        self.component("extra")
        literal = "text = '{{hook:unknown}}'\n"
        self.put("components/extra/files/helpers/tool.py", literal)
        self.put("components/extra/files/helpers/tool.pyc", "cache")
        files = builder.compose(["extra"], self.sources)
        self.assertEqual(files["helpers/tool.py"], literal)
        self.assertNotIn("helpers/tool.pyc", files)
        self.put("components/extra/files/helpers/README.md", "Ordinary file\n")
        self.component("second")
        self.put("components/second/helpers/README.md", "Helper section\n")
        self.assert_failure(["extra", "second"], "conflict")

    def test_matrix_rejects_unowned_bytecode_in_output(self):
        self.component("extra")
        self.put("ddd/helpers/tool.py", "original\n")
        output = self.root / "matrix"
        builder.build_all(output, self.sources)
        (output / "ddd/helpers/unowned.pyc").write_bytes(b"unowned bytecode")
        with self.assertRaisesRegex(ValueError, "modified|unowned"):
            builder.build_all(output, self.sources)

    def test_matrix_ownership_includes_helper_integrity(self):
        self.component("extra", ["docs"])
        self.put("helper-packs/docs/check.py", "original\n")
        output = self.root / "matrix"
        builder.build_all(output, self.sources)
        builder.build_all(output, self.sources)
        (output / "ddd+extra/helpers/check.py").write_text("edited\n")
        with self.assertRaisesRegex(ValueError, "modified"):
            builder.build_all(output, self.sources)


@unittest.skipUnless(CLI, "Install OpenSpec 1.13.1 or set OPENSPEC_BIN for integration tests")
class BuiltSchemaOpenSpecTests(unittest.TestCase):
    def test_combinations_validate_and_use_native_lifecycle(self):
        self.assertEqual(subprocess.check_output([CLI, "--version"], text=True).strip(), "1.13.1")
        with tempfile.TemporaryDirectory() as matrix_temp:
            matrix = Path(matrix_temp) / "schemas"
            entries = builder.build_all(matrix)
            generated = {tuple(e["components"]): builder.read_files(matrix / e["path"])
                         for e in entries if e["kind"] == "composed"}
        base_guidance = {}
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
                    self.assertIn("The entire openspec/specs/** tree remains read-only during planning and Apply.",
                                  " ".join(instructions["instruction"].split()))
                    if artifact["id"] == "domain-model":
                        model_instruction = " ".join(instructions["instruction"].split())
                        for required in ("a model explains concepts and how they relate",
                                         "allowed values, absence versus unknown",
                                         "Model drafts must be readable without the change history or implementation",
                                         "product-informed reader", "concrete example", "owning requirements",
                                         "Record the actual semantic review in the existing handoff/evidence"):
                            self.assertIn(required, model_instruction)
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
                instruction = " ".join(ready["instruction"].split())
                self.assertIn("Apply updates mapped descriptive documentation outside openspec/specs/** in the development checkout.",
                              instruction)
                self.assertIn("The entire openspec/specs/** tree remains read-only during planning and Apply.",
                              instruction)
                self.assertIn("maintained model companions, adr records, and openspec/catalog.json",
                              instruction.lower())
                self.assertIn("creation, edits, deletion, renaming, and indirect/generated writes", instruction)
                self.assertNotIn("including owner-local views under openspec/specs/", instruction)
                self.assertIn("Authorization for native requirement sync alone does not authorize companion publication.",
                              instruction)
                self.assertIn("Do not run sync/archive", instruction)
                for required in ("authorized publication include semantic review", "product-informed reader",
                                 "concrete example", "owning requirements", "assessment/process metadata",
                                 "not a wholesale assessment copy", "Record actual review in existing handoff/evidence"):
                    self.assertIn(required, instruction)
                if "arc42" in components:
                    self.assertIn("arc42 Apply updates mapped maintained handbook pages", instruction)
                    self.assertIn("Update the affected maintained system architecture under openspec/system-architecture/** during Apply.",
                                  instruction)
                    self.assertIn("Do not defer ordinary handbook updates to sync/archive.", instruction)
                if "user-doc" in components:
                    self.assertIn("User documentation Apply updates mapped maintained pages", instruction)
                self.assertEqual(ready["state"], "ready")
                self.assertEqual(ready["progress"], {"total": 1, "complete": 0, "remaining": 1})
                archive = cli("instructions", "archive", "--change", "docs-only", "--json", as_json=True)
                archive_guidance = " ".join(" ".join(item.split()) for item in archive["operationGuidance"])
                for required in ("Before model publication", "product-informed reader", "concrete example",
                                 "coherent model", "not a wholesale assessment copy",
                                 "process metadata in assessment/handoff/evidence", "owning requirements",
                                 "Record actual review", "not merely heading presence"):
                    self.assertIn(required, archive_guidance)
                results = {"apply": ready, "archive": archive}
                if not components:
                    base_guidance = {operation: result["operationGuidance"]
                                     for operation, result in results.items()}
                for operation, result in results.items():
                    expected = list(base_guidance[operation])
                    for component in components:
                        package = builder.SOURCES / "components" / component
                        manifest = json.loads((package / "component.json").read_text())
                        fragment = package / manifest["contributions"][f"operation.{operation}"]
                        expected.append(textwrap.dedent(fragment.read_text()).strip("\n"))
                    self.assertEqual(result["operationGuidance"], expected)
                if "arc42" in components:
                    guidance = " ".join(" ".join(item.split()) for item in ready["operationGuidance"])
                    self.assertIn("Update the affected maintained system architecture under openspec/system-architecture/** during Apply.",
                                  guidance)
                    self.assertIn("Do not defer ordinary handbook updates to sync/archive.", guidance)
                for component in components:
                    package = builder.SOURCES / "components" / component
                    manifest = json.loads((package / "component.json").read_text())
                    def fragment(hook):
                        return textwrap.dedent((package / manifest["contributions"][hook]).read_text()).strip("\n")
                    self.assertIn(fragment("project.context"), archive["context"])
                    self.assertNotIn(fragment("project.agent-instructions"), archive["context"])
                    self.assertNotIn(fragment("project.readme"), archive["context"])

    def test_operation_guidance_round_trips_through_native_yaml_parser(self):
        self.assertEqual(subprocess.check_output([CLI, "--version"], text=True).strip(), "1.13.1")
        payload = ('Rule: "quoted" # not a comment\n- !!str list-looking\n&anchor *alias !tag\n'
                   '---\ncontext: injected\noperations:\n  archive: injected\n...\nUnicode: café 😀\u0085\u2028\u2029; C:\\docs\\')
        with tempfile.TemporaryDirectory() as temp:
            sources = Path(temp) / "sources"
            shutil.copytree(builder.SOURCES / "ddd", sources / "ddd")
            package = sources / "components/literal"
            package.mkdir(parents=True)
            (package / "text.txt").write_text(payload + "\n")
            (package / "component.json").write_text(json.dumps({
                "description": "Literal guidance", "requires": [], "contributions": {
                    "operation.apply": "text.txt", "operation.archive": "text.txt"}}))
            project = Path(temp) / "project"
            files = builder.build(project / "openspec/schemas/openspec-ddd", ["literal"], sources)
            (project / "openspec/config.yaml").write_text(files["templates/config.yaml"])
            env = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1",
                       OPENSPEC_NO_UPDATE_CHECK="1", XDG_CONFIG_HOME=str(Path(temp) / "config"),
                       XDG_DATA_HOME=str(Path(temp) / "data"))
            def cli(*args):
                result = subprocess.run([CLI, *args], cwd=project, env=env,
                                        text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                return result.stdout
            cli("schema", "validate", "openspec-ddd")
            cli("new", "change", "literal-guidance")
            archive = json.loads(cli("instructions", "archive", "--change", "literal-guidance", "--json"))
            self.assertEqual(archive["operationGuidance"][-1], payload)
            self.assertTrue(all(isinstance(item, str) for item in archive["operationGuidance"]))
            self.assertNotEqual(archive["context"], "injected")
            self.assertNotIn("context: injected", archive["context"])
            metadata = project / "openspec/changes/literal-guidance/.openspec.yaml"
            metadata.write_text(metadata.read_text() + "skip_specs: true\n")
            for name in ("proposal.md", "impact.md", "domain-model-changes.md", "design.md",
                         "architectural-decisions.md", "tasks.md"):
                (project / "openspec/changes/literal-guidance" / name).write_text(
                    "- [ ] 1.1 Check literal guidance\n" if name == "tasks.md" else "Test assessment.\n")
            apply = json.loads(cli("instructions", "apply", "--change", "literal-guidance", "--json"))
            self.assertEqual(apply["operationGuidance"][-1], payload)
            self.assertEqual(apply["state"], "ready")


if __name__ == "__main__":
    unittest.main()
