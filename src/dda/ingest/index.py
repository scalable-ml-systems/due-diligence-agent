from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set

from pathspec import PathSpec


@dataclass(frozen=True)
class FileEntry:
    path: str
    size: int


@dataclass
class FileIndex:
    root: Path
    files: List[FileEntry]
    languages: List[str]


def _detect_languages(paths: Iterable[str]) -> List[str]:
    exts: Set[str] = set()
    for p in paths:
        if "." in p:
            exts.add(p.rsplit(".", 1)[-1].lower())
    # very rough mapping; enough for report snapshot
    mapping = {
        "go": "Go",
        "py": "Python",
        "ts": "TypeScript",
        "js": "JavaScript",
        "rs": "Rust",
        "java": "Java",
        "tf": "Terraform",
        "yaml": "YAML",
        "yml": "YAML",
        "sql": "SQL",
    }
    langs = sorted({mapping[e] for e in exts if e in mapping})
    return langs[:6]


def build_file_index(
    repo_dir: Path,
    include_globs: List[str],
    exclude_globs: List[str],
    max_files: int,
    max_bytes: int,
) -> FileIndex:
    include = PathSpec.from_lines("gitwildmatch", include_globs)
    exclude = PathSpec.from_lines("gitwildmatch", exclude_globs)

    entries: List[FileEntry] = []
    for fp in repo_dir.rglob("*"):
        if not fp.is_file():
            continue
        rel = fp.relative_to(repo_dir).as_posix()
        if exclude.match_file(rel):
            continue
        if not include.match_file(rel):
            continue

        size = fp.stat().st_size
        if size > max_bytes:
            continue
        entries.append(FileEntry(path=rel, size=size))
        if len(entries) >= max_files:
            break

    langs = _detect_languages([e.path for e in entries])
    return FileIndex(root=repo_dir, files=entries, languages=langs)
