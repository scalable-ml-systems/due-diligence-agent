# DDA Rubric (v1)

Scoring scale (0–5):
- 0: Missing / actively dangerous
- 1: Weak / ad-hoc / undocumented
- 2: Partial / inconsistent
- 3: Solid baseline (production-acceptable)
- 4: Strong (well-instrumented, disciplined)
- 5: Excellent (best-in-class)

Confidence (0.0–1.0):
- 0.2: mostly inferred
- 0.5: some evidence, incomplete
- 0.8: strong evidence in repo
- 0.95: explicit docs/tests/runbooks + code support

## Evidence rule (non-negotiable)
Every non-trivial claim must reference evidence:
- file path + line range (preferred), or
- snippet id (from evidence/snippets), or
- repo artifact (CI config, Helm chart, Terraform module)

If evidence is missing:
- mark finding as **Unverified**
- lower confidence
- do NOT present as a fact

---

## Categories

### 1) Architecture clarity
Signals:
- clear module boundaries
- ownership/areas (CODEOWNERS)
- docs describing components, control/data plane, interfaces

Evidence examples:
- `/docs/architecture/*.md`
- `CODEOWNERS`
- package/module layout

### 2) Operational readiness
Signals:
- health checks, readiness/liveness
- runbooks, ops docs
- release process & backout strategy
- well-defined config management

Evidence:
- `/docs/`, `/ops/`, `/runbook/`
- k8s manifests, helm charts
- release notes

### 3) Observability
Signals:
- structured logging
- metrics + dashboards
- tracing (OpenTelemetry)
- explicit SLO/SLA language (optional)

Evidence:
- instrumentation code paths
- dashboards (Grafana), Prom rules
- OTel pipelines/exporters

### 4) Reliability & correctness
Signals:
- retries with backoff + limits
- idempotency
- backpressure/queueing controls
- timeouts/circuit breakers

Evidence:
- retry libraries/config
- queue/buffer settings
- explicit timeout defaults

### 5) Security posture
Signals:
- secrets management guidance
- least privilege IAM/K8s RBAC
- dependency hygiene
- security docs, threat model (bonus)

Evidence:
- security policy docs
- RBAC manifests
- Dependabot / Snyk configs
- pinned deps / lockfiles

### 6) Data contracts & migrations
Signals:
- schema definitions
- versioning strategy
- migration tooling + discipline

Evidence:
- schema registry usage
- migrations folder
- protobuf/openapi specs

### 7) Testing discipline
Signals:
- unit/integration/e2e separation
- CI gates
- flaky test mitigation
- coverage reports (optional)

Evidence:
- CI workflow files
- test directories + naming conventions

### 8) Performance risks
Signals:
- obvious hot paths
- concurrency model clarity
- caching/batching where appropriate
- profiling guidance

Evidence:
- perf docs, benchmarks, pprof usage
- benchmark tests

### 9) Deployment maturity
Signals:
- IaC (Terraform)
- Helm/Kustomize
- environment separation
- GitOps compatibility

Evidence:
- `/deploy`, `/charts`, `/manifests`, `/infra`

### 10) Cost risks
Signals:
- knobs for scaling
- resource requests/limits
- data egress awareness
- expensive defaults avoided

Evidence:
- resource configs
- docs explaining sizing/capacity planning
