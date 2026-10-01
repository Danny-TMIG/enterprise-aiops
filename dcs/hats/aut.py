"""AUT — automation. Bash script generator with safety prologue."""

from dcs.generate import requirement


def script(cmds: list[str]) -> str:
    body = "\n".join(cmds)
    return "#!/usr/bin/env bash\nset -euo pipefail\n" + body + "\n"


def is_safe(s: str) -> bool:
    return s.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")


@requirement(
    id="DCS-AUT-001",
    title="generated scripts always carry set -euo pipefail",
    section="AUT.automation",
    hats=["AUT"],
    criticality="MUST",
)
def test():
    s = script(["echo hi"])
    assert is_safe(s)
