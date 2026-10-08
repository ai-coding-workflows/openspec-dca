"""Catalog-neutral ADR data and safe discovery (Python 3.10+).

Parsing preserves incomplete/duplicate metadata for callers to validate. It does
not establish decision authority, lifecycle validity, or reference existence.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import re


TITLE = re.compile(r"^#[ \t]+(ADR-[^\s:]+)[ \t]*:[ \t]*(\S[^\n]*?)[ \t]*(?:[ \t]+#+)?$", re.MULTILINE)
ADR_HEADING = re.compile(r"^#\s+ADR(?:\b|[-:])", re.MULTILINE | re.IGNORECASE)
NONRECORD_NAMES = {"readme", "index", "assessment", "assessments", "architectural-decisions",
                   "adr-index", "adr-assessment", "adr-assessments"}


@dataclass(frozen=True)
class AdrRecord:
    path: str
    text: str
    id: str | None
    title: str | None
    fields: tuple[tuple[str, tuple[str, ...]], ...]
    supersession_targets: tuple[str, ...]

    def field_values(self, name: str) -> tuple[str, ...]:
        """Return all occurrences, including empty values, case-insensitively."""
        return next((values for field, values in self.fields if field == name.lower()), ())

    def _single(self, name):
        values = self.field_values(name)
        return (values[0].strip() or None) if len(values) == 1 else None

    @property
    def status(self):
        return self._single("status")

    @property
    def date(self):
        return self._single("date")

    @property
    def scope(self):
        return self._single("scope")


def contained(root: Path, path: Path) -> Path:
    """Resolve a path, rejecting physical paths outside the project root."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes project: {path}")
    return resolved


def project_path(root: Path, name) -> Path:
    """Resolve an existing, nonempty project-relative file or directory."""
    if not isinstance(name, (str, os.PathLike)) or not str(name).strip() or Path(name).is_absolute():
        raise ValueError(f"Paths must be nonempty project-relative paths: {name!r}")
    path = contained(root, root / name)
    if not path.exists():
        raise ValueError(f"Missing path: {name}")
    if not (path.is_dir() or path.is_file()):
        raise ValueError(f"Not a file or directory: {name}")
    return path


def _markdown(text):
    """Match the checker's metadata view without modifying original text."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    result, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker[1]
        elif not line.startswith(("    ", "\t")):
            result.append(line)
    return "\n".join(result)


def _individual(path, text):
    if path.suffix.lower() != ".md" or path.stem.lower() in NONRECORD_NAMES:
        return False
    return path.name.lower().startswith("adr-") or bool(ADR_HEADING.search(text))


def _destination(value):
    value = value.strip()
    if value.startswith("<"):
        end = value.find(">")
        if end < 0:
            raise ValueError(f"Malformed Markdown link destination: {value}")
        return value[1:end]
    return value.split()[0] if value else ""


def _supersession_targets(path, text):
    # Keep raw destinations (including external URLs and fragments). Local path
    # resolution and existence checks belong to consumers, not the data reader.
    definitions = {" ".join(label.lower().split()): _destination(value)
                   for label, value in re.findall(r"^[ \t]{0,3}\[([^\]]+)\]:[ \t]*(.+)$", text, re.MULTILINE)}
    targets = []
    blocks = re.findall(r"^(?:Supersedes|Superseded by):[^\n]*(?:\n(?!\s*$|#|[\w ]+:)[^\n]+)*",
                        text, re.MULTILINE | re.IGNORECASE)
    for block in blocks:
        inline = re.compile(
            r"(?<!!)\[([^\]]+)\]\([ \t]*(<[^>]*>[^\n)]*|(?:[^()<>\n]|\([^()\n]*\))*)\)")
        targets.extend(_destination(match[2]) for match in inline.finditer(block))
        remainder = inline.sub("", block)
        for match in re.finditer(r"(?<!!)\[([^\]]+)\](?:\[([^\]]*)\])?", remainder):
            label = " ".join((match[2] or match[1]).lower().split())
            if label in definitions:
                targets.append(definitions[label])
            elif match[2] is not None:
                raise ValueError(f"Undefined supersession Markdown reference [{label}] in {path}")
    return tuple(targets)


def _source(path, snapshots):
    if path not in snapshots:
        original = path.read_bytes().decode("utf-8")
        snapshots[path] = (original, _markdown(original))
    return snapshots[path]


def _parse(path, root, original, text):
    title = TITLE.search(text)
    fields = tuple((field, tuple(re.findall(rf"^{field}:[ \t]*([^\n]*)$", text,
                                          flags=re.MULTILINE | re.IGNORECASE)))
                   for field in ("status", "date", "scope"))
    return AdrRecord(path.relative_to(root).as_posix(), original,
                     title[1] if title else None, title[2] if title else None,
                     fields, _supersession_targets(path, text))


def read_adr(path: Path, root: Path) -> AdrRecord:
    """Read a contained physical file, preserving UTF-8 text and line endings."""
    root = root.resolve()
    path = contained(root, path)
    if not path.is_file():
        raise ValueError(f"Missing file: {path}")
    return _parse(path, root, *_source(path, {}))


def _walk(root, start):
    """Include internal directory symlinks, but reject escapes and stop cycles."""
    visited = set()

    def failed(error):
        raise error

    for directory, dirs, files in os.walk(start, followlinks=True, onerror=failed):
        current = contained(root, Path(directory))
        if current in visited:
            dirs[:] = []
            continue
        visited.add(current)
        dirs.sort()
        for name in dirs:
            child = contained(root, Path(directory) / name)
            if not child.exists():
                raise ValueError(f"Missing path: {Path(directory) / name}")
        yield Path(directory), sorted(files)


def _directory_records(root, start, snapshots, *, default=False):
    for directory, names in _walk(root, start):
        if default and "architectural-decisions" not in directory.relative_to(start).parts:
            continue
        for name in names:
            if Path(name).suffix.lower() != ".md":
                continue
            path = contained(root, directory / name)
            if not path.is_file():
                raise ValueError(f"Missing file: {directory / name}")
            if default and path.is_relative_to(root / "openspec/changes"):
                continue
            _, text = _source(path, snapshots)
            if _individual(directory / name, text):
                yield path


def decisions(root: Path, *, decision_paths=(), references=()) -> list[AdrRecord]:
    """Select ADRs, independently of any catalog implementation.

    Explicit files/directories replace default maintained-directory discovery.
    References always add existing individual Markdown files; indexes are valid
    references but not records. Selection uses aliases before resolving symlinks.
    """
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Missing project directory: {root}")
    if isinstance(decision_paths, (str, os.PathLike)) or isinstance(references, (str, os.PathLike)):
        raise ValueError("decision_paths and references must be sequences, not a single string/path")
    decision_paths, references = tuple(decision_paths), tuple(references)
    candidates, snapshots = set(), {}
    for name in references:
        path = project_path(root, name)
        if not path.is_file():
            raise ValueError(f"Not a file: {name}")
        if path.suffix.lower() == ".md" and _individual(Path(name), _source(path, snapshots)[1]):
            candidates.add(path)
    if not decision_paths:
        for name in ("openspec/specs", "openspec/system-architecture"):
            start = root / name
            if start.exists() or start.is_symlink():
                start = project_path(root, name)
                if not start.is_dir():
                    raise ValueError(f"Expected directory: {name}")
                candidates.update(_directory_records(root, start, snapshots, default=True))
    for name in decision_paths:
        path = project_path(root, name)
        if path.is_dir():
            candidates.update(_directory_records(root, path, snapshots))
        else:
            if not _individual(Path(name), _source(path, snapshots)[1]):
                raise ValueError(f"Explicit decision file is not an individual ADR: {name}")
            candidates.add(path)
    return [_parse(path, root, *snapshots[path])
            for path in sorted(candidates, key=lambda path: path.relative_to(root).as_posix())]
