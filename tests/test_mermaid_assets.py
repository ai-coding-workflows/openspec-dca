import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/md-book-builder'))
from mermaid_assets import ensure_mermaid_assets, native_mermaid_assets


class AssetTests(unittest.TestCase):
    def test_cache_integrity_identity_and_scratch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = []
            def install(scratch):
                self.assertTrue((scratch / 'book.toml').is_file())
                self.assertNotEqual(scratch, root)
                calls.append(scratch)
                for name in ('mermaid.min.js', 'mermaid-init.js'):
                    (scratch / name).write_text(name)
            assets = ensure_mermaid_assets(root, 'image:version/unsafe', install)
            self.assertEqual(assets, ensure_mermaid_assets(root, 'image:version/unsafe', install))
            self.assertEqual(len(calls), 1)
            assets[0].write_text('corrupted')
            ensure_mermaid_assets(root, 'image:version/unsafe', install)
            self.assertEqual(len(calls), 2)
            assets[1].unlink()
            ensure_mermaid_assets(root, 'image:version/unsafe', install)
            self.assertEqual(len(calls), 3)
            other = ensure_mermaid_assets(root, 'image:other', install)
            self.assertNotEqual(other, assets)
            self.assertTrue(all(not p.exists() for p in calls))

    def test_concurrent_processes_publish_once(self):
        script = '''
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from mermaid_assets import ensure_mermaid_assets
root = Path(sys.argv[2])
def install(scratch):
    with (root / 'calls').open('a') as stream:
        stream.write('install\\n')
    time.sleep(0.15)
    for name in ('mermaid.min.js', 'mermaid-init.js'):
        (scratch / name).write_text('selected binary')
ensure_mermaid_assets(root, 'shared selected binary', install)
'''
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, '-c', script, str(Path(__file__).resolve().parents[1] / 'scripts/md-book-builder'), directory]
            children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(3)]
            for child in children:
                _, error = child.communicate(timeout=15)
                self.assertEqual(child.returncode, 0, error)
            self.assertEqual((Path(directory) / 'calls').read_text(), 'install\n')

    def test_failed_install_does_not_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def incomplete(scratch):
                (scratch / 'mermaid.min.js').write_text('one')
            with self.assertRaises(ValueError):
                ensure_mermaid_assets(root, 'binary', incomplete)
            self.assertFalse(list(root.rglob('integrity.json')))

    def test_selected_binary_version_and_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / 'chosen binary'
            binary.write_bytes(b'first binary')
            calls = []
            def run(command, **kwargs):
                calls.append(command)
                if command[1] == '--version':
                    from subprocess import CompletedProcess
                    return CompletedProcess(command, 0, 'mdbook-mermaid 0.17.1\n')
                scratch = Path(command[2])
                for name in ('mermaid.min.js', 'mermaid-init.js'):
                    (scratch / name).write_text('selected')
            with patch('mermaid_assets.subprocess.run', side_effect=run):
                first = native_mermaid_assets(binary, root)
                binary.write_bytes(b'second binary')
                second = native_mermaid_assets(binary, root)
            self.assertNotEqual(first, second)
            self.assertTrue(all(c[0] == str(binary) for c in calls))
            self.assertEqual(sum(c[1] == 'install' for c in calls), 2)
