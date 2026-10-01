"""Mesh planes / families / states / routing dimensions.
Values are lifted verbatim from the DEV AGENT / SKILL ATLAS — naming agnostic.
"""

PLANES = [
    "intent", "knowledge", "capability", "skill", "agent", "model", "tool",
    "data", "execution", "runtime", "compute", "storage", "network",
    "security", "policy", "governance", "evidence", "qualification",
    "observability", "delivery", "operations", "interface", "moat",
]

SKILL_FAMILIES = [
    "intent", "context", "requirements", "search", "repository",
    "planning", "architecture", "modeling", "formal", "coding",
    "language", "paradigms", "algorithms", "data-structures",
    "api", "database", "data-engineering", "ai-ml", "tensor",
    "distributed", "concurrency", "os", "firmware", "hardware",
    "networking", "web", "mobile", "desktop", "cli", "build",
    "package", "source-control", "ci", "cd", "containers",
    "orchestration", "iac", "cloud", "edge", "identity",
    "cryptography", "appsec", "security-testing", "threat",
    "zero-trust", "sandbox", "testing", "performance",
    "reliability", "observability", "debugging", "compatibility",
    "migration", "configuration", "secrets", "policy", "standards",
    "governance", "evidence", "provenance", "qualification",
    "artifact", "documentation", "knowledge", "memory", "tooling",
    "capability-mgmt", "skill-mgmt", "agent-mgmt", "multi-agent",
    "model-mgmt", "execution", "runtime-control", "environment",
    "resource", "cost", "scheduling", "messaging", "integration",
    "interoperability", "file-format", "serialization", "media",
    "spatial", "scientific", "statistics", "optimization",
    "simulation", "ui-ux", "accessibility", "localization",
    "quality", "lifecycle", "change-mgmt", "incident-mgmt",
    "ops-mgmt", "product", "project", "business", "legal",
    "privacy", "supply-chain", "audit", "recovery", "learning",
]

RESULT_STATES = [
    "PASS", "FAIL", "PARTIAL", "UNKNOWN", "NOT_RUN", "BLOCKED",
    "NOT_AUTHORIZED", "UNSUPPORTED", "INCOMPATIBLE",
    "INSUFFICIENT_DATA", "INSUFFICIENT_EVIDENCE", "TIMEOUT",
    "CANCELLED", "RESOURCE_EXHAUSTED", "POLICY_DENIED",
    "SECURITY_DENIED", "QUALIFICATION_DENIED", "DEPENDENCY_FAILURE",
    "ENVIRONMENT_FAILURE", "TOOL_FAILURE", "MODEL_FAILURE",
    "EXECUTION_FAILURE", "VERIFICATION_FAILURE", "EXPIRED", "DEPRECATED",
]

ROUTING_DIMENSIONS = [
    "intent", "capability", "skill", "operation", "domain", "target",
    "artifact-type", "input-type", "output-type", "language", "framework",
    "runtime", "os", "arch", "accelerator", "environment", "locality",
    "connectivity", "authority", "permission", "security-classification",
    "trust-level", "evidence-level", "qualification-level", "compatibility",
    "latency", "throughput", "cost", "energy", "memory", "storage",
    "network", "reliability", "determinism", "reversibility", "risk",
    "availability", "specialization", "historical-success", "current-load",
    "resource-fit",
]
