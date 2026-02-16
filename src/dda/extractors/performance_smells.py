from __future__ import annotations

from pathlib import Path
from typing import Any, List

from dda.ingest.index import FileIndex


def extract_performance_smells(repo_dir: Path, index: FileIndex, evidence_dir: Path, snippets_dir: Path) -> dict[str, Any]:
    """
    Placeholder: real version will scan for obvious perf risks
    (unbounded buffers, missing timeouts, goroutine leaks, etc.).
    Keep minimal now to ship.
    """
    risks: List[dict[str, Any]] = []
    # Minimal output; your week-2 upgrade can add real detectors.
    return {"risks": risks}
