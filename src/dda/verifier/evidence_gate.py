from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def evidence_gate(
    scorecard: dict[str, Any],
    evidence_jsonl_path: Path,
    require_evidence: bool,
    min_conf_if_missing: float,
) -> dict[str, Any]:
    """
    Ensures referenced evidence IDs exist in evidence.jsonl.
    If missing, marks category as lower confidence; and overall confidence lowered.
    """
    if not require_evidence:
        return scorecard

    present_ids = set()
    if evidence_jsonl_path.exists():
        for line in evidence_jsonl_path.read_text().splitlines():
            try:
                obj = json.loads(line)
                if "id" in obj:
                    present_ids.add(obj["id"])
            except Exception:
                continue

    # walk categories
    for cat in scorecard.get("categories", []):
        ev = cat.get("evidence", [])
        missing = []
        for e in ev:
            # We use "snippet" ref to point to evidence-id in v1 (simple)
            ref = e.get("ref")
            if ref and ref not in present_ids:
                missing.append(ref)

        if missing:
            cat["notes"] = (cat.get("notes", "") + f" | Unverified refs: {missing}").strip()
            cat["confidence"] = round(max(min_conf_if_missing, float(cat.get("confidence", 0.0)) * 0.6), 2)

    # recompute overall confidence
    cats = scorecard.get("categories", [])
    if cats:
        scorecard["overall"]["confidence"] = round(sum(float(c.get("confidence", 0.0)) for c in cats) / len(cats), 2)

    return scorecard
