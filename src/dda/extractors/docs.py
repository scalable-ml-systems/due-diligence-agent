from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl, make_file_lines_ref


def extract_docs(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    """
    Minimal doc extraction:
    - Find README + SECURITY + CONTRIBUTING
    - Emit a couple of placeholder findings/quick wins/roadmap entries
    """
    evidence_path = evidence_dir / "evidence.jsonl"
    files = {e.path for e in index.files}

    findings_top = []
    quick_wins = []
    roadmap = []

    def add_doc_evidence(eid: str, rel: str, summary: str):
        write_evidence_jsonl(
            evidence_path,
            {
                "id": eid,
                "kind": "doc",
                "summary": summary,
                "refs": [{"type": "file_lines", "ref": make_file_lines_ref(rel, 1, 120)}],
            },
        )

    if "README.md" in files:
        add_doc_evidence("EVID-DOC-README", "README.md", "Project overview present in README")
        findings_top.append(
            {
                "title": "Clear project overview documentation",
                "severity": "low",
                "confidence": 0.75,
                "what": "README provides project overview and usage entry points.",
                "why": "Good docs reduce adoption friction and operational mistakes.",
                "evidence_list": ["EVID-DOC-README"],
                "recommendation": "Keep adding architecture diagrams and operational notes as the surface grows.",
                "unverified": False,
            }
        )
    else:
        findings_top.append(
            {
                "title": "Missing README overview",
                "severity": "medium",
                "confidence": 0.6,
                "what": "No README.md found in scanned set.",
                "why": "Operators and contributors lack a canonical entry point.",
                "evidence_list": [],
                "recommendation": "Add README with architecture + runbook links.",
                "unverified": True,
            }
        )

    if "SECURITY.md" in files:
        add_doc_evidence("EVID-DOC-SECURITY", "SECURITY.md", "Security policy present")
    else:
        quick_wins.append(
            {
                "title": "Add SECURITY.md and vulnerability reporting guidance",
                "steps": "Add SECURITY.md with reporting process + supported versions + response expectations.",
                "evidence_list": [],
            }
        )

    roadmap.append(
        {
            "phase": "30 days",
            "outcome": "Publish a production-readiness guide",
            "work": "Document deployment, scaling, upgrades, and troubleshooting paths.",
            "exit_criteria": "Operators can deploy + upgrade with a known-good checklist.",
        }
    )

    return {
        "findings": {"top": findings_top[:7]},
        "quick_wins": quick_wins[:5],
        "roadmap": roadmap[:3],
    }
