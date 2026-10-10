"""Public starter-builder contract for review-only, hierarchical agent guidance."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SELECTIONS = ((), ("arc42",), ("user-doc",), ("arc42", "user-doc"))
PROPOSAL = "AGENTS.proposal.md"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "project_guidance_builder_tests", ROOT / "scripts/starter-builder/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def snapshot(root):
    result = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = ("link", os.readlink(path))
        elif path.is_dir():
            result[name] = ("directory",)
        else:
            result[name] = ("file", path.read_bytes(), path.stat().st_mode & 0o777)
    return result


class ProjectGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def fixture(self, temporary, *, local_root=False):
        directory = Path(temporary)
        sources = directory / "src/project_templates"
        schemas = directory / "src/schemas"
        shutil.copytree(ROOT / "src/project_templates", sources)
        shutil.copytree(ROOT / "src/schemas", schemas,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if local_root:
            shutil.copytree(ROOT / "scripts/md-book-builder", directory / "scripts/md-book-builder",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".cache", ".venv"))
            for name in ("book.sh", "book.cmd", "book.md"):
                shutil.copy2(ROOT / "scripts" / name, directory / "scripts" / name)
        return {"sources": sources, "schema_sources": schemas,
                "root": directory if local_root else ROOT}

    def proposal(self, components=(), **kwargs):
        payload = self.builder.compose(components=components, **kwargs)
        self.assertIn(PROPOSAL, payload)
        self.assertNotIn("AGENTS.md", payload)
        return payload[PROPOSAL][0].decode("utf-8"), payload

    def test_four_selections_are_review_only_and_include_canonical_prose_once(self):
        config = read_json(ROOT / "src/project_templates/guidance.json")
        intro = (ROOT / config["intro"]).read_text().split("\n\n")[1]
        shared = (ROOT / config["groups"][1]["source"]).read_text().split("\n\n")[0]
        base = self.builder.schema_builder.compose([])["templates/agent-instructions.md"]
        # Whole prose paragraphs remain canonical even though headings are nested.
        base_paragraphs = [block for block in base.split("\n\n")
                           if block.strip() and not block.startswith(("#", "{{"))]
        self.assertTrue(base_paragraphs)
        for components in SELECTIONS:
            with self.subTest(components=components):
                name = "+".join(("ddd", *components))
                text, payload = self.proposal(components)
                self.assertEqual(text.count(intro), 1)
                self.assertEqual(text.count(shared), int(bool(components)))
                self.assertEqual(text.count("\n## DDD foundation\n"), 1)
                self.assertEqual(text.count("\n### Documentation\n"), int(bool(components)))
                for paragraph in base_paragraphs:
                    self.assertEqual(text.count(paragraph.replace("openspec-ddd", name).strip()), 1)
                for component in ("arc42", "user-doc"):
                    manifest = read_json(ROOT / "src/project_templates" / component / "manifest.json")
                    guidance = manifest["guidance"]
                    fragment = (ROOT / guidance["source"]).read_text().strip().replace("openspec-ddd", name)
                    self.assertEqual(text.count(fragment), int(component in components))
                    self.assertEqual(text.count("\n#### " + guidance["title"] + "\n"),
                                     int(component in components))
                self.assertNotRegex(text, r"\{\{/?(?:hook|slot|group|schema-name)\b")
                self.assertNotIn("openspec/schemas/openspec-ddd/", text)
                if components:
                    helper = f"openspec/schemas/{name}/helpers/docs-check.py"
                    self.assertIn(helper, text)
                    self.assertIn(helper, payload)
                self.assertEqual(payload, self.builder.compose(components=components))

    def test_build_and_matrix_only_materialize_the_proposal(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for components in SELECTIONS:
                output = directory / ("single-" + "+".join(("ddd", *components)))
                self.builder.build(output, components=components)
                expected, _ = self.proposal(components)
                self.assertEqual((output / PROPOSAL).read_text(), expected)
                self.assertFalse((output / "AGENTS.md").exists())
            matrix = directory / "matrix"
            entries = self.builder.build_all(matrix)
            for entry in entries:
                project = matrix / entry["path"]
                self.assertTrue((project / PROPOSAL).is_file())
                self.assertFalse((project / "AGENTS.md").exists())
            before = snapshot(matrix)
            self.assertEqual(entries, self.builder.build_all(matrix))
            self.assertEqual(before, snapshot(matrix))

    def add_future_component(self, options):
        sources, schemas = options["sources"], options["schema_sources"]
        config_path = sources / "guidance.json"
        config = read_json(config_path)
        config["groups"].append({"id": "reference", "parent": "documentation",
                                 "title": "Reference documentation"})
        write_json(config_path, config)
        component = schemas / "components/reference-doc"
        component.mkdir()
        fragment = ROOT / "src/schemas/components/user-doc/fragments/project-agent-instructions.txt"
        shutil.copy2(fragment, component / "agent.txt")
        write_json(component / "component.json", {
            "description": "Future reference component", "requires": [],
            "helper-packs": ["docs"],
            "contributions": {"project.agent-instructions": "agent.txt"}})
        write_json(sources / "reference-doc/manifest.json", {
            "files": {}, "books": {}, "guidance": {
                "group": "reference", "title": "Reference delivery",
                "source": "src/schemas/components/user-doc/fragments/project-agent-instructions.txt"}})

    def test_future_component_activates_nested_ancestors_and_shared_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            options = self.fixture(temporary)
            self.add_future_component(options)
            text, payload = self.proposal(("reference-doc",), **options)
            headings = ("## DDD foundation", "### Documentation",
                        "#### Reference documentation", "##### Reference delivery")
            positions = []
            for heading in headings:
                self.assertEqual(text.count("\n" + heading + "\n"), 1)
                positions.append(text.index("\n" + heading + "\n"))
            self.assertEqual(positions, sorted(positions))
            self.assertIn("scripts/md-book-builder/book.py", payload)
            self.assertIn("scripts/book.sh", payload)
            self.assertIn("openspec/schemas/ddd+reference-doc/helpers/docs-check.py", payload)
            self.assertNotIn("book.arc42.toml", payload)
            self.assertNotIn("book.user-doc.toml", payload)
            self.assertEqual(payload, self.builder.compose(("reference-doc",), **options))
            entries = self.builder.build_all(Path(temporary) / "matrix", **options)
            self.assertTrue(any(entry["components"] == ["reference-doc"] for entry in entries))

    def assert_invalid_preserves_outputs(self, mutate, *, local_root=False):
        with tempfile.TemporaryDirectory() as temporary:
            options = self.fixture(temporary, local_root=local_root)
            matrix = Path(temporary) / "matrix"
            self.builder.build_all(matrix, **options)
            before = snapshot(matrix)
            mutate(options)
            with self.assertRaises(ValueError):
                self.builder.compose(("arc42", "user-doc"), **options)
            fresh = Path(temporary) / "fresh"
            with self.assertRaises(ValueError):
                self.builder.build(fresh, ("arc42", "user-doc"), **options)
            self.assertFalse(fresh.exists())
            with self.assertRaises(ValueError):
                self.builder.build_all(matrix, **options)
            self.assertEqual(before, snapshot(matrix))

    def test_invalid_configuration_fields_types_and_graphs_preserve_matrix(self):
        original = read_json(ROOT / "src/project_templates/guidance.json")
        cases = []
        for field, value in (("intro", None), ("groups", {}), ("unexpected", True)):
            config = copy.deepcopy(original)
            config[field] = value
            cases.append(config)
        for field, value in (("id", 1), ("title", ""), ("parent", "unknown"),
                             ("always", "true"), ("source", []), ("packages", "documentation"),
                             ("packages", [1]), ("packages", ["documentation", "documentation"]),
                             ("packages", ["arc42"]),
                             ("unexpected", True)):
            config = copy.deepcopy(original)
            config["groups"][0][field] = value
            cases.append(config)
        duplicate = copy.deepcopy(original)
        duplicate["groups"].append(copy.deepcopy(duplicate["groups"][0]))
        cases.append(duplicate)
        cycle = copy.deepcopy(original)
        cycle["groups"][0]["parent"] = "documentation"
        cases.append(cycle)
        deep = copy.deepcopy(original)
        parent = "documentation"
        for index in range(5):
            name = f"level-{index}"
            deep["groups"].append({"id": name, "parent": parent, "title": name})
            parent = name
        cases.append(deep)
        for index, config in enumerate(cases):
            with self.subTest(case=index):
                self.assert_invalid_preserves_outputs(
                    lambda options, config=config: write_json(options["sources"] / "guidance.json", config))

    def test_invalid_component_guidance_preserves_matrix(self):
        original = read_json(ROOT / "src/project_templates/arc42/manifest.json")["guidance"]
        cases = [None, [], "documentation"]
        for field, value in (("group", "unknown"), ("group", 1), ("title", ""),
                             ("title", "two\nlines"), ("source", None), ("unexpected", True)):
            guidance = dict(original)
            guidance[field] = value
            cases.append(guidance)
        missing = dict(original)
        missing.pop("source")
        cases.append(missing)
        for guidance in cases:
            with self.subTest(guidance=guidance):
                def mutate(options):
                    path = options["sources"] / "arc42/manifest.json"
                    manifest = read_json(path)
                    manifest["guidance"] = guidance
                    write_json(path, manifest)
                self.assert_invalid_preserves_outputs(mutate)

    def test_unsafe_guidance_sources_and_proposal_collisions_preserve_matrix(self):
        for unsafe in ("../outside.md", "/outside.md", "safe/../../outside.md", "back\\slash.md"):
            for location in ("intro", "group", "fragment"):
                with self.subTest(source=unsafe, location=location):
                    def mutate(options):
                        path = options["sources"] / "guidance.json"
                        config = read_json(path)
                        if location == "intro":
                            config["intro"] = unsafe
                        elif location == "group":
                            config["groups"][0]["source"] = unsafe
                        else:
                            path = options["sources"] / "arc42/manifest.json"
                            config = read_json(path)
                            config["guidance"]["source"] = unsafe
                        write_json(path, config)
                    self.assert_invalid_preserves_outputs(mutate)
        for destination in (PROPOSAL, PROPOSAL + "/child"):
            with self.subTest(destination=destination):
                def mutate(options):
                    path = options["sources"] / "arc42/manifest.json"
                    manifest = read_json(path)
                    manifest["files"][destination] = "schema:templates/config.yaml"
                    write_json(path, manifest)
                self.assert_invalid_preserves_outputs(mutate)

    def test_symlink_guidance_source_preserves_matrix(self):
        def mutate(options):
            path = options["root"] / "src/project_templates/documentation/files/agent-intro.md"
            target = options["root"] / "original-intro.md"
            path.rename(target)
            path.symlink_to(target)
        self.assert_invalid_preserves_outputs(mutate, local_root=True)

    def test_fenced_headings_are_preserved_and_real_headings_are_nested(self):
        with tempfile.TemporaryDirectory() as temporary:
            options = self.fixture(temporary, local_root=True)
            path = options["root"] / "fragment.md"
            path.write_text("# Authoring\n\n## Detail\n\n```markdown\n# Literal\n"
                            "###### Also literal\n```\n\n~~~md\n## Tilde literal\n~~~\n")
            manifest_path = options["sources"] / "arc42/manifest.json"
            manifest = read_json(manifest_path)
            manifest["guidance"]["source"] = "fragment.md"
            write_json(manifest_path, manifest)
            text, _ = self.proposal(("arc42",), **options)
            self.assertIn("\n##### Authoring\n", text)
            self.assertIn("\n###### Detail\n", text)
            self.assertIn("```markdown\n# Literal\n###### Also literal\n```", text)
            self.assertIn("~~~md\n## Tilde literal\n~~~", text)

    def test_overdeep_source_headings_and_unresolved_markers_preserve_matrix(self):
        for content in ("# Parent\n\n### Too deep\n", "{{hook:project.agent-instructions}}\n",
                        "{{group:unknown}}\n", "{{slot:unknown}}\n"):
            with self.subTest(content=content):
                def mutate(options):
                    (options["root"] / "fragment.md").write_text(content)
                    path = options["sources"] / "arc42/manifest.json"
                    manifest = read_json(path)
                    manifest["guidance"]["source"] = "fragment.md"
                    write_json(path, manifest)
                self.assert_invalid_preserves_outputs(mutate, local_root=True)


if __name__ == "__main__":
    unittest.main()
