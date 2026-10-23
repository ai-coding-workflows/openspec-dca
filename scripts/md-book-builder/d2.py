"""Provision optional D2 executables in the builder cache, never globally."""
from pathlib import Path
import json
import hashlib
import os
import platform
import runpy
import shlex
import sys
import tempfile
import shutil

from book_features import read_config
from cache_lock import cache_lock


MANIFEST = Path(__file__).with_name('d2-toolchain.json')
DEFAULT_CACHE = Path(__file__).parent / '.cache/native-tools'


def asset_name(name: str, version: str) -> tuple[str, str]:
    arch = {'x86_64': 'amd64', 'amd64': 'amd64', 'arm64': 'arm64',
            'aarch64': 'arm64'}.get(platform.machine().lower())
    system = 'linux' if sys.platform.startswith('linux') else {
        'darwin': 'macos', 'win32': 'windows'}.get(sys.platform)
    if not arch or not system:
        raise RuntimeError(f'Unsupported D2 platform: {sys.platform} {platform.machine()}')
    executable = name + ('.exe' if system == 'windows' else '')
    if name == 'd2':
        return f'd2-{version}-{system}-{arch}.tar.gz', executable
    cpu = 'x86_64' if arch == 'amd64' else 'aarch64'
    target = {'linux': 'unknown-linux-musl', 'macos': 'apple-darwin',
              'windows': 'pc-windows-msvc'}[system]
    extension = 'zip' if system == 'windows' else 'tar.gz'
    return f'mdbook-d2-{cpu}-{target}.{extension}', executable


def valid_binary(binary: Path) -> bool:
    marker = Path(str(binary) + '.sha256')
    return (binary.is_file() and marker.is_file()
            and (os.name == 'nt' or os.access(binary, os.X_OK))
            and marker.read_text().strip() == hashlib.sha256(binary.read_bytes()).hexdigest())


def install(cache: Path, name: str, *, allow_install: bool = True) -> Path:
    tool = json.loads(MANIFEST.read_text(encoding='utf-8'))[name]
    asset, executable = asset_name(name, tool['version'])
    digest = tool['assets'][asset]
    destination = cache / name / asset.removesuffix('.tar.gz').removesuffix('.zip') / digest[:16] / executable
    with cache_lock(destination.parent / '.lock'):
        if valid_binary(destination):
            return destination
        if not allow_install:
            raise RuntimeError(f'{name} is missing from PATH/cache; --no-install disables D2 downloads')
        # Reuse the canonical downloader's bounded HTTP client and safe archive
        # member extraction; it never extracts archive paths onto the filesystem.
        download = runpy.run_path(str(Path(__file__).with_name('download-latest-mdbook.py')))
        url = f"https://github.com/{tool['repository']}/releases/download/{tool['version']}/{asset}"
        print(f'Downloading {name} {tool["version"]}: {asset}', file=sys.stderr)
        archive = download['request_bytes'](url)
        if hashlib.sha256(archive).hexdigest() != digest:
            raise RuntimeError(f'SHA-256 mismatch for {asset}')
        payload = download['extract_binary'](archive, 'zip' if asset.endswith('.zip') else 'tar.gz', executable)
        with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
            staged = Path(temporary) / executable
            staged.write_bytes(payload)
            if os.name != 'nt':
                staged.chmod(0o755)
            os.replace(staged, destination)
            Path(str(destination) + '.sha256').write_text(hashlib.sha256(payload).hexdigest() + '\n')
    return destination


def prepare(config_file: Path, *, enabled: bool, docker_mode: bool = False,
            cache: Path = DEFAULT_CACHE, allow_install: bool = True) -> dict[str, str]:
    if not enabled:
        return {}
    options = read_config(config_file).get('preprocessor', {}).get('d2', {})
    # External-file mode writes into maintained sources (also mounted read-only
    # by Docker). Managed setup uses upstream's default inline SVG mode instead.
    if options.get('inline', True) is not True:
        raise ValueError('Managed D2 requires inline = true; inline = false writes into book sources')
    if docker_mode:
        return {}  # The optional Docker image stage supplies both executables.
    preprocessor = shutil.which('mdbook-d2')
    if not preprocessor:
        preprocessor = str(install(cache, 'mdbook-d2', allow_install=allow_install))
    binary = options.get('path', 'd2')
    if not isinstance(binary, str) or not binary:
        raise ValueError('[preprocessor.d2].path must be a non-empty string')
    # mdBook starts preprocessors at the book root, including alternate configs.
    target = str(config_file.parent / binary) if '/' in binary or '\\' in binary else binary
    executable = shutil.which(target)
    if not executable:
        if binary != 'd2':
            raise RuntimeError(f'D2 executable not found: {binary!r}; fix [preprocessor.d2].path')
        executable = str(install(cache, 'd2', allow_install=allow_install))
    # Alternate configs run in a scratch root. Resolve relative executables before
    # staging so ../tools/d2 continues to refer to the maintained book root.
    return {'MDBOOK_PREPROCESSOR__D2__PATH': json.dumps(str(Path(executable).resolve())),
            'MDBOOK_PREPROCESSOR__D2__COMMAND': json.dumps(shlex.quote(Path(preprocessor).resolve().as_posix()))}
