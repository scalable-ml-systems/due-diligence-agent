from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl, make_file_lines_ref


def extract_security_deps(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    evidence_path = evidence_dir / "evidence.jsonl"
    files = {e.path for e in index.files}

    deps = []
    for f in ["go.mod", "go.sum", "package-lock.json", "pnpm-lock.yaml", "poetry.lock", "requirements.txt"]:
        if f in files:
            deps.append(f)
    scanners = [p for p in files if "dependabot" in p.lower() or "codeql" in p.lower() or "snyk" in p.lower()]

    if deps:
        write_evidence_jsonl(evidence_path, {"id": "EVID-SEC-DEPS", "kind": "security", "summary": f"Dependency manifests present: {', '.join(deps)}", "refs": [{"type": "file_lines", "ref": make_file_lines_ref(deps[0], 1, 80)}]})
    if scanners:
        write_evidence_jsonl(evidence_path, {"id": "EVID-SEC-SCANNERS", "kind": "security", "summary": "Security scanning config detected", "refs": [{"type": "file_lines", "ref": make_file_lines_ref(sorted(scanners)[0], 1, 200)}]})

    return {"deps": deps, "scanners": scanners}
