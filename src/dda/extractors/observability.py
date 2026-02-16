from __future__ import annotations

from pathlib import Path
from typing import Any

from dda.ingest.index import FileIndex
from dda.extractors._common import write_evidence_jsonl


def extract_observability(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    evidence_path = evidence_dir / "evidence.jsonl"
    files = {e.path for e in index.files}

    # simple heuristics
    prom = [p for p in files if "prometheus" in p.lower()]
    graf = [p for p in files if "grafana" in p.lower() or p.lower().endswith(".json")]
    otel = [p for p in files if "otel" in p.lower() or "opentelemetry" in p.lower()]

    summary = []
    if prom:
        write_evidence_jsonl(evidence_path, {"id": "EVID-OBS-PROM", "kind": "observability", "summary": "Prometheus-related artifacts detected", "refs": [{"type": "file_lines", "ref": f"{prom[0]}:L1-L80"}]})
        summary.append("Prometheus")
    if graf:
        write_evidence_jsonl(evidence_path, {"id": "EVID-OBS-GRAF", "kind": "observability", "summary": "Grafana/dashboard artifacts detected", "refs": [{"type": "file_lines", "ref": f"{graf[0]}:L1-L80"}]})
        summary.append("Grafana/dashboards")
    if otel:
        write_evidence_jsonl(evidence_path, {"id": "EVID-OBS-OTEL", "kind": "observability", "summary": "OpenTelemetry-related artifacts detected", "refs": [{"type": "file_lines", "ref": f"{otel[0]}:L1-L80"}]})
        summary.append("OpenTelemetry")

    return {"summary": ", ".join(summary) if summary else "No explicit observability artifacts detected (heuristic)", "signals": {"prom": prom, "graf": graf, "otel": otel}}
