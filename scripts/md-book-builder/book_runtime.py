"""Stage alternate configurations without modifying maintained book sources."""

from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from book_paths import BookPaths
from book_selection import BOOK_CONFIG_NAME


@contextmanager
def staged_book(paths: BookPaths, docker_mode: bool = False, *, force: bool = False):
    """Yield an mdBook root, retaining any staging until the command exits.

    Relative links work both natively and through Docker's repository mount.
    The output ancestor is omitted: callers override mdBook's build directory
    with the original absolute output path instead of mirroring its cache.
    """
    if paths.config_file.name == BOOK_CONFIG_NAME and not force:
        yield paths.repository
        return

    # mdBook clears its destination during a build. Never put its runtime root
    # inside that destination, including a top-level build-dir such as "user-book".
    staging_parent = (paths.output_root if paths.output_root != paths.build_dir
                      else paths.build_dir.parent)
    staging_parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="mdbook-runtime-", dir=staging_parent) as temporary:
        runtime = Path(temporary)
        try:
            for entry in paths.repository.iterdir():
                if entry.name == BOOK_CONFIG_NAME or runtime.is_relative_to(entry):
                    continue
                (runtime / entry.name).symlink_to(
                    os.path.relpath(entry, runtime), target_is_directory=entry.is_dir()
                )
            (runtime / BOOK_CONFIG_NAME).symlink_to(os.path.relpath(paths.config_file, runtime))
        except (OSError, NotImplementedError) as exc:
            raise RuntimeError(
                "Alternate book configurations require symbolic links; "
                f"cannot stage {paths.config_file}: {exc}"
            ) from exc
        yield runtime
