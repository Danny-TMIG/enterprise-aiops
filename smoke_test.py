#!/usr/bin/env python3
import json, sys, urllib.request, urllib.error, pathlib

BASE = "http://127.0.0.1:8000"
ROOT = pathlib.Path(__file__).resolve().parent

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as r:
            return r.status, r.read().decode()
    except Exception as e:
        return None, str(e)

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 50)
    print("  Nexus Omega & Enterprise AIOps Smoke Test Suite")
    print("=" * 50)
    ok = True

    print("[*] Testing /health endpoint...")
    s, b = get("/health")
    if s == 200:
        print("    [OK] health 200")
    else:
        print(f"    [FAIL] health: {s} {b}")
        ok = False

    print("[*] Testing /v1/models ...")
    s, b = get("/v1/models")
    if s == 200:
        print("    [OK] models 200")
    else:
        print(f"    [FAIL] models: {s} {b}")
        ok = False

    print("[*] Testing /v1/chat/completions ...")
    s, b = post("/v1/chat/completions", {"messages": [{"role": "user", "content": "ping"}]})
    if s == 200:
        print("    [OK] chat 200")
    else:
        print(f"    [FAIL] chat: {s} {b}")
        ok = False

    print("[*] Testing /persona/synthesize ...")
    s, b = post("/persona/synthesize", {"profile_id": "omega_prime", "archetype": "sovereign_governor"})
    if s == 200:
        print("    [OK] persona 200")
    else:
        print(f"    [FAIL] persona: {s} {b}")
        ok = False

    proof = ROOT / "vatican" / "proof" / "OMEGA_SIGNOFF.md"
    print(f"[*] Verifying cryptographic proof artifact at '{proof}'...")
    if proof.exists():
        print(f"    [OK] Proof artifact verified present ({proof.stat().st_size} bytes)")
    else:
        print(f"    [FAIL] missing proof artifact")
        ok = False

    print("-" * 50)
    if ok:
        print("[SUCCESS] All checks passed.")
        return 0
    print("[FAILURE] One or more checks failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
