"""End-to-end slice: intent -> code -> train -> SBOM -> sign -> policy -> braid -> CD."""
from __future__ import annotations


def test_01_intent_to_code():
    from app.reconfig.codeal import from_tasks
    from app.reconfig.emit import emit_all
    from app.reconfig.interpreter import interpret
    from app.reconfig.rules import apply_rules
    ir = interpret("count the words in postgres and store the results")
    tasks, _ = apply_rules(ir)
    assert tasks, "no tasks from intent"
    prog = from_tasks("slice", tasks)
    out = emit_all(prog)
    assert "python" in out and "sql" in out and "mql" in out and "rl" in out
    assert "def run(env):" in out["python"]

def test_02_parallel_grid():
    from app.engines.parallel import run_grid
    _, tiles = run_grid({"sudoku": "easy", "crossword": "easy", "rubik": "easy"},
                        puzzles_per_tile=2, seed=0, max_workers=4)
    assert tiles
    assert any(t.rate == 1.0 for t in tiles)
    assert any(t.rate == 0.0 for t in tiles)

def test_03_cd_nand_all_levels():
    from app.cd_nand.compute import nand_cd, verify_all_levels
    r = verify_all_levels(6)
    assert r["ok"], r["failures"]
    for a in (False, True):
        for b in (False, True):
            assert nand_cd(a, b, 3) == (not (a and b))

def test_04_sbom():
    from pathlib import Path

    from app.supply.sbom import build_sbom, sbom_digest
    sbom = build_sbom("enterprise_aiops", "0.1.0", Path.cwd())
    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.5"
    assert sbom["serialNumber"].startswith("urn:uuid:")
    assert len(sbom["components"]) > 50
    for c in sbom["components"][:3]:
        assert c["hashes"][0]["alg"] == "SHA-256"
        assert len(c["hashes"][0]["content"]) == 64
    d = sbom_digest(sbom)
    assert d == sbom_digest(sbom)

def test_05_sign_and_verify():
    from app.supply.sign import generate_key, key_id, sign, verify
    key = generate_key()
    assert len(key) == 32
    payload = b"hello"
    sig = sign(payload, key)
    assert verify(payload, sig, key)
    assert not verify(payload + b" ", sig, key)
    assert not verify(payload, sig, generate_key())
    assert len(key_id(key)) == 16

def test_06_attestation():
    from pathlib import Path

    from app.supply.attest import build_attestation, verify_attestation
    from app.supply.sbom import build_sbom
    from app.supply.sign import generate_key
    sbom = build_sbom("enterprise_aiops", "0.1.0", Path.cwd())
    key = generate_key()
    att = build_attestation(sbom, key)
    assert att["_type"].startswith("https://in-toto.io/")
    assert att["predicateType"].startswith("https://slsa.dev/")
    assert att["subject"]
    assert verify_attestation(att, key)
    att["predicate"]["timestamp"] = "tampered"
    assert not verify_attestation(att, key)

def test_07_policy():
    from app.policy.parser import evaluate, parse_policy
    # rules are ordered: most specific first, catch-all last.
    # the engine is first-match-wins, so "escalate_medium" must
    # appear before "allow_low" to fire on severity==2 + known resource.
    src = (
        'rule "escalate_medium" when severity == 2 and resource in ["model","policy"] then escalate "review"\n'
        'rule "deny_high" when severity >= 3 then deny "too high"\n'
        'rule "allow_low" when severity < 3 then allow "ok"\n'
    )
    rules = parse_policy(src)
    assert len(rules) == 3
    assert evaluate(rules, {"severity": 5, "resource": "model"})["action"] == "deny"
    assert evaluate(rules, {"severity": 1, "resource": "model"})["action"] == "allow"
    assert evaluate(rules, {"severity": 2, "resource": "policy"})["action"] == "escalate"
    assert evaluate(rules, {"severity": 99})["action"] == "deny"

def test_08_policy_rejects_code():
    from app.policy.parser import parse_policy
    for bad in [
        'rule "x" when __import__("os").system("rm") then deny ""',
        'rule "x" when open("/etc/passwd").read() then deny ""',
        'rule "x" when (lambda: 1)() then deny ""',
    ]:
        try:
            parse_policy(bad)
        except ValueError:
            continue
        raise AssertionError(f"policy should have rejected: {bad}")

def test_09_braid():
    from app.braid.parser import compile_workflow, parse_workflow
    src = (
        'workflow demo {\n'
        '  source a = fetch("http://x")\n'
        '  source b = fetch("http://y")\n'
        '  braid c = a + b\n'
        '  transform d = c |> verify\n'
        '  emit d\n'
        '}\n'
    )
    wf = parse_workflow(src)
    assert wf.name == "demo"
    plan = compile_workflow(wf)
    assert plan["name"] == "demo"
    assert len(plan["tasks"]) == 5
    ops = [t["op"] for t in plan["tasks"]]
    assert ops == ["fetch","fetch","braid","transform","emit"]
    assert plan["tasks"][2]["inputs"] == ["a","b"]

def test_10_braid_rejects_undefined():
    from app.braid.parser import compile_workflow, parse_workflow
    src = (
        'workflow bad {\n'
        '  source a = fetch("http://x")\n'
        '  braid c = a + z\n'
        '  emit c\n'
        '}\n'
    )
    wf = parse_workflow(src)
    try:
        compile_workflow(wf)
    except ValueError:
        return
    raise AssertionError("should reject undefined ref")

def test_11_cli_round_trip():
    from app.cli import main
    assert main(["supply"]) == 0
    assert main(["cd"]) == 0
    assert main(["atlas"]) == 0
    assert main(["policy"]) == 0
    assert main(["braid"]) == 0

def test_12_atlas_grounded():
    from app.atlas.algorithms import ALGORITHMS
    from app.atlas.algorithms import validate as av
    from app.atlas.moats import all_moats
    from app.atlas.moats import validate as mv
    a = av(); assert a["ok"], a["invalid_residuals"]
    m = mv(); assert m["ok"], m["invalid_residuals"]
    assert len(ALGORITHMS) == 40
    assert len(all_moats()) == 11
    # the corpus reference must be the real module
    for moat in all_moats():
        for impl in moat.implementers:
            if "corpus" in impl:
                assert "app.delta.corpus" in impl or "app.delta" in impl
