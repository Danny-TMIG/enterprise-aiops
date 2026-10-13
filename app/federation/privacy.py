import re
from typing import Any, ClassVar


class DifferentialPrivacyGovernance:
    PII_PATTERNS: ClassVar[tuple[re.Pattern, ...]] = (
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    )

    @classmethod
    def sanitize_payload(cls, data: dict[str, Any]) -> dict[str, Any]:
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, str):
                val = v
                for pattern in cls.PII_PATTERNS:
                    val = pattern.sub("[REDACTED_PRIVACY_MASK]", val)
                sanitized[k] = val
            elif isinstance(v, dict):
                sanitized[k] = cls.sanitize_payload(v)  # type: ignore[assignment]
            else:
                sanitized[k] = v
        return sanitized
