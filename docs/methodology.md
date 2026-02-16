# Methodology (v1)

## Goal
Produce a CTO-grade, evidence-backed assessment of production readiness.

## Non-goals
- No claims about runtime behavior unless supported by tests/benchmarks/docs.
- No “best practices” preaching; only actionable gaps with evidence.

## How findings are produced
1) Ingest repo and build file index.
2) Extract signals:
   - docs/architecture, README claims
   - CI workflows and quality gates
   - infra/deploy assets (Helm/Kustomize/Terraform)
   - observability instrumentation patterns
   - security posture signals (SECURITY.md, deps, scanners)
3) Score each rubric category:
   - score 0–5
   - assign confidence 0–1
   - attach evidence refs
4) Verifier step:
   - any claim without evidence is marked **Unverified**
   - confidence is reduced
   - report language switches from “is” → “may”

## Severity levels
- High: could cause outage/data loss/security incident
- Medium: likely operational pain / scaling risk
- Low: polish / future-hardening
