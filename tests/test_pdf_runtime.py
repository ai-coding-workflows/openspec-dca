"""Offline tests of the optional PDF environment lifecycle."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "scripts/md-book-builder/pdf_runtime.py"
spec = importlib.util.spec_from_file_location("pdf_runtime", MODULE)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class PdfRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.builder = Path(self.temp.name) / "builder"
        self.requirements = self.builder / "exporter/requirements-pdf.txt"
        self.requirements.parent.mkdir(parents=True)
        self.requirements.write_text("typst==0.15.0\ntomli==2.2.1; python_version < '3.11'\n")
        self.venv = patch.object(runtime.venv, "EnvBuilder").start()
        self.run = patch.object(runtime.subprocess, "run").start()
        self.addCleanup(patch.stopall)
        self.venv.return_value.create.side_effect = self.fake_create
        self.run.side_effect = self.fake_run

    def config(self):
        return runtime._configuration(self.builder)

    def fake_create(self, target):
        python = runtime._python(target)
        python.parent.mkdir(exist_ok=True)
        python.touch()

    def fake_run(self, command, **kwargs):
        if "pip" in command:
            return subprocess.CompletedProcess(command, 0)
        target, _, _, pin = self.config()
        return subprocess.CompletedProcess(command, 0, json.dumps({
            "version": list(sys.version_info[:2]), "prefix": str(target.resolve()), "typst": pin,
        }))

    def managed(self, ready=True):
        target, _, identity, _ = self.config()
        target.mkdir(parents=True)
        runtime._write_marker(target / runtime._OWNER, identity)
        self.fake_create(target)
        if ready:
            runtime._write_marker(target / runtime._READY, identity)
        return target

    def assert_not_ready(self):
        target, _, _, _ = self.config()
        self.assertFalse((target / runtime._READY).exists())
        self.assertFalse(target.with_name(target.name + ".lock").exists())

    def test_no_install_does_not_write_or_probe_host(self):
        before = sorted(self.builder.rglob("*"))
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "Enable"):
            runtime.ensure_pdf_python(self.builder, allow_install=False)
        self.assertEqual(before, sorted(self.builder.rglob("*")))
        self.venv.assert_not_called()
        self.run.assert_not_called()

    def test_reuse_only_probes_managed_interpreter(self):
        target = self.managed()
        self.assertEqual(runtime.ensure_pdf_python(self.builder, allow_install=False), runtime._python(target))
        self.venv.assert_not_called()
        command = self.run.call_args.args[0]
        self.assertEqual(command[:3], [str(runtime._python(target)), "-I", "-c"])
        self.assertIn("import typst", command[3])
        self.assertIn("import tomli", command[3])

    def test_install_lifecycle_and_command(self):
        target, _, identity, _ = self.config()
        def create(path):
            self.assertTrue(runtime._marker_matches(path / runtime._OWNER, identity))
            self.assertFalse((path / runtime._READY).exists())
            self.assertTrue(path.with_name(path.name + ".lock").is_dir())
            self.fake_create(path)
        self.venv.return_value.create.side_effect = create
        with patch.object(runtime, "print") as log:
            python = runtime.ensure_pdf_python(self.builder)
        self.venv.assert_called_once_with(with_pip=True)
        self.assertEqual(python, runtime._python(target))
        self.assertEqual(self.run.call_args_list[0].args[0], [
            str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(self.requirements),
        ])
        self.assertEqual(self.run.call_args_list[0].kwargs, {"check": True, "timeout": 600})
        self.assertTrue(runtime._marker_matches(target / runtime._READY, identity))
        self.assertFalse(target.with_name(target.name + ".lock").exists())
        self.assertIs(log.call_args.kwargs["file"], sys.stderr)

    def test_requirements_and_interpreter_changes_partition_cache(self):
        original = self.config()[0]
        self.requirements.write_text("typst==0.16.0\n")
        changed = self.config()[0]
        self.assertNotEqual(original, changed)
        with patch.object(runtime.sys, "version_info", (3, 10, 99)):
            self.assertNotEqual(changed, self.config()[0])
        with patch.object(runtime.sys, "executable", str(MODULE)):
            self.assertNotEqual(changed, self.config()[0])
        with patch.object(runtime.sysconfig, "get_platform", return_value="other-platform"):
            self.assertNotEqual(changed, self.config()[0])

    def test_wrong_version_prefix_pin_and_broken_probe_rejected_without_writes(self):
        target = self.managed()
        expected = {"version": list(sys.version_info[:2]), "prefix": str(target), "typst": "0.15.0"}
        for field, value in [("version", [0, 0]), ("prefix", str(self.builder)), ("typst", "0.14.0")]:
            with self.subTest(field=field):
                self.run.side_effect = None
                self.run.return_value = subprocess.CompletedProcess([], 0, json.dumps(dict(expected, **{field: value})))
                with self.assertRaises(runtime.PdfEnvironmentError):
                    runtime.ensure_pdf_python(self.builder, allow_install=False)
        self.run.side_effect = subprocess.CalledProcessError(1, ["python"])
        with self.assertRaises(runtime.PdfEnvironmentError):
            runtime.ensure_pdf_python(self.builder, allow_install=False)
        self.venv.assert_not_called()

    def test_owned_partial_retries(self):
        target = self.managed(ready=False)
        with self.assertRaises(runtime.PdfEnvironmentError):
            runtime.ensure_pdf_python(self.builder, allow_install=False)
        self.run.assert_not_called()
        self.assertEqual(runtime.ensure_pdf_python(self.builder), runtime._python(target))
        self.assertTrue((target / runtime._READY).exists())

    def test_invalid_ready_marker_and_missing_python_are_repaired(self):
        target = self.managed()
        (target / runtime._READY).write_text("interrupted JSON")
        runtime._python(target).unlink()
        with self.assertRaises(runtime.PdfEnvironmentError):
            runtime.ensure_pdf_python(self.builder, allow_install=False)
        self.assertEqual((target / runtime._READY).read_text(), "interrupted JSON")
        runtime.ensure_pdf_python(self.builder)
        self.assertTrue(runtime._python(target).is_file())
        self.assertTrue(runtime._marker_matches(target / runtime._READY, self.config()[2]))

    def test_pip_failure_is_retryable(self):
        self.run.side_effect = subprocess.CalledProcessError(1, ["pip"])
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "pip output/network"):
            runtime.ensure_pdf_python(self.builder)
        self.assert_not_ready()
        self.run.side_effect = self.fake_run
        runtime.ensure_pdf_python(self.builder)
        self.assertTrue((self.config()[0] / runtime._READY).exists())

    def test_creation_errors_and_interrupt_cleanup(self):
        for error in [OSError("ensurepip unavailable"), ModuleNotFoundError("ensurepip"), PermissionError("denied"), KeyboardInterrupt()]:
            with self.subTest(error=type(error).__name__):
                self.venv.return_value.create.side_effect = error
                expected = KeyboardInterrupt if isinstance(error, KeyboardInterrupt) else runtime.PdfEnvironmentError
                with self.assertRaises(expected):
                    runtime.ensure_pdf_python(self.builder)
                self.assert_not_ready()

    def test_unavailable_venv_is_actionable(self):
        with patch.object(runtime, "venv", None):
            with self.assertRaisesRegex(runtime.PdfEnvironmentError, "venv is unavailable"):
                runtime.ensure_pdf_python(self.builder)
        self.assert_not_ready()

    def test_timeout_and_verification_failure_do_not_mark_ready(self):
        self.run.side_effect = subprocess.TimeoutExpired(["pip"], 600)
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "timed out"):
            runtime.ensure_pdf_python(self.builder)
        self.assert_not_ready()
        def fail_probe(command, **kwargs):
            if "pip" in command:
                return subprocess.CompletedProcess(command, 0)
            return subprocess.CompletedProcess(command, 0, "not JSON")
        self.run.side_effect = fail_probe
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "verification failed"):
            runtime.ensure_pdf_python(self.builder)
        self.assert_not_ready()

    def test_unowned_target_refused(self):
        target = self.config()[0]
        target.mkdir(parents=True)
        sentinel = target / "unrelated"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "unowned"):
            runtime.ensure_pdf_python(self.builder)
        self.assertEqual(sentinel.read_text(), "keep")
        self.venv.assert_not_called()

    def test_target_and_cache_symlinks_refused(self):
        target = self.config()[0]
        target.parent.mkdir()
        target.symlink_to(self.builder / "missing", target_is_directory=True)
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "unowned"):
            runtime.ensure_pdf_python(self.builder)
        target.unlink()
        target.parent.rmdir()
        target.parent.symlink_to(self.builder / "elsewhere", target_is_directory=True)
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "symlinked PDF cache"):
            runtime.ensure_pdf_python(self.builder)
        self.venv.assert_not_called()

    def test_external_symlink_in_partial_env_refused(self):
        target = self.managed(ready=False)
        (target / "lib").symlink_to(self.builder / "exporter", target_is_directory=True)
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "external symlink"):
            runtime.ensure_pdf_python(self.builder)
        self.venv.assert_not_called()
        self.assert_not_ready()

    def test_existing_lock_is_not_removed(self):
        target = self.managed()
        lock = target.with_name(target.name + ".lock")
        lock.mkdir()
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "Retry after setup"):
            runtime.ensure_pdf_python(self.builder)
        self.assertTrue(lock.is_dir())
        self.run.assert_not_called()

    def test_lock_race_refused_and_not_cleaned(self):
        target = self.config()[0]
        target.parent.mkdir()
        lock = target.with_name(target.name + ".lock")
        original = Path.mkdir
        def mkdir(path, *args, **kwargs):
            if path == lock:
                original(path)
                raise FileExistsError()
            return original(path, *args, **kwargs)
        with patch.object(Path, "mkdir", mkdir):
            with self.assertRaisesRegex(runtime.PdfEnvironmentError, "locked"):
                runtime.ensure_pdf_python(self.builder)
        self.assertTrue(lock.is_dir())
        self.venv.assert_not_called()

    def test_ready_marker_symlink_refused(self):
        target = self.managed(ready=False)
        (target / runtime._READY).symlink_to(self.requirements)
        with self.assertRaisesRegex(runtime.PdfEnvironmentError, "symlinked PDF completion"):
            runtime.ensure_pdf_python(self.builder)
        self.assertTrue(self.requirements.exists())
        self.venv.assert_not_called()


if __name__ == "__main__":
    unittest.main()
