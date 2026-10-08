"""Install browser assets with the selected Mermaid binary, in scratch only."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from cache_lock import cache_lock

NAMES = ('mermaid.min.js', 'mermaid-init.js')


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _metadata(directory: Path, identity: str) -> dict:
    files = {}
    for name in NAMES:
        path = directory / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
            raise ValueError(f'Mermaid install did not produce a nonempty regular {name}')
        files[name] = _sha(path)
    return {'identity': identity, 'sha256': files}


def _valid(directory: Path, identity: str) -> bool:
    try:
        metadata = json.loads((directory / 'integrity.json').read_text(encoding='utf-8'))
        return metadata == _metadata(directory, identity)
    except (OSError, ValueError):
        return False


def ensure_mermaid_assets(builder_dir: Path, identity: str,
                          install: Callable[[Path], None]) -> tuple[Path, Path]:
    """Reuse only complete integrity-checked assets; callback installs in a mini-book.

    The cache belongs to the builder, not the selected documentation project.
    Docker callbacks must extract the pinned image's assets into the scratch root.
    """
    if not identity:
        raise ValueError('Mermaid asset identity must not be empty')
    slug = re.sub(r'[^A-Za-z0-9._-]', '-', identity)[:60].strip('.-') or 'binary'
    key = slug + '-' + hashlib.sha256(identity.encode()).hexdigest()
    base = builder_dir.resolve() / '.cache/scripts/mermaid'
    target = base / key
    with cache_lock(base / f'{key}.lock'):
        if not _valid(target, identity):
            _install_assets(target, identity, install)
        return tuple(target / name for name in NAMES)


def _install_assets(target: Path, identity: str, install: Callable[[Path], None]) -> None:
    with tempfile.TemporaryDirectory(prefix='.install-', dir=target.parent) as work:
        scratch = Path(work) / 'book'
        scratch.mkdir()
        (scratch / 'src').mkdir()
        (scratch / 'src/SUMMARY.md').write_text('# Summary\n', encoding='utf-8')
        (scratch / 'book.toml').write_text('[book]\ntitle = "Mermaid assets"\nsrc = "src"\n', encoding='utf-8')
        install(scratch)
        metadata = _metadata(scratch, identity)
        stage = Path(work) / 'assets'
        stage.mkdir()
        for name in NAMES:
            shutil.copyfile(scratch / name, stage / name)
        if _metadata(stage, identity) != metadata:
            raise ValueError('Mermaid assets changed during cache staging')
        (stage / 'integrity.json').write_text(json.dumps(metadata, sort_keys=True), encoding='utf-8')
        # Keep an old cache until the replacement is fully verified and staged.
        backup = Path(work) / 'old'
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(stage, target)
        except OSError:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise


def native_mermaid_assets(binary: Path, builder_dir: Path) -> tuple[Path, Path]:
    """Identity includes both actual selected executable bytes and its version."""
    binary = binary.resolve(strict=True)
    version = subprocess.run([str(binary), '--version'], check=True,
                             capture_output=True, text=True).stdout.strip()
    identity = f'native:{version}:sha256:{_sha(binary)}'
    def install(scratch: Path) -> None:
        subprocess.run([str(binary), 'install', str(scratch)], cwd=scratch, check=True)
    return ensure_mermaid_assets(builder_dir, identity, install)
