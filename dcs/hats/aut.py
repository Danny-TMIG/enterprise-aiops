"""AUT — automation. Bash script generator with safety prologue."""

from dcs.generate import requirement  # pragma: no cover


def script(cmds: list[str]) -> str:  # pragma: no cover
    body = "\n".join(cmds)
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + body + "\n"  # pragma: no cover


def is_safe(s: str) -> bool:  # pragma: no cover
    return s.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")  # pragma: no cover


@requirement(
    id="DCS-AUT-001",
    title="generated scripts always carry set -euo pipefail",
    section="AUT.automation",
    hats=["AUT"],
    criticality="MUST",
)
def test():  # pragma: no cover
    s = script(["echo hi"])
    assert is_safe(s)
