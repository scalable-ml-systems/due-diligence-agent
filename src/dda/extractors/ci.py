from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl, make_file_lines_ref


def extract_ci(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    evidence_path = evidence_dir / "evidence.jsonl"
    files = {e.path for e in index.files}

    candidates = [p for p in files if p.startswith(".github/workflows/")]
    if not candidates:
        return {"summary": "No GitHub Actions workflows detected (in scanned set)", "workflows": []}

    # evidence for first workflow
    wf = sorted(candidates)[0]
    write_evidence_jsonl(
        evidence_path,
        {
            "id": "EVID-CI-GHA-001",
            "kind": "ci",
            "summary": f"GitHub Actions workflow present: {wf}",
            "refs": [{"type": "file_lines", "ref": make_file_lines_ref(wf, 1, 200)}],
        },
    )
    return {"summary": "GitHub Actions workflows detected", "workflows": sorted(candidates)}
