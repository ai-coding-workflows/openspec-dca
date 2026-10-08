"""Translate native resource paths without assuming a builder installation layout."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
from tempfile import mkdtemp

from book_paths import tomllib


def container_path(path: Path, project_root: Path, builder_dir: Path) -> str:
    path = path.resolve()
    if path.is_relative_to(builder_dir.resolve()):
        return (Path('/book-builder') / path.relative_to(builder_dir.resolve())).as_posix()
    if path.is_relative_to(project_root.resolve()):
        return (Path('/book') / path.relative_to(project_root.resolve())).as_posix()
    raise ValueError(f'Docker resource must be inside the project or builder: {path}')


def requires_asset_staging(config_file: Path, builder_dir: Path) -> bool:
    if tomllib is None:
        raise RuntimeError('Reading book.toml requires Python 3.11+ or tomli')
    config = tomllib.loads(config_file.read_text(encoding='utf-8'))
    scripts = config.get('output', {}).get('html', {}).get('additional-js', [])
    cache = (builder_dir / '.cache/scripts').resolve()
    return any((config_file.parent / value).resolve().is_relative_to(cache) for value in scripts)


def javascript_environment(config_file: Path, *, project_root: Path, builder_dir: Path,
                           docker_mode: bool = False, runtime: Path | None = None) -> dict[str, str]:
    """Resolve scripts from the maintained config, not an alternate staging root."""
    if tomllib is None:
        raise RuntimeError('Reading book.toml requires Python 3.11+ or tomli')
    config = tomllib.loads(config_file.read_text(encoding='utf-8'))
    scripts = config.get('output', {}).get('html', {}).get('additional-js')
    if scripts is None:
        return {}
    if not isinstance(scripts, list) or any(not isinstance(value, str) for value in scripts):
        raise ValueError('[output.html].additional-js must be an array of strings')
    paths = [(config_file.parent / value).resolve() for value in scripts]
    if runtime is not None:
        values = runtime_scripts(scripts, paths, runtime, builder_dir)
    else:
        values = [container_path(path, project_root, builder_dir) if docker_mode else str(path)
                  for path in paths]
    output = config['output']
    output['html']['additional-js'] = values
    # Backend fields use hyphens; nested environment spelling with underscores
    # creates different keys. Override the native output object explicitly.
    return {'MDBOOK_OUTPUT': json.dumps(output)}


def runtime_scripts(scripts, paths, runtime: Path, builder_dir: Path):
    """Give mdBook safe relative asset names, never absolute/traversing targets.

    Its additional-js copier uses script paths as destination names. Cached
    assets outside nested book roots therefore need a scratch-root alias.
    Author script declarations retain their existing interpretation.
    """
    cache = (builder_dir / '.cache/scripts').resolve()
    staging = None
    values = []
    for script, path in zip(scripts, paths):
        if path.is_relative_to(cache):
            if staging is None:
                staging = Path(mkdtemp(prefix='book-builder-assets-', dir=runtime))
            target = staging / path.name
            shutil.copyfile(path, target)
            values.append(target.relative_to(runtime).as_posix())
        else:
            values.append(script)
    return values


def capture_environment(environment: dict[str, str], renderer: str) -> dict[str, str]:
    # Nested HTML overrides would reintroduce a second renderer after MDBOOK_OUTPUT.
    result = {key: value for key, value in environment.items()
              if not key.startswith('MDBOOK_OUTPUT__')}
    result['MDBOOK_OUTPUT'] = renderer
    result['MDBOOK_BUILD__CREATE_MISSING'] = 'false'
    return result
