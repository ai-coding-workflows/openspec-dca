import hashlib
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = ROOT / "scripts" / "md-book-builder" / "download-latest-mdbook.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("mdbook_installer", INSTALLER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MdBookInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def test_install_defaults_to_both_tools_and_supports_selection(self):
        for selected, expected in ((None, ["mdbook", "mdbook-mermaid"]),
                                   (["mdbook"], ["mdbook"]),
                                   (["mdbook-mermaid"], ["mdbook-mermaid"]), ([], [])):
            with self.subTest(selected=selected), mock.patch.object(
                self.installer, "target_asset", return_value=("target", "tar.gz")
            ), mock.patch.object(self.installer, "install_tool", return_value=Path("binary")) as install:
                result = self.installer.install(Path("cache"), selected)
                self.assertEqual(list(result), expected)
                self.assertEqual([call.args[1].name for call in install.call_args_list], expected)

    def test_install_rejects_unknown_names_before_any_download(self):
        with mock.patch.object(self.installer, "install_tool") as install:
            with self.assertRaisesRegex(ValueError, "unknown tool names"):
                self.installer.install(Path("cache"), ["other"])
            install.assert_not_called()

    def test_cli_retains_cache_only_and_accepts_tool_names(self):
        for arguments, selected in ((["cache"], None), (["cache", "mdbook"], ["mdbook"])):
            with mock.patch.object(sys, "argv", ["installer", *arguments]), mock.patch.object(
                self.installer, "install", return_value={"mdbook": Path("binary")}
            ) as install, mock.patch("builtins.print"):
                self.assertEqual(self.installer.main(), 0)
                install.assert_called_once_with(Path("cache").resolve(), selected)

    def test_supported_targets_match_both_release_families(self):
        cases = (
            ("linux", "x86_64", "x86_64-unknown-linux-musl", "tar.gz"),
            ("linux", "aarch64", "aarch64-unknown-linux-musl", "tar.gz"),
            ("darwin", "arm64", "aarch64-apple-darwin", "tar.gz"),
            ("win32", "AMD64", "x86_64-pc-windows-msvc", "zip"),
        )
        for system, machine, target, archive_type in cases:
            with self.subTest(system=system, machine=machine), mock.patch.object(
                self.installer.sys, "platform", system
            ), mock.patch.object(self.installer.platform, "machine", return_value=machine):
                self.assertEqual(self.installer.target_asset(), (target, archive_type))

    def test_installs_mermaid_from_its_checksum_verified_release(self):
        tool = next(tool for tool in self.installer.TOOLS if tool.name == "mdbook-mermaid")
        target = "x86_64-unknown-linux-musl"
        tag = "v1.2.3"
        archive = b"release archive"
        digest = hashlib.sha256(archive).hexdigest()
        asset_name = f"mdbook-mermaid-{tag}-{target}.tar.gz"
        release = {
            "tag_name": tag,
            "assets": [
                {
                    "name": asset_name,
                    "digest": f"sha256:{digest}",
                    "browser_download_url": (
                        f"https://github.com/badboy/mdbook-mermaid/releases/download/"
                        f"{tag}/{asset_name}"
                    ),
                    "size": len(archive),
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            self.installer, "latest_release", return_value=release
        ), mock.patch.object(
            self.installer, "request_bytes", return_value=archive
        ), mock.patch.object(
            self.installer, "extract_binary", return_value=b"executable"
        ), mock.patch.object(
            self.installer, "cached_binary_is_valid", side_effect=(False, True)
        ):
            result = self.installer.install_tool(
                Path(temporary), tool, target, "tar.gz"
            )

            self.assertEqual(
                result,
                Path(temporary) / "mdbook-mermaid" / target / tag / "mdbook-mermaid",
            )
            self.assertEqual(result.read_bytes(), b"executable")
            self.assertEqual(
                Path(f"{result}.sha256").read_text(encoding="ascii"),
                f"sha256:{digest}\n",
            )
            if os.name != "nt":
                self.assertTrue(os.access(result, os.X_OK))

    def test_rejects_mermaid_asset_from_an_unexpected_repository(self):
        tool = next(tool for tool in self.installer.TOOLS if tool.name == "mdbook-mermaid")
        target = "x86_64-unknown-linux-musl"
        tag = "v1.2.3"
        asset_name = f"mdbook-mermaid-{tag}-{target}.tar.gz"
        release = {
            "tag_name": tag,
            "assets": [
                {
                    "name": asset_name,
                    "digest": "sha256:" + "0" * 64,
                    "browser_download_url": (
                        f"https://github.com/example/fork/releases/download/{tag}/{asset_name}"
                    ),
                    "size": 100,
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            self.installer, "latest_release", return_value=release
        ):
            with self.assertRaisesRegex(RuntimeError, "unexpected release asset URL"):
                self.installer.install_tool(Path(temporary), tool, target, "tar.gz")


if __name__ == "__main__":
    unittest.main()
