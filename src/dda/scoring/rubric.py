from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RubricCategory:
    id: str
    name: str
    description: str


RUBRIC: List[RubricCategory] = [
    RubricCategory("arch_clarity", "Architecture Clarity",
                   "Module boundaries, ownership, architectural documentation."),
    RubricCategory("ops_readiness", "Operational Readiness",
                   "Health checks, runbooks, release discipline."),
    RubricCategory("observability", "Observability",
                   "Metrics, logs, tracing, dashboards."),
    RubricCategory("reliability", "Reliability & Correctness",
                   "Retries, idempotency, backpressure, timeouts."),
    RubricCategory("security", "Security Posture",
                   "Dependency hygiene, secrets management, scanning."),
    RubricCategory("data_contracts", "Data Contracts & Migrations",
                   "Schema versioning and migration discipline."),
    RubricCategory("testing", "Testing Discipline",
                   "Unit/integration tests and CI enforcement."),
    RubricCategory("performance", "Performance Risks",
                   "Hot paths, batching, resource limits."),
    RubricCategory("deployment", "Deployment Maturity",
                   "IaC, Helm/Kustomize, environment separation."),
    RubricCategory("cost", "Cost Risk",
                   "Resource sizing, scaling knobs, expensive defaults.")
]
