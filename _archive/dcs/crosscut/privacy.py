"""Privacy: PII redaction by pattern."""

import re  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover

PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


def redact(text: str) -> tuple[str, int]:  # pragma: no cover
    n = 0
    for name, pat in PATTERNS.items():
        text, k = pat.subn(f"<{name.upper()}>", text)
        n += k
    return text, n  # pragma: no cover


@requirement(
    id="DCS-XC-PRIV-001",
    title="redactor strips email/phone/SSN",
    section="X.privacy",
    hats=["SD", "CMP2", "BE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    cleaned, n = redact("a@b.com 555-121-9999 123-45-6789")
    assert n == 3 and "@" not in cleaned and "555" not in cleaned
