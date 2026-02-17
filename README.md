# DDA — Technical Due Diligence Agent (Evidence-First)

DDA analyzes a GitHub repository and produces an **evidence-backed** due diligence report:
architecture map, production readiness scorecard, risks, and quick wins.


## Architecture



## **Design principles**

- Evidence-first: every score must cite file-level evidence
- Deterministic scoring: repeatable rubric evaluation
- Verifier-gated: unsupported claims reduce confidence
- Artifact-driven: outputs are shareable CTO-grade reports

                    +----------------------+
                    |   GitHub Repo URL    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    Ingestion Layer   |
                    |  (clone + index)     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      Extractors      |
                    |----------------------|
                    | docs                |
                    | structure           |
                    | ci                 |
                    | infra              |
                    | observability      |
                    | security/deps      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Evidence Store     |
                    |   evidence.jsonl     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Rubric Engine      |
                    |   (scoring)          |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Evidence Gate      |
                    |   (verification)     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Report Renderer    |
                    |   (Jinja2)           |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        report.md        scorecard.json      graph.json


## Why
Most “repo analyzers” hallucinate. DDA enforces a strict rule:
> Every meaningful claim must cite evidence (file path + line range or snippet).

## Quickstart
```bash
dda analyze https://github.com/argoproj/argo-cd --out ./out/argo-cd
dda analyze https://github.com/open-telemetry/opentelemetry-collector --out ./out/otel-collector
dda analyze https://github.com/kubernetes-sigs/kind --out ./out/kind

## Outputs
- report.md
- scorecard.json (schema: templates/scorecard.schema.json)
- evidence/evidence.jsonl (+ snippets)
- graph.json

## Rubric
See docs/rubric.md.

## Design
Planner → Extractors → Scoring → Verifier (evidence gate) → Report builder

## License
Apache 2
