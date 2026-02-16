import json
from pathlib import Path

from dda.verifier.evidence_gate import evidence_gate


def test_evidence_gate_downgrades_missing_refs(tmp_path):
    evidence_path = tmp_path / "evidence.jsonl"
    evidence_path.write_text(
        json.dumps({"id": "EVID-1"}) + "\n"
    )

    scorecard = {
        "categories": [
            {
                "id": "arch_clarity",
                "name": "Architecture Clarity",
                "score": 4,
                "confidence": 0.8,
                "notes": "",
                "evidence": [{"type": "snippet", "ref": "MISSING-EVID"}],
            }
        ],
        "overall": {"confidence": 0.8}
    }

    updated = evidence_gate(
        scorecard,
        evidence_path,
        require_evidence=True,
        min_conf_if_missing=0.3,
    )

    assert updated["categories"][0]["confidence"] <= 0.8
