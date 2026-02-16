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
    present_evidence_ids: set[str],
) -> dict[str, Any]:
    """
    v1 scoring: heuristic + evidence refs from extractors.
    Keep deterministic and conservative.

    Key rule:
    - Only attach evidence IDs that are actually present in evidence.jsonl
      to avoid "Unverified refs" for repos that simply lack those artifacts.
    """
    has_ci = bool(signals.get("ci", {}).get("workflows"))
    infra_summary = signals.get("infra", {}).get("summary", "")
    obs_summary = signals.get("observability", {}).get("summary", "")
    deps = signals.get("security_deps", {}).get("deps", [])

    fileset = {e.path for e in index.files}

    def clamp(x: float) -> float:
        return max(0.0, min(5.0, x))

    categories: list[dict[str, Any]] = []

    # Architecture clarity
    arch = 3.0 + (0.5 if signals.get("structure", {}).get("architecture", {}).get("components") else -0.5)
    if "README.md" in fileset:
        arch += 0.5
    categories.append(
        _cat(
            "arch_clarity",
            clamp(arch),
            0.7,
            "Inferred from structure + docs",
            ["EVID-DOC-README", "EVID-STRUCT-TOPLEVEL"],
            present_evidence_ids,
        )
    )

    # Ops readiness
    has_deploy_assets = ("Helm" in infra_summary) or ("Kustomize" in infra_summary) or ("Terraform" in infra_summary)
    ops = 3.0 + (1.5 if has_deploy_assets else 0.0)
    categories.append(
        _cat(
            "ops_readiness",
            clamp(ops),
            0.65 if has_deploy_assets else 0.55,
            "IaC/deploy artifacts detected" if has_deploy_assets else "No IaC/deploy assets detected (scanned set)",
            ["EVID-INFRA-HELM", "EVID-INFRA-KUSTOMIZE", "EVID-INFRA-TF"],
            present_evidence_ids,
        )
    )

    # Observability
    obs = 2.5
    if "OpenTelemetry" in obs_summary:
        obs += 1.5
    if "Prometheus" in obs_summary:
        obs += 1.0
    if "Grafana" in obs_summary:
        obs += 0.5
    categories.append(
        _cat(
            "observability",
            clamp(obs),
            0.6 if ("OpenTelemetry" in obs_summary or "Prometheus" in obs_summary) else 0.5,
            "Heuristic from repo artifacts",
            ["EVID-OBS-OTEL", "EVID-OBS-PROM", "EVID-OBS-GRAF"],
            present_evidence_ids,
        )
    )

    # Reliability (placeholder)
    rel = 3.0
    categories.append(
        _cat(
            "reliability",
            clamp(rel),
            0.45,
            "v1: heuristic-only (deep detectors next)",
            [],
            present_evidence_ids,
        )
    )

    # Security posture
    sec = 2.5 + (0.5 if deps else 0.0) + (0.5 if signals.get("security_deps", {}).get("scanners") else 0.0)
    categories.append(
        _cat(
            "security",
            clamp(sec),
            0.55 if deps else 0.45,
            "Dependency hygiene + scanner hints",
            ["EVID-SEC-DEPS", "EVID-SEC-SCANNERS"],
            present_evidence_ids,
        )
    )

    # Data contracts (placeholder)
    data = 2.5
    categories.append(
        _cat(
            "data_contracts",
            clamp(data),
            0.4,
            "v1: not deeply analyzed yet",
            [],
            present_evidence_ids,
        )
    )

    # Testing discipline
    test = 3.0 + (1.0 if has_ci else -0.5)
    categories.append(
        _cat(
            "testing",
            clamp(test),
            0.65 if has_ci else 0.45,
            "CI presence as proxy",
            ["EVID-CI-GHA-001"],
            present_evidence_ids,
        )
    )

    # Performance (placeholder)
    perf = 2.5
    categories.append(
        _cat(
            "performance",
            clamp(perf),
            0.4,
            "v1: not deeply analyzed yet",
            [],
            present_evidence_ids,
        )
    )

    # Deployment maturity
    dep = 3.0 + (1.5 if infra_summary else 0.0)
    categories.append(
        _cat(
            "deployment",
            clamp(dep),
            0.6 if infra_summary else 0.45,
            "IaC/deploy artifacts detected" if infra_summary else "No IaC/deploy artifacts detected (scanned set)",
            ["EVID-INFRA-TF", "EVID-INFRA-HELM", "EVID-INFRA-KUSTOMIZE"],
            present_evidence_ids,
        )
    )

    # Cost risk (placeholder)
    cost = 3.0
    categories.append(
        _cat(
            "cost",
            clamp(cost),
            0.35,
            "v1: not deeply analyzed yet",
            [],
            present_evidence_ids,
        )
    )

    avg = sum(c["score"] for c in categories) / len(categories)
    overall = {
        "score": round(avg, 2),
        "confidence": round(sum(float(c["confidence"]) for c in categories) / len(categories), 2),
        "rationale": (
            "Evidence-first v1: focuses on repo structure, docs, CI, dependency signals, and deploy artifacts. "
            "Deep reliability/performance detectors are next."
        ),
        "evidence": _merge_evidence(categories),
    }

    return {
        "version": 1,
        "repo": {"url": repo_meta.url, "commit": repo_meta.commit, "name": repo_meta.name},
        "run": {"id": run_id, "timestamp": ""},
        "overall": overall,
        "categories": categories,
    }


def _cat(
    cid: str,
    score: float,
    conf: float,
    notes: str,
    evidence_ids: list[str],
    present: set[str],
) -> dict[str, Any]:
    name = CATEGORY_IDS[cid]
    # Only attach evidence that actually exists for this run
    evidence = [{"type": "evidence_id", "ref": eid} for eid in evidence_ids if eid in present]
    return {
        "id": cid,
        "name": name,
        "score": round(score, 2),
        "confidence": round(conf, 2),
        "notes": notes,
        "evidence": evidence,
        "recommendations": [],
    }


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
