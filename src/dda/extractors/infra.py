from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl


def extract_infra(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    evidence_path = evidence_dir / "evidence.jsonl"
    files = {e.path for e in index.files}

    hits = {
        "terraform": [p for p in files if p.endswith(".tf")],
        "helm": [p for p in files if "/charts/" in p or p.endswith("Chart.yaml")],
        "kustomize": [p for p in files if p.endswith("kustomization.yaml") or p.endswith("kustomization.yml")],
        "k8s_manifests": [p for p in files if p.endswith(".yaml") or p.endswith(".yml")],
    }

    summary_parts = []
    if hits["terraform"]:
        write_evidence_jsonl(
            evidence_path,
            {"id": "EVID-INFRA-TF", "kind": "infra", "summary": "Terraform files present", "refs": [{"type": "file_lines", "ref": f"{hits['terraform'][0]}:L1-L80"}]},
        )
        summary_parts.append("Terraform")
    if hits["helm"]:
        write_evidence_jsonl(
            evidence_path,
            {"id": "EVID-INFRA-HELM", "kind": "infra", "summary": "Helm chart assets present", "refs": [{"type": "file_lines", "ref": f"{hits['helm'][0]}:L1-L80"}]},
        )
        summary_parts.append("Helm")
    if hits["kustomize"]:
        write_evidence_jsonl(
            evidence_path,
            {"id": "EVID-INFRA-KUSTOMIZE", "kind": "infra", "summary": "Kustomize manifests present", "refs": [{"type": "file_lines", "ref": f"{hits['kustomize'][0]}:L1-L80"}]},
        )
        summary_parts.append("Kustomize")

    return {"summary": ", ".join(summary_parts) if summary_parts else "No IaC/deploy assets detected (in scanned set)", "hits": hits}
