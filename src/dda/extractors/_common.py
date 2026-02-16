from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def write_evidence_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def make_file_lines_ref(file_path: str, start: int, end: int) -> str:
    return f"{file_path}:L{start}-L{end}"


def save_snippet(snippets_dir: Path, snippet_id: str, text: str) -> str:
    snippets_dir.mkdir(parents=True, exist_ok=True)
    out = snippets_dir / f"{snippet_id}.txt"
    out.write_text(text, encoding="utf-8")
    return out.as_posix()
