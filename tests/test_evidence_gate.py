import json
from dda.verifier.evidence_gate import evidence_gate

def test_evidence_gate_downgrades_missing(tmp_path):
    (tmp_path / "evidence.jsonl").write_text(json.dumps({"id": "EVID-OK"}) + "\n")

    scorecard = {
        "categories": [{
            "id": "x", "name": "X", "score": 3, "confidence": 0.8,
            "notes": "", "evidence": [{"type": "evidence_id", "ref": "MISSING"}],
            "recommendations": []
        }],
        "overall": {"confidence": 0.8}
    }

    out = evidence_gate(scorecard, tmp_path / "evidence.jsonl", True, 0.3)
    assert out["categories"][0]["confidence"] < 0.8
