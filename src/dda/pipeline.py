from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Optional

from dda.ingest.clone import clone_repo
from dda.ingest.index import build_file_index
from dda.report.render import render_report
from dda.scoring.score import score_repo
from dda.utils.config import load_config
from dda.utils.hashing import short_hash
from dda.verifier.evidence_gate import evidence_gate

# Extractors (signals)
from dda.extractors.docs import extract_docs
from dda.extractors.structure import extract_structure
from dda.extractors.ci import extract_ci
from dda.extractors.infra import extract_infra
from dda.extractors.observability import extract_observability
from dda.extractors.security_deps import extract_security_deps
from dda.extractors.performance_smells import extract_performance_smells


def run_analysis(
    repo_url: str,
    run_dir: Path,
    focus: Optional[str],
    config_path: Path,
    keep_repo: bool,
) -> dict[str, Any]:
    cfg = load_config(config_path)

    def _present_evidence_ids(evidence_jsonl_path: Path) -> set[str]:
        ids: set[str] = set()
        if not evidence_jsonl_path.exists():
            return ids
        for line in evidence_jsonl_path.read_text().splitlines():
            try:
                obj = json.loads(line)
                if "id" in obj:
                    ids.add(obj["id"])
            except Exception:
                continue
        return ids

    # 1) clone
    work_dir = run_dir / "_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    repo_dir = work_dir / "repo"

    repo_meta = clone_repo(repo_url=repo_url, dest=repo_dir)
    # stable-ish run id if needed
    run_id = short_hash(f"{repo_url}:{repo_meta.commit}:{time.time()}")[:12]

    # 2) index files
    index = build_file_index(
        repo_dir=repo_dir,
        include_globs=cfg.analysis.include_globs,
        exclude_globs=cfg.analysis.exclude_globs,
        max_files=cfg.analysis.max_files_scanned,
        max_bytes=cfg.analysis.max_file_bytes,
    )

    # create output dirs
    evidence_dir = run_dir / "evidence"
    snippets_dir = evidence_dir / "snippets"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    snippets_dir.mkdir(parents=True, exist_ok=True)

    # 3) extract signals (tool executors)
    signals: dict[str, Any] = {}
    signals["docs"] = extract_docs(repo_dir, index, evidence_dir, snippets_dir)
    signals["structure"] = extract_structure(repo_dir, index, evidence_dir, snippets_dir)
    signals["ci"] = extract_ci(repo_dir, index, evidence_dir, snippets_dir)
    signals["infra"] = extract_infra(repo_dir, index, evidence_dir, snippets_dir)
    signals["observability"] = extract_observability(repo_dir, index, evidence_dir, snippets_dir)
    signals["security_deps"] = extract_security_deps(repo_dir, index, evidence_dir, snippets_dir)
    signals["performance_smells"] = extract_performance_smells(repo_dir, index, evidence_dir, snippets_dir)

    present_ids = _present_evidence_ids(evidence_dir / "evidence.jsonl")

    # 4) scoring (rubric engine)
    scorecard = score_repo(
        repo_meta=repo_meta,
        run_id=run_id,
        focus=focus,
        cfg=cfg,
        index=index,
        signals=signals,
        evidence_jsonl_path=evidence_dir / "evidence.jsonl",
        present_evidence_ids=present_ids,

    )

    # 5) verifier (evidence gate)
    scorecard = evidence_gate(
        scorecard=scorecard,
        evidence_jsonl_path=evidence_dir / "evidence.jsonl",
        require_evidence=cfg.evidence.require_for_claims,
        min_conf_if_missing=cfg.evidence.min_confidence_if_no_evidence,
    )

    # 6) graph + summary (minimal placeholders)
    graph = signals.get("structure", {}).get("graph", {"nodes": [], "edges": []})
    summary = {
        "repo": {"name": repo_meta.name, "url": repo_meta.url, "commit": repo_meta.commit},
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "focus": focus,
    }

    # 7) render report
    render_report(
        template_path=Path(cfg.report.template),
        out_path=run_dir / "report.md",
        context={
            "repo": {
                "name": repo_meta.name,
                "url": repo_meta.url,
                "commit": repo_meta.commit,
                "languages": ", ".join(index.languages) if index.languages else "unknown",
                "ci_summary": signals.get("ci", {}).get("summary", "unknown"),
                "deploy_summary": signals.get("infra", {}).get("summary", "unknown"),
                "observability_summary": signals.get("observability", {}).get("summary", "unknown"),
            },
            "run": {"id": run_id, "timestamp": summary["generated_at"]},
            "summary": {"executive": scorecard.get("overall", {}).get("rationale", "")},
            "scorecard": scorecard,
            "architecture": signals.get("structure", {}).get("architecture", {"components": [], "flows": []}),
            "findings": signals.get("docs", {}).get("findings", {"top": []}),
            "risks": signals.get("performance_smells", {}).get("risks", []),
            "quick_wins": signals.get("docs", {}).get("quick_wins", []),
            "roadmap": signals.get("docs", {}).get("roadmap", []),
        },
    )

    # write other artifacts
    (run_dir / "scorecard.json").write_text(json.dumps(scorecard, indent=2))
    (run_dir / "graph.json").write_text(json.dumps(graph, indent=2))
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    # cleanup
    if not keep_repo:
        shutil.rmtree(work_dir, ignore_errors=True)

    return {"scorecard": scorecard, "summary": summary}
