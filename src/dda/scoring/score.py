from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from dda.ingest.clone import RepoMeta
from dda.ingest.index import FileIndex

from dda.scoring.rubric import RUBRIC

CATEGORY_IDS = {c.id: c.name for c in RUBRIC}

def score_repo(
    repo_meta: RepoMeta,
    run_id: str,
    focus: Optional[str],
    cfg: Any,
    index: FileIndex,
    signals: dict[str, Any],
    evidence_jsonl_path: Path,
) -> dict[str, Any]:
    """
    v1 scoring: heuristic + evidence refs from extractors.
    Keep deterministic and conservative.
    """
    # crude signals
    has_ci = bool(signals.get("ci", {}).get("workflows"))
    infra_summary = signals.get("infra", {}).get("summary", "")
    obs_summary = signals.get("observability", {}).get("summary", "")
    deps = signals.get("security_deps", {}).get("deps", [])

    def clamp(x: float) -> float:
        return max(0.0, min(5.0, x))

    categories = []

    # Architecture clarity: based on whether structure components exist + README
    arch = 3.0 + (0.5 if signals.get("structure", {}).get("architecture", {}).get("components") else -0.5)
    if "README.md" in {e.path for e in index.files}:
        arch += 0.5
    categories.append(_cat("arch_clarity", clamp(arch), 0.7, "Inferred from structure + docs", ["EVID-DOC-README"]))

    # Ops readiness: presence of deploy assets
    ops = 3.0 + (1.0 if ("Helm" in infra_summary or "Kustomize" in infra_summary) else 0.0)
    categories.append(_cat("ops_readiness", clamp(ops), 0.65, "Inferred from deploy assets", ["EVID-INFRA-HELM", "EVID-INFRA-KUSTOMIZE"]))

    # Observability: heuristic
    obs = 2.5
    if "OpenTelemetry" in obs_summary:
        obs += 1.5
    if "Prometheus" in obs_summary:
        obs += 1.0
    categories.append(_cat("observability", clamp(obs), 0.6, "Heuristic from repo artifacts", ["EVID-OBS-OTEL", "EVID-OBS-PROM", "EVID-OBS-GRAF"]))

    # Reliability: placeholder (week-2 add real detectors)
    rel = 3.0
    categories.append(_cat("reliability", clamp(rel), 0.45, "Not deeply analyzed in v1 (upgrade later)", []))

    # Security posture: dep manifests + scanning config
    sec = 2.5 + (0.5 if deps else 0.0) + (0.5 if signals.get("security_deps", {}).get("scanners") else 0.0)
    categories.append(_cat("security", clamp(sec), 0.55, "Dependency hygiene + scanner hints", ["EVID-SEC-DEPS", "EVID-SEC-SCANNERS"]))

    # Data contracts: placeholder
    data = 2.5
    categories.append(_cat("data_contracts", clamp(data), 0.4, "Not deeply analyzed in v1", []))

    # Testing discipline: CI present
    test = 3.0 + (1.0 if has_ci else -0.5)
    categories.append(_cat("testing", clamp(test), 0.65, "CI presence as proxy", ["EVID-CI-GHA-001"]))

    # Performance: placeholder
    perf = 2.5
    categories.append(_cat("performance", clamp(perf), 0.4, "Not deeply analyzed in v1", []))

    # Deployment maturity: IaC/deploy assets
    dep = 3.0 + (1.5 if infra_summary else 0.0)
    categories.append(_cat("deployment", clamp(dep), 0.6, "IaC/deploy artifacts detected", ["EVID-INFRA-TF", "EVID-INFRA-HELM", "EVID-INFRA-KUSTOMIZE"]))

    # Cost risk: conservative default
    cost = 3.0
    categories.append(_cat("cost", clamp(cost), 0.35, "Not deeply analyzed in v1", []))

    # overall
    avg = sum(c["score"] for c in categories) / len(categories)
    overall = {
        "score": round(avg, 2),
        "confidence": round(sum(c["confidence"] for c in categories) / len(categories), 2),
        "rationale": "Evidence-first v1 assessment. Some categories are placeholders until deeper detectors are added.",
        "evidence": _merge_evidence(categories),
    }

    return {
        "version": 1,
        "repo": {"url": repo_meta.url, "commit": repo_meta.commit, "name": repo_meta.name},
        "run": {"id": run_id, "timestamp": ""},
        "overall": overall,
        "categories": categories,
    }


def _cat(cid: str, score: float, conf: float, notes: str, evidence_ids: list[str]) -> dict[str, Any]:
    name = dict(CATEGORY_IDS)[cid]
    # store evidence as refs; verifier will check existence
    evidence = [{"type": "snippet", "ref": eid} for eid in evidence_ids if eid]
    return {"id": cid, "name": name, "score": round(score, 2), "confidence": round(conf, 2), "notes": notes, "evidence": evidence, "recommendations": []}


def _merge_evidence(categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for c in categories:
        for e in c.get("evidence", []):
            key = (e.get("type"), e.get("ref"))
            if key in seen:
                continue
            seen.add(key)
            out.append(e)
    return out
