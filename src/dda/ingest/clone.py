from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoMeta:
    name: str
    url: str
    commit: str


def clone_repo(repo_url: str, dest: Path) -> RepoMeta:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        # allow rerun
        subprocess.check_call(["rm", "-rf", str(dest)])

    # shallow clone for speed
    subprocess.check_call(["git", "clone", "--depth", "1", repo_url, str(dest)])

    commit = (
        subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"])
        .decode("utf-8")
        .strip()
    )
    name = repo_url.rstrip("/").split("/")[-1]
    return RepoMeta(name=name, url=repo_url, commit=commit)
