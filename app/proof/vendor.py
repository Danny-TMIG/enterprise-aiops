"""Claim 2: nobody external has confirmed anything."""
from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path


def check_no_third_party_sig() -> tuple:
    """External confirmation means a key we did NOT generate signed
    something. A local Ed25519 public key is our own key material —
    not confirmation by anyone else."""
    our_keys = set()
    for name in ("dist/public_key.pem", "dist/key.pem"):
        f = Path(name)
        if f.exists():
            our_keys.add(f.resolve())
    ext = []
    for pattern in ("*.gpg", "*.asc"):
        for f in Path(".").rglob(pattern):
            if any(x in str(f) for x in
                   (".venv", "node_modules", "site-packages")):
                continue
            ext.append(str(f))
    # SBOM.sig is HMAC with a local key; not third party
    ok = not ext
    return ok, (f"external signatures: {ext or ['none']}; "
                f"local keys on disk: {sorted(str(k.name) for k in our_keys)}")


def check_apis_never_called() -> tuple:
    keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "DEEPSEEK_API_KEY",
            "MISTRAL_API_KEY", "CODACY_API_TOKEN",
            "MICROSOFT_VERIFY_ENDPOINT", "SALESFORCE_ORG_URL",
            "SERVICENOW_INSTANCE", "GOOGLE_CLOUD_PROJECT"]
    set_keys = [k for k in keys if os.environ.get(k)]
    return (not set_keys), f"set keys: {set_keys or 'none'}"


def check_vendor_substitutions() -> tuple:
    from app.proprietary.registry import ProprietaryRegistry
    reg = ProprietaryRegistry()
    rows = []
    for name, obj in reg.objects.items():
        rows.append((name, obj.has_local(), obj.has_tenant(), obj.env_key))
    ok = all(l and not t for _, l, t, _ in rows)
    return ok, "; ".join(f"{n}: local={l} tenant={t}" for n, l, t, _ in rows)


def check_reality_definition() -> tuple:
    from app.proprietary.base import ProprietaryObject
    src = inspect.getsource(ProprietaryObject.is_real)
    ok = "has_tenant" in src and "has_local" in src
    return ok, "is_real = has_tenant OR has_local"


AXES = [
    ("no_third_party_signature", check_no_third_party_sig),
    ("apis_never_called", check_apis_never_called),
    ("all_vendors_local_substitutes", check_vendor_substitutions),
    ("reality_defined_as_local_or_tenant", check_reality_definition),
]


def main() -> int:
    print("── claim 2: nobody external has confirmed anything ──")
    passed = 0
    for name, fn in AXES:
        try:
            ok, ev = fn()
        except Exception as e:
            ok, ev = False, f"{type(e).__name__}: {e}"
        passed += int(ok)
        print(f"  {'PASS' if ok else 'FAIL'}  {name:36s}  {ev}")
    print()
    print(f"  verdict: {passed}/{len(AXES)} axes confirm no external confirmation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
