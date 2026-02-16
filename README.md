# DDA — Technical Due Diligence Agent (Evidence-First)

DDA analyzes a GitHub repository and produces an **evidence-backed** due diligence report:
architecture map, production readiness scorecard, risks, and quick wins.

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
MIT
