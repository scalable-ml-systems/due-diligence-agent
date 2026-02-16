from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl


def extract_structure(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    evidence_path = evidence_dir / "evidence.jsonl"

    # very lightweight: infer "components" by top-level folders
    top = {}
    for e in index.files:
        parts = e.path.split("/")
        if len(parts) > 1:
            top[parts[0]] = top.get(parts[0], 0) + 1

    components = []
    for name, count in sorted(top.items(), key=lambda x: -x[1])[:12]:
        eid = f"EVID-STRUCT-{name.upper()[:16]}"
        write_evidence_jsonl(
            evidence_path,
            {
                "id": "EVID-STRUCT-TOPLEVEL",
                "kind": "code",
                "summary": "Top-level repository structure inferred from folder distribution",
                "refs": [{"type": "file_lines", "ref": f"{name}/:L1-L1"}],
            },
        )
        components.append({"name": name, "purpose": f"Inferred component boundary ({count} files scanned)", "evidence_ref": eid})

    # graph placeholder
    graph = {"nodes": [{"id": c["name"]} for c in components], "edges": []}

    return {
        "summary": "Repo structure indexed",
        "architecture": {"components": components, "flows": []},
        "graph": graph,
    }
