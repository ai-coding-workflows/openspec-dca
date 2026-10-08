"""Decide which standard preprocessors the builder may manage."""
from dataclasses import dataclass
from pathlib import Path

from book_paths import tomllib


def read_config(config_file: Path) -> dict:
    if tomllib is None:
        raise RuntimeError('Reading book.toml requires Python 3.11+ or tomli')
    return tomllib.loads(config_file.read_bytes().decode('utf-8'))


def managed_feature(config: dict, name: str, requested: bool | None) -> bool:
    preprocessors = config.get('preprocessor', {})
    if not isinstance(preprocessors, dict):
        raise ValueError('[preprocessor] must be a table')
    options = preprocessors.get(name)
    if options is not None and not isinstance(options, dict):
        raise ValueError(f'[preprocessor.{name}] must be a table')
    if options is not None and options.get('command', f'mdbook-{name}') != f'mdbook-{name}':
        return False  # Custom commands remain author-managed even with an explicit true flag.
    return options is not None if requested is None else requested


@dataclass(frozen=True)
class FeaturePolicy:
    mermaid: bool
    svgbob: bool


def feature_policy(config_file: Path, *, mermaid: bool | None = None,
                   svgbob: bool | None = None) -> FeaturePolicy:
    """False flags stop provisioning; they never remove author configuration."""
    config = read_config(config_file)
    return FeaturePolicy(managed_feature(config, 'mermaid', mermaid),
                         managed_feature(config, 'svgbob', svgbob))
