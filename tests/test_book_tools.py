"""Offline coverage for configuration-selected tooling and builder-owned caches."""
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/md-book-builder"
sys.path.insert(0, str(BUILDER))
from book_paths import read_book_paths
import svgbob

spec = importlib.util.spec_from_file_location("book_tools_runner", BUILDER / "book.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class BookToolsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = self.root / "book.other.toml"
        self.cache = self.root / "scripts/md-book-builder/.cache/native-tools"

    def paths(self, extra=""):
        self.config.write_text('[book]\nsrc="docs"\n[build]\nbuild-dir="site/html"\n' + extra)
        return read_book_paths(self.config)

    def test_mermaid_selection_respects_selected_config_and_custom_commands(self):
        for extra, expected in (("", False), ('[preprocessor.mermaid]\n', True),
                                ('[preprocessor.mermaid]\ncommand="mdbook-mermaid"\n', True),
                                ('[preprocessor.mermaid]\ncommand="my-mermaid --flag"\n', False)):
            with self.subTest(extra=extra):
                paths = self.paths(extra)
                original = self.config.read_bytes()
                with patch.object(runner.shutil, "which", side_effect=lambda name: "/tools/" + name) as which:
                    commands, status = runner.native_toolchain(paths)
                self.assertEqual(status, 0)
                self.assertEqual(list(commands), ["mdbook", "mdbook-mermaid"] if expected else ["mdbook"])
                self.assertEqual(which.call_count, 2 if expected else 1)
                self.assertEqual(self.config.read_bytes(), original)

    def test_malformed_preprocessor_tables_fail_clearly(self):
        for content in ('preprocessor = []\n', '[preprocessor]\nmermaid = "invalid"\n'):
            self.config.write_text(content)
            with self.subTest(content=content), self.assertRaisesRegex(ValueError, 'must be a table'):
                runner.requires_mermaid(self.config)

    def test_downloader_receives_only_missing_required_tools_and_internal_cache(self):
        paths = self.paths('[preprocessor.mermaid]\n')
        for missing in ("mdbook", "mdbook-mermaid"):
            with self.subTest(missing=missing), patch.object(runner, "NATIVE_TOOLS_CACHE", self.cache), \
                    patch.object(runner.shutil, "which", side_effect=lambda name: None if name == missing else "/tools/" + name), \
                    patch.object(runner.subprocess, "run", return_value=SimpleNamespace(
                        returncode=0, stdout=json.dumps({missing: "/cache/" + missing}), stderr="")) as download:
                commands, status = runner.native_toolchain(paths)
                self.assertEqual(status, 0)
                self.assertEqual(commands[missing], "/cache/" + missing)
                self.assertEqual(download.call_args.args[0],
                                 [sys.executable, str(runner.MD_BOOK_DOWNLOADER), str(self.cache), missing])
        self.assertFalse(paths.output_root.exists())

    def test_native_accepts_mdbook_only_and_keeps_native_build_destination(self):
        paths = self.paths()
        with patch.object(runner, "native_toolchain", return_value=({"mdbook": "/mdbook/bin/mdbook"}, 0)), \
                patch.object(runner, "NATIVE_TOOLS_CACHE", self.cache), \
                patch.object(runner, "prepare_svgbob", return_value=None) as prepare, \
                patch.object(runner, "staged_book", return_value=nullcontext(self.root)), \
                patch.object(runner, "serve_process", return_value=0) as serve:
            self.assertEqual(runner.native_command("serve", paths, 3000, False), 0)
        prepare.assert_called_once_with(self.config, self.cache)
        env = serve.call_args.kwargs["env"]
        self.assertTrue(env["PATH"].startswith("/mdbook/bin"))
        self.assertEqual(json.loads(env["MDBOOK_BUILD__BUILD_DIR"]), str(paths.build_dir))

    def test_docker_selects_mermaid_and_uses_readonly_cache_path(self):
        for extra, enabled in (("", "false"), ('[preprocessor.mermaid]\n', "true"),
                               ('[preprocessor.mermaid]\ncommand="custom"\n', "false")):
            paths = self.paths(extra)
            binary = self.cache / "mdbook-svgbob/linux/revision/mdbook-svgbob"
            with self.subTest(extra=extra), patch.object(runner, "REPOSITORY", self.root), \
                    patch.object(runner, "NATIVE_TOOLS_CACHE", self.cache), \
                    patch.object(runner.shutil, "which", return_value="docker"), \
                    patch.object(runner, "prepare_svgbob", return_value=binary) as prepare, \
                    patch.object(runner, "staged_book", return_value=nullcontext(self.root)), \
                    patch.object(runner, "docker_mermaid_assets", return_value=()), \
                    patch.object(runner, "update_book_config", return_value=False), \
                    patch.object(runner, "run", return_value=0) as run, \
                    patch.object(runner, "serve_process", return_value=0):
                self.assertEqual(runner.docker_command("serve", paths, 3000, False), 0)
                prepare.assert_called_once_with(self.config, self.cache, docker_mode=True)
                env = run.call_args.kwargs["env"]
                self.assertEqual(env["DOCS_WITH_MERMAID"], enabled)
                self.assertEqual(env["DOCS_SVGBOB_BIN"],
                                 "/book/scripts/md-book-builder/.cache/native-tools/mdbook-svgbob/linux/revision")

    def test_docker_svgbob_always_builds_linux_even_on_windows_host(self):
        self.paths('[preprocessor.svgbob]\n')
        with patch.object(svgbob.sys, "platform", "win32"), \
                patch.object(svgbob.platform, "machine", return_value="AMD64"), \
                patch.object(svgbob, "install", return_value=self.cache / "mdbook-svgbob") as install:
            svgbob.prepare(self.config, self.cache, docker_mode=True)
        install.assert_called_once_with(self.cache, "x86_64-unknown-linux-musl", "linux/amd64")

    def test_dockerfile_selection_filters_before_downloading_pinned_tools(self):
        dockerfile = (BUILDER / "docker/Dockerfile").read_text()
        self.assertIn('RUN python3 /opt/docs-toolchain/install-mdbook.py "$TARGETARCH"', dockerfile)
        source = (BUILDER / "docker/install-mdbook.py").read_text()
        # Exercise tool selection without downloads or filesystem writes.
        selection = source.split("for name, repository, version, expected_digest in tools:")[0]
        for enabled, count in (("false", 1), ("true", 2)):
            namespace = {"__file__": str(BUILDER / "docker/install-mdbook.py")}
            with patch.dict("os.environ", {"DOCS_WITH_MERMAID": enabled}), patch.object(sys, "argv", ["installer", "amd64"]):
                exec(selection, namespace)
            self.assertEqual(len(namespace["tools"]), count)
        compose = runner.COMPOSE_FILE.read_text()
        self.assertIn("DOCS_WITH_MERMAID: ${DOCS_WITH_MERMAID:-false}", compose)
        self.assertIn("DOCS_PROJECT_HOST", compose)
        self.assertIn("DOCS_BUILDER_HOST", compose)
        self.assertIn("target: /book-builder", compose)
        self.assertNotIn("../../..:/book", compose)
        self.assertIn("target: /book-export", compose)
        self.assertIn(".cache/", (BUILDER / ".gitignore").read_text())


if __name__ == "__main__":
    unittest.main()
