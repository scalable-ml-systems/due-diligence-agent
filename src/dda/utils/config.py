from __future__ import annotations

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel


class AnalysisCfg(BaseModel):
    max_files_scanned: int = 2500
    max_file_bytes: int = 750_000
    include_globs: List[str]
    exclude_globs: List[str]


class EvidenceCfg(BaseModel):
    require_for_claims: bool = True
    min_confidence_if_no_evidence: float = 0.35
    snippet_max_chars: int = 1800


class ReportCfg(BaseModel):
    template: str
    include_top_findings: int = 7
    include_quick_wins: int = 5
    include_risks: int = 7


class RootCfg(BaseModel):
    version: int = 1
    analysis: AnalysisCfg
    evidence: EvidenceCfg
    report: ReportCfg


def load_config(path: Path) -> RootCfg:
    data = yaml.safe_load(path.read_text())
    return RootCfg(**data)
