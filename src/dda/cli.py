from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from dda.pipeline import run_analysis
from dda.utils.text import slugify

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def analyze(
    repo_url: str = typer.Argument(..., help="GitHub repo URL, e.g. https://github.com/argoproj/argo-cd"),
    out: Path = typer.Option(Path("./out"), "--out", "-o", help="Output root directory"),
    focus: Optional[str] = typer.Option(None, "--focus", help="Optional focus area (infra|security|perf|obs|testing)"),
    config: Path = typer.Option(Path("templates/config.yaml"), "--config", help="Path to config.yaml"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Optional run id override"),
    keep_repo: bool = typer.Option(False, "--keep-repo", help="Do not delete cloned repo after run"),
):
    """
    Evidence-first due diligence analysis.
    Produces report.md + scorecard.json + evidence JSONL + graph.json.
    """
    repo_slug = slugify(repo_url.split("/")[-1])
    rid = run_id or f"{int(time.time())}"
    run_dir = out / repo_slug / rid
    run_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel.fit(f"[bold]DDA Analyze[/bold]\nRepo: {repo_url}\nRun: {rid}\nOut: {run_dir}"))

    result = run_analysis(
        repo_url=repo_url,
        run_dir=run_dir,
        focus=focus,
        config_path=config,
        keep_repo=keep_repo,
    )

    # brief summary to terminal
    console.print("\n[bold]Done.[/bold]")
    console.print(f"Report: {run_dir / 'report.md'}")
    console.print(f"Scorecard: {run_dir / 'scorecard.json'}")
    console.print(f"Evidence: {run_dir / 'evidence' / 'evidence.jsonl'}")

    # optional pretty summary
    console.print("\n[bold]Overall[/bold]")
    console.print(json.dumps(result["scorecard"]["overall"], indent=2))


@app.command()
def validate(
    scorecard_path: Path = typer.Argument(..., help="Path to scorecard.json"),
    evidence_path: Optional[Path] = typer.Option(None, "--evidence", help="Path to evidence.jsonl (optional)"),
):
    """
    Validates scorecard format and (optionally) evidence references are present.
    Lightweight sanity check, not full JSON Schema validation.
    """
    data = json.loads(scorecard_path.read_text())
    required = ["version", "repo", "run", "overall", "categories"]
    missing = [k for k in required if k not in data]
    if missing:
        raise typer.BadParameter(f"Missing keys: {missing}")

    if evidence_path and not evidence_path.exists():
        raise typer.BadParameter(f"Evidence file not found: {evidence_path}")

    console.print("[green]OK[/green]")


if __name__ == "__main__":
    app()
