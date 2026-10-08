"""Root entry point: delegation, failure propagation, and portable invocation."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("root_build", ROOT / "build.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildEntryPointTests(unittest.TestCase):
    def test_default_build_and_forwarded_arguments(self):
        with patch.object(builder, "run", return_value=0) as run:
            self.assertEqual(builder.main([]), 0)
            run.assert_called_once_with("scripts/schema-builder/build.py")
        with patch.object(builder, "run", return_value=17) as run:
            self.assertEqual(builder.main(["schemas", "--base", "--output", "build/custom"]), 17)
            run.assert_called_once_with("scripts/schema-builder/build.py", "--base", "--output", "build/custom")
        with patch.object(builder, "run", return_value=0) as run:
            self.assertEqual(builder.main(["docs", "--docker"]), 0)
            run.assert_called_once_with("scripts/md-book-builder/book.py", "build", "--docker")

    def test_all_stops_on_failure(self):
        with patch.object(builder, "run", side_effect=[0, 7]) as run, patch.object(builder, "check") as check:
            self.assertEqual(builder.main(["all"]), 7)
            self.assertEqual(run.call_count, 2)
            check.assert_not_called()

    def test_all_runs_checks_after_both_builds(self):
        with patch.object(builder, "run", return_value=0) as run, patch.object(builder, "check", return_value=9) as check:
            self.assertEqual(builder.main(["all"]), 9)
            self.assertEqual(run.call_args_list[0].args, ("scripts/schema-builder/build.py",))
            self.assertEqual(run.call_args_list[1].args, ("scripts/md-book-builder/book.py", "build"))
            check.assert_called_once_with()

    def test_check_rejects_unsupported_cli_before_tests_can_skip(self):
        result = subprocess.CompletedProcess([], 0, "1.13.2\n", "")
        with patch.dict(builder.os.environ, {"OPENSPEC_BIN": "/test/openspec"}), \
                patch.object(builder.subprocess, "run", return_value=result), \
                patch.object(builder, "run") as run:
            self.assertEqual(builder.main(["check"]), 1)
            run.assert_not_called()

    def test_check_preserves_test_failure_and_runs_rendered_check_on_success(self):
        version = subprocess.CompletedProcess([], 0, "1.13.1\n", "")
        with patch.dict(builder.os.environ, {"OPENSPEC_BIN": "/test/openspec"}), \
                patch.object(builder.subprocess, "run", return_value=version):
            with patch.object(builder, "run", return_value=5) as run:
                self.assertEqual(builder.main(["check"]), 5)
                run.assert_called_once_with("-m", "unittest", "discover", "-s", "tests", "-v")
            with patch.object(builder, "run", side_effect=[0, 0]) as run:
                self.assertEqual(builder.main(["check"]), 0)
                self.assertEqual(run.call_args_list[-1].args, ("scripts/md-book-builder/check.py", "--rendered"))

    def test_real_invocation_from_another_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "schema with spaces"
            result = subprocess.run([sys.executable, str(ROOT / "build.py"), "schemas",
                                     "--base", "--output", str(output)],
                                    cwd=temp, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / "schema.yaml").is_file())
            self.assertTrue((output / "templates").is_dir())
