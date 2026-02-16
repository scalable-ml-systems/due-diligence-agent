from dda.scoring.score import score_repo
from dda.ingest.clone import RepoMeta
from dda.ingest.index import FileIndex


def test_basic_scoring_structure(tmp_path):
    repo_meta = RepoMeta(name="dummy", url="https://example.com", commit="abc123")

    index = FileIndex(root=tmp_path, files=[], languages=[])

    signals = {
        "ci": {},
        "infra": {},
        "observability": {},
        "security_deps": {},
        "structure": {},
    }

    scorecard = score_repo(
        repo_meta=repo_meta,
        run_id="test-run",
        focus=None,
        cfg=type("Cfg", (), {})(),  # minimal stub
        index=index,
        signals=signals,
        evidence_jsonl_path=tmp_path / "evidence.jsonl",
    )

    assert "categories" in scorecard
    assert len(scorecard["categories"]) >= 5
    assert "overall" in scorecard
