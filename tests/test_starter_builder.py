"""Starter composition, safe generation, and relocated native installation checks."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/starter-builder/build.py"
CLI = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec")
SELECTIONS = ((), ("arc42",), ("user-doc",), ("arc42", "user-doc"))
def schema_name(components):
    return "+".join(("ddd", *components))


def schema_prefix(components):
    return f"openspec/schemas/{schema_name(components)}/"

# Deliberately explicit: distribution must not silently grow to include caches,
# downloaded tools, virtual environments, or unrelated maintenance files.
BOOK_PAYLOAD = (
    ".gitignore", "book.py", "book_capture.py", "book_discovery.py",
    "book_environment.py", "book_features.py", "book_paths.py", "book_root.py",
    "book_runtime.py", "book_selection.py", "book_servers.py", "book_toml.py",
    "cache_lock.py", "capture_backend.py", "check.py", "download-latest-mdbook.py",
    "mermaid_assets.py", "pdf_runtime.py", "svgbob.py", "docker/.dockerignore",
    "docker/Dockerfile", "docker/compose.yml", "docker/install-mdbook.py",
    "docker/svgbob.Dockerfile", "docker/toolchain.json", "exporter/README.md",
    "exporter/__init__.py", "exporter/export_book.py", "exporter/markdown_to_typst.py",
    "exporter/render_context.py", "exporter/requirements-pdf.txt",
    "exporter/templates/default.typ", "exporter/templates/modern-guide.typ",
)


def load_builder(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_payload(payload):
    return {name: data.decode("utf-8") for name, (data, mode) in payload.items()}


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*") if path.is_file() and not path.is_symlink()}


def snapshot(root):
    """Include empty directories, links, and modes in preservation assertions."""
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


class StarterBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Missing production sources are failures, not skipped tool integrations.
        cls.builder = load_builder("starter_builder_tests", SCRIPT)
        cls.schema = load_builder("starter_schema_tests", ROOT / "scripts/schema-builder/build.py")

    def run_command(self, command, cwd, env=None):
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_compositions_install_exact_composed_schema_and_project_templates(self):
        for components in SELECTIONS:
            with self.subTest(components=components):
                expected = self.schema.compose(components)
                composed = text_payload(self.builder.compose(components=components))
                prefix = schema_prefix(components)
                installed = {name.removeprefix(prefix): text
                             for name, text in composed.items() if name.startswith(prefix)}
                self.assertEqual(installed, expected)
                for target, template in (("openspec/config.yaml", "config.yaml"),
                                         ("openspec/README.md", "openspec-README.md")):
                    self.assertEqual(composed[target], expected[f"templates/{template}"].replace(
                        "openspec-ddd", schema_name(components)))
                self.assertTrue(composed["openspec/config.yaml"].startswith(
                    f"schema: {schema_name(components)}\n"))
                self.assertFalse(any(name.startswith("openspec/schemas/openspec-ddd/")
                                     for name in composed))
                self.assertNotIn("{{schema-name}}", composed["README.md"])
                self.assertIn(f"openspec schema validate {schema_name(components)}",
                              composed["README.md"])
                self.assertNotIn("AGENTS.md", composed)
                proposal = composed["AGENTS.proposal.md"]
                self.assertIn("not active project instructions", proposal)
                self.assertIn("DDD foundation", proposal)
                self.assertTrue(composed["README.md"].strip())
                catalog = json.loads(composed["openspec/catalog.json"])
                self.assertEqual(catalog["schema_version"], 1)
                self.assertEqual(catalog["specs"], [])
                self.assertEqual(composed, text_payload(self.builder.compose(components=components)))
                self.assertFalse(any("{{hook:" in text for name, text in composed.items()
                                     if name.endswith((".md", ".yaml"))))
                self.assertFalse(any("__pycache__" in name or ".cache" in Path(name).parts
                                     or name.endswith(".pyc") for name in composed))
                self.assertFalse(any("user-documentation" in Path(name).parts for name in composed))
                for name, text in composed.items():
                    if name.endswith((".md", ".yaml", ".toml")):
                        self.assertNotIn("user-documentation/", text, name)

    def test_optional_books_use_canonical_pages_and_complete_maintained_runner(self):
        for components in SELECTIONS:
            with self.subTest(components=components):
                composed = text_payload(self.builder.compose(components=components))
                schema = self.schema.compose(components)
                for component, destination, template, config in (
                    ("arc42", "openspec/system-architecture", "system-architecture", "book.arc42.toml"),
                    ("user-doc", "user-doc", "user-doc", "book.user-doc.toml"),
                ):
                    selected = component in components
                    self.assertEqual(config in composed, selected)
                    self.assertEqual(f"{destination}/SUMMARY.md" in composed, selected)
                    prefix = f"templates/{template}/"
                    for name, text in schema.items():
                        if name.startswith(prefix):
                            if component == "user-doc" and name == prefix + "README.md":
                                text = (ROOT / "src/project_templates/user-doc/files/README.md").read_text()
                            self.assertEqual(composed[f"{destination}/{name.removeprefix(prefix)}"],
                                             text.replace("openspec-ddd", schema_name(components)))
                    if not selected:
                        self.assertFalse(any(name.startswith(destination + "/") for name in composed))
                self.assertEqual("book-builder.toml" in composed, bool(components))
                if "user-doc" in components:
                    self.assertIn('src = "user-doc"', composed["book.user-doc.toml"])
                    self.assertIn("user-doc/README.md", composed)
                    self.assertNotIn("user-documentation/README.md", composed)
                actual = {name.removeprefix("scripts/md-book-builder/") for name in composed
                          if name.startswith("scripts/md-book-builder/")}
                self.assertEqual(actual, set(BOOK_PAYLOAD) if components else set())
                for name in actual:
                    self.assertEqual(composed["scripts/md-book-builder/" + name],
                                     (ROOT / "scripts/md-book-builder" / name).read_text())
                for wrapper in ("scripts/book.sh", "scripts/book.cmd"):
                    self.assertEqual(wrapper in composed, bool(components))

    def test_documentation_manifest_declares_entire_maintained_tool_tree(self):
        manifest = json.loads((ROOT / "src/project_templates/documentation/manifest.json").read_text())
        tooling = manifest["tooling"]
        canonical = ROOT / tooling["source"]
        excluded_directories = {"__pycache__", ".venv", "venv", ".cache"}
        maintained = set()
        for path in canonical.rglob("*"):
            relative = path.relative_to(canonical)
            if any(part in excluded_directories or part.endswith(".cache")
                   for part in relative.parts):
                continue
            if path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_file():
                maintained.add(relative.as_posix())
        self.assertEqual(set(tooling["files"]), maintained)
        self.assertEqual(len(tooling["files"]), len(set(tooling["files"])))
        self.assertEqual(set(BOOK_PAYLOAD), maintained)

    def test_single_build_matches_composition_and_wrappers_are_executable(self):
        with tempfile.TemporaryDirectory() as temp:
            for components in SELECTIONS:
                output = Path(temp) / "+".join(("ddd", *components))
                self.builder.build(output, components=components)
                expected = {name: data for name, (data, mode) in self.builder.compose(components).items()}
                actual = files(output)
                self.assertIn(".starter-build.json", actual)
                actual.pop(".starter-build.json")
                self.assertEqual(actual, expected)
                if components:
                    self.assertTrue(os.access(output / "scripts/book.sh", os.X_OK))

    def test_binary_source_bytes_and_executable_permissions_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "payload.bin"
            source.write_bytes(b"\x00\xff\x80\r\n")
            source.chmod(0o755)
            sources = root / "sources"
            (sources / "base").mkdir(parents=True)
            (sources / "base/manifest.json").write_text(json.dumps({
                "files": {"assets/payload.bin": "payload.bin"}, "books": {}}))
            (root / "intro.md").write_text("# Agent instructions proposal\n")
            (sources / "guidance.json").write_text(json.dumps({
                "intro": "intro.md", "groups": [{"id": "base", "title": "Example", "always": True}]}))
            output = root / "project"
            self.builder.build(output, sources=sources, root=root)
            copied = output / "assets/payload.bin"
            self.assertEqual(copied.read_bytes(), source.read_bytes())
            self.assertEqual(copied.stat().st_mode & 0o777, source.stat().st_mode & 0o777)

    def test_ownership_records_materialized_not_requested_modes(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "starters"
            chmod = Path.chmod
            # Simulate a platform normalizing requested file permissions.
            with patch.object(Path, "chmod", autospec=True,
                              side_effect=lambda path, mode: chmod(path, 0o600)):
                self.builder.build_all(output)
                self.builder.verify_owned(output)
                self.builder.build_all(output)
                self.builder.verify_owned(output)

    def test_default_source_and_output_paths_use_project_templates(self):
        self.assertEqual(self.builder.SOURCES, ROOT / "src/project_templates")
        self.assertEqual(self.builder.DEFAULT_OUTPUT, ROOT / "build/project_templates")

    def test_matrix_is_four_variants_owned_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "starters"
            entries = self.builder.build_all(output=output)
            self.assertEqual(len(entries), 4)
            self.assertEqual({tuple(e["components"]) for e in entries}, set(SELECTIONS))
            self.assertTrue((output / ".starter-build.json").is_file())
            for entry in entries:
                variant = output / entry["path"]
                self.assertEqual(entry["schema"], entry["variant"])
                self.assertEqual([path.name for path in (variant / "openspec/schemas").iterdir()],
                                 [entry["variant"]])
                self.assertTrue((variant / "openspec/config.yaml").is_file())
                self.assertFalse((variant / "schema.yaml").exists())
                expected = {name: data for name, (data, mode) in
                            self.builder.compose(entry["components"]).items()}
                self.assertEqual(files(variant), expected)
            before = snapshot(output)
            self.assertEqual(entries, self.builder.build_all(output=output))
            self.assertEqual(before, snapshot(output))

    def test_matrix_rejects_modified_unowned_files_directories_and_symlinks(self):
        for mutation in ("modified", "mode", "file", "directory", "symlink", "manifest"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                output = root / "starters"
                entries = self.builder.build_all(output=output)
                if mutation == "modified":
                    (output / entries[0]["path"] / "AGENTS.proposal.md").write_text("Local changes\n")
                elif mutation == "mode":
                    (output / entries[0]["path"] / "AGENTS.proposal.md").chmod(0o600)
                elif mutation == "file":
                    (output / "mine.txt").write_text("Local file\n")
                elif mutation == "directory":
                    (output / "empty-local-directory").mkdir()
                elif mutation == "symlink":
                    target = root / "outside"
                    target.mkdir()
                    (output / "local-link").symlink_to(target, target_is_directory=True)
                else:
                    (output / ".starter-build.json").write_text("{}\n")
                before = snapshot(output)
                with self.assertRaises(ValueError):
                    self.builder.build_all(output=output)
                self.assertEqual(snapshot(output), before)

    def test_unowned_output_and_output_symlinks_are_not_adopted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            unowned = root / "unowned"
            unowned.mkdir()
            link = root / "link"
            link.symlink_to(unowned, target_is_directory=True)
            for output in (unowned, link):
                for operation in (self.builder.build, self.builder.build_all):
                    with self.subTest(output=output, operation=operation.__name__):
                        with self.assertRaises(ValueError):
                            operation(output)
            self.assertEqual(list(unowned.iterdir()), [])
            self.assertTrue(link.is_symlink())

    def test_late_composition_failure_preserves_previous_matrix(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "starters"
            self.builder.build_all(output=output)
            before = snapshot(output)
            compose = self.builder.compose
            calls = []

            def failing(*args, **kwargs):
                calls.append(args)
                if len(calls) == 2:
                    raise ValueError("Deliberate late composition failure")
                return compose(*args, **kwargs)

            with patch.object(self.builder, "compose", side_effect=failing):
                with self.assertRaisesRegex(ValueError, "late composition"):
                    self.builder.build_all(output=output)
            self.assertEqual(snapshot(output), before)

    def test_unsafe_payload_paths_cannot_escape_or_replace_previous_matrix(self):
        for unsafe in ("../escape.txt", "/escape.txt", "safe/../../escape.txt"):
            with self.subTest(path=unsafe), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                output = root / "starters"
                self.builder.build_all(output=output)
                before = snapshot(root)
                with patch.object(self.builder, "compose", return_value={unsafe: (b"unsafe\n", 0o644)}):
                    with self.assertRaises(ValueError):
                        self.builder.build_all(output=output)
                self.assertEqual(snapshot(root), before)

    def test_manifest_traversal_collisions_and_source_links_preserve_previous_build(self):
        cases = (
            ("../escape.txt", "schema:templates/config.yaml"),
            ("/escape.txt", "schema:templates/config.yaml"),
            ("safe/../../escape.txt", "schema:templates/config.yaml"),
            ("back\\slash.txt", "schema:templates/config.yaml"),
            ("AGENTS.md", "schema:templates/config.yaml"),
            ("AGENTS.proposal.md", "schema:templates/config.yaml"),
            ("openspec", "schema:templates/config.yaml"),
            ("AGENTS.proposal.md/child", "schema:templates/config.yaml"),
            (".starter-build.json", "schema:templates/config.yaml"),
            ("escape.txt", "schema:../config.yaml"),
            ("escape.txt", "../outside.txt"),
            ("escape.txt", "/outside.txt"),
        )
        for destination, source in cases:
            with self.subTest(destination=destination, source=source), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                sources = root / "sources"
                shutil.copytree(ROOT / "src/project_templates", sources)
                output = root / "starters"
                self.builder.build_all(output=output, sources=sources)
                before = snapshot(output)
                manifest_path = sources / "arc42/manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["files"][destination] = source
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    self.builder.build_all(output=output, sources=sources)
                self.assertEqual(snapshot(output), before)
                self.assertFalse((root / "escape.txt").exists())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sources = root / "sources"
            shutil.copytree(ROOT / "src/project_templates", sources)
            output = root / "starters"
            self.builder.build_all(output=output, sources=sources)
            before = snapshot(output)
            manifest = sources / "arc42/manifest.json"
            original = root / "original.json"
            manifest.rename(original)
            manifest.symlink_to(original)
            with self.assertRaises(ValueError):
                self.builder.build_all(output=output, sources=sources)
            self.assertEqual(snapshot(output), before)

    def test_publish_rename_failure_restores_previous_matrix(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "starters"
            self.builder.build_all(output=output)
            before = snapshot(output)
            rename = Path.rename

            def fail_publish(path, target):
                if path.name == "starters" and path.parent.name.startswith(".starter-build-"):
                    raise OSError("Deliberate publication failure")
                return rename(path, target)

            with patch.object(Path, "rename", autospec=True, side_effect=fail_publish):
                with self.assertRaisesRegex(OSError, "publication failure"):
                    self.builder.build_all(output=output)
            self.assertEqual(snapshot(output), before)

    def test_cli_single_selections_require_output_and_build_expected_projects(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for selection in (("--base",), ("--component", "arc42")):
                result = subprocess.run([sys.executable, str(SCRIPT), *selection], cwd=root,
                                        capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--output", result.stderr)
                self.assertEqual(list(root.iterdir()), [])
            for components in SELECTIONS:
                output = root / "+".join(("ddd", *components))
                selection = [item for component in components for item in ("--component", component)]
                self.run_command([sys.executable, str(SCRIPT), *(selection or ["--base"]),
                                  "--output", str(output)], root)
                self.assertTrue((output / "openspec/config.yaml").is_file())

    def test_relocated_metadata_and_docs_source_checks_are_read_only(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            # Python's normal import cache is not documentation delivery output.
            # Disable it to compare maintained sources and outputs byte-for-byte.
            check_env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            for components in SELECTIONS:
                project = root / "+".join(("ddd", *components))
                self.builder.build(project, components=components)
                helpers = project / schema_prefix(components) / "helpers"
                before = snapshot(project)
                self.run_command([sys.executable, str(helpers / "check.py")], outside, check_env)
                if components:
                    self.run_command([sys.executable, str(helpers / "docs-check.py"),
                                      "--source-only"], outside, check_env)
                    self.assertEqual(before, snapshot(project))
                    original = project / "scripts/md-book-builder"
                    relocated = project / "tools/documentation/md-book-builder"
                    relocated.parent.mkdir(parents=True)
                    shutil.move(str(original), relocated)
                    before = snapshot(project)
                    self.run_command([sys.executable, str(helpers / "docs-check.py"),
                                      "--builder", str(relocated / "book.py"), "--source-only"], outside, check_env)
                    env = dict(os.environ, BOOK_BUILDER=str(relocated / "book.py"),
                               PYTHONDONTWRITEBYTECODE="1")
                    self.run_command([str(project / "scripts/book.sh"), "--help"], outside, env)
                self.assertEqual(before, snapshot(project))
                if components:
                    destination = "user-doc" if "user-doc" in components else "openspec/system-architecture"
                    broken = project / destination / "README.md"
                    broken.write_text(broken.read_text() + "\n[Missing](starter-missing-page.md)\n")
                    before = snapshot(project)
                    result = subprocess.run(
                        [sys.executable, str(helpers / "docs-check.py"), "--builder",
                         str(relocated / "book.py"), "--source-only"], cwd=outside, env=check_env,
                        capture_output=True, text=True, timeout=30)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(before, snapshot(project))

    @unittest.skipUnless(shutil.which("mdbook") and shutil.which("mdbook-mermaid"),
                         "Install mdbook and mdbook-mermaid for starter rendering integration")
    def test_copied_documentation_starters_build_all_selected_books(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            matrix = root / "distribution"
            entries = self.builder.build_all(matrix)
            for entry in entries:
                components = entry["components"]
                if not components:
                    continue
                with self.subTest(components=components):
                    project = root / "installed" / entry["path"]
                    shutil.copytree(matrix / entry["path"], project)
                    destination = ("openspec/system-architecture" if "arc42" in components
                                   else "user-doc")
                    landing = project / destination / "README.md"
                    landing.write_text(landing.read_text() +
                                       "\n```mermaid\nflowchart LR\n    Reader --> Starter\n```\n")
                    before = {name: data for name, data in files(project).items()
                              if name.endswith(".md") and not name.startswith("scripts/")}
                    self.run_command([sys.executable, str(project / "scripts/md-book-builder/book.py"),
                                      "build"], project)
                    checker = project / "scripts/md-book-builder/check.py"
                    for component in components:
                        output = project / "build/books" / component
                        html = (output / "index.html").read_text()
                        self.assertTrue(list(output.glob("*.md")), "Missing Markdown export")
                        if component == ("arc42" if "arc42" in components else "user-doc"):
                            self.assertIn('class="mermaid"', html)
                            self.assertRegex(html, r'mermaid-init(?:-[a-f0-9]+)?\.js')
                        self.run_command([sys.executable, str(checker), "--book", component,
                                          "--rendered"], project)
                    for name, data in before.items():
                        self.assertEqual((project / name).read_bytes(), data, name)

    @unittest.skipUnless(CLI, "Install OpenSpec 1.13.1 or set OPENSPEC_BIN for integration tests")
    def test_copied_starters_initialize_with_supported_native_pi_without_config_overwrite(self):
        self.assertEqual(subprocess.check_output([CLI, "--version"], text=True).strip(), "1.13.1")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            matrix = root / "generated"
            entries = self.builder.build_all(output=matrix)
            for entry in entries:
                with self.subTest(components=entry["components"]):
                    project = root / "installed" / entry["path"]
                    shutil.copytree(matrix / entry["path"], project)
                    self.assertFalse((project / "AGENTS.md").exists())
                    self.assertTrue((project / "AGENTS.proposal.md").is_file())
                    config = (project / "openspec/config.yaml").read_bytes()
                    env = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1",
                               OPENSPEC_NO_UPDATE_CHECK="1", XDG_CONFIG_HOME=str(root / "config"),
                               XDG_DATA_HOME=str(root / "data"))
                    self.run_command([CLI, "init", "--tools", "pi", "--profile", "core",
                                      "--no-animation"], project, env)
                    self.assertEqual((project / "openspec/config.yaml").read_bytes(), config)
                    self.assertTrue((project / ".pi/prompts/opsx-propose.md").is_file())
                    self.assertTrue((project / ".pi/skills/openspec-propose/SKILL.md").is_file())
                    selected_schema = entry["variant"]
                    self.run_command([CLI, "schema", "validate", selected_schema], project, env)
                    templates = json.loads(self.run_command(
                        [CLI, "templates", "--schema", selected_schema, "--json"], project, env))
                    self.assertTrue(templates)
                    self.run_command([CLI, "new", "change", "starter-smoke"], project, env)
                    status = json.loads(self.run_command(
                        [CLI, "status", "--change", "starter-smoke", "--json"], project, env))
                    self.assertEqual(status["schemaName"], selected_schema)
                    self.assertEqual(len(status["artifacts"]), 7)


if __name__ == "__main__":
    unittest.main()
