#!/usr/bin/env python3
"""Idempotent status report for the Aether repo."""
from __future__ import annotations
import argparse, datetime as _dt, json, subprocess, sys
from pathlib import Path

REPORT_FORMAT = "v1"

def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p.parent, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return p.parent.parent

ROOT = _repo_root()

def _run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 127, "", str(e)

def git_info():
    out = {}
    rc, h, _ = _run(["git","rev-parse","HEAD"]); out["head"] = h if rc==0 else None
    rc, b, _ = _run(["git","rev-parse","--abbrev-ref","HEAD"]); out["branch"] = b if rc==0 else None
    rc, r, _ = _run(["git","remote","get-url","origin"]); out["remote"] = r if rc==0 else None
    rc, s, _ = _run(["git","status","--porcelain"])
    out["dirty"] = bool(s); out["dirty_files"] = s.splitlines() if s else []
    rc, o, _ = _run(["git","rev-parse","origin/main"]); out["origin_main"] = o if rc==0 else None
    out["in_sync"] = out["head"] == out.get("origin_main")
    rc, l, _ = _run(["git","log","--oneline","-1"]); out["last_commit"] = l if rc==0 else None
    return out

def tree_info():
    req = {".github":"dir","catalog":"dir","components":"dir","contracts":"dir","deploy":"dir",
           "docs":"dir","examples":"dir","integration":"dir","libraries":"dir","tooling":"dir",
           "README.md":"file","pyproject.toml":"file","Makefile":"file","LICENSE":"file"}
    out = {"required":{}, "missing":[]}
    for n,k in req.items():
        p = ROOT/n; present = p.is_dir() if k=="dir" else p.is_file()
        out["required"][n]=present
        if not present: out["missing"].append(n)
    layers={}
    for L in ("ax","ag","ac"):
        d=ROOT/"components"/L
        layers[L]=len([x for x in d.iterdir() if x.is_dir()]) if d.is_dir() else 0
    out["components_per_layer"]=layers
    out["components_total"]=sum(layers.values())
    out["components_consistent"]=out["components_total"]==layers["ax"]+layers["ag"]+layers["ac"]
    for d in ("catalog/inventories","contracts/schemas","docs/architecture","docs/decisions"):
        out.setdefault("subdirs",{})[d]=(ROOT/d).is_dir()
    out["archive_present"]=(ROOT/"_archive").exists()
    return out

def tracked_info():
    rc, f, _ = _run(["git","ls-files"])
    if rc!=0: return {"tracked_files":0,"tracked_bytes":0,"size_ok":False}
    fl=f.splitlines(); tot=0; miss=0
    for x in fl:
        try: tot+=(ROOT/x).stat().st_size
        except OSError: miss+=1
    return {"tracked_files":len(fl),"tracked_bytes":tot,"tracked_missing":miss,"size_ok":miss==0}

def compute_verdict(d):
    rs=[]
    g,t,tr=d["git"],d["tree"],d["tracked"]
    if not g["in_sync"]: rs.append({"code":"R2","detail":f"head {g['head']} != origin/main {g['origin_main']}"})
    if g["dirty"]: rs.append({"code":"R3","detail":f"{len(g['dirty_files'])} change(s) in working tree"})
    if not t["components_consistent"]:
        pl=t["components_per_layer"]
        rs.append({"code":"R4","detail":f"total {t['components_total']} != ax+ag+ac {pl['ax']}+{pl['ag']}+{pl['ac']}"})
    if t["missing"]: rs.append({"code":"R5","detail":f"missing: {', '.join(t['missing'])}"})
    if t["archive_present"]: rs.append({"code":"R6","detail":"_archive/ present"})
    if tr.get("tracked_missing",0)>0: rs.append({"code":"R7","detail":f"{tr['tracked_missing']} tracked file(s) missing"})
    for gr in d.get("gates",[]):
        if not gr["pass"]: rs.append({"code":"R8","detail":f"gate '{gr['name']}' failed"})
    return {"status":"OK" if not rs else "ATTENTION","reasons":rs}

GATES=[("orchestrator",[sys.executable,"tooling/master_orchestrator.py"]),
       ("spec_audit",[sys.executable,"tooling/validation/spec_audit.py"]),
       ("platform_val",[sys.executable,"tooling/validation/platform_validate.py"]),
       ("profiles",[sys.executable,"tooling/validation/validate_profiles.py"]),
       ("federation",[sys.executable,"tooling/validation/check_federation_gate.py"]),
       ("tests",[sys.executable,"-m","pytest","tests/","-q"]),
       ("e2e",[sys.executable,"integration/e2e/test_full_stack_diagnostic.py"])]

def gate_info():
    r=[]
    for n,c in GATES:
        rc,so,se=_run(c)
        r.append({"name":n,"pass":rc==0,"exit":rc,
                  "tail":(so+("\n"+se if se else "")).strip().splitlines()[-4:]})
    return r

def print_human(d):
    g,t,tr,v=d["git"],d["tree"],d["tracked"],d["verdict"]
    ts=_dt.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    print("="*70); print(" AETHER STATUS")
    print(f" report format   : {REPORT_FORMAT}"); print(f" generated at    : {ts}")
    print("="*70)
    print("\nGIT")
    print(f"  branch           : {g['branch']}")
    print(f"  head             : {g['head']}")
    print(f"  origin/main      : {g['origin_main']}")
    print(f"  in sync          : {g['in_sync']}")
    print(f"  remote           : {g['remote']}")
    n=len(g["dirty_files"])
    print(f"  working tree     : {'clean' if not g['dirty'] else str(n)+' change(s)'}")
    print(f"  last commit      : {g['last_commit']}")
    print("\nTREE")
    pl=t["components_per_layer"]
    print(f"  components       : {t['components_total']}  (ax={pl['ax']} ag={pl['ag']} ac={pl['ac']})")
    print(f"  _archive present : {t['archive_present']}")
    m=t["missing"]
    print(f"  required dirs    : {'all present' if not m else 'MISSING: '+str(m)}")
    for k,val in t.get("subdirs",{}).items():
        print(f"  {k:24s}: {'present' if val else 'MISSING'}")
    print("\nSIZE")
    print(f"  tracked files    : {tr['tracked_files']}")
    print(f"  tracked bytes    : {tr['tracked_bytes']:,}  ({tr['tracked_bytes']/1024/1024:.2f} MiB)")
    if "gates" in d:
        print("\nGATES")
        for gr in d["gates"]:
            print(f"  [{'PASS' if gr['pass'] else 'FAIL'}] {gr['name']} (exit {gr['exit']})")
            if not gr["pass"]:
                for line in gr["tail"]: print(f"        {line}")
    print()
    if v["status"]=="OK": print("VERDICT: OK")
    else:
        print(f"VERDICT: ATTENTION ({','.join(r['code'] for r in v['reasons'])})")
        for r in v["reasons"]: print(f"  {r['code']}: {r['detail']}")
    print("="*70)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",action="store_true")
    ap.add_argument("--gates",action="store_true")
    a=ap.parse_args()
    d={"git":git_info(),"tree":tree_info(),"tracked":tracked_info(),
       "report_format":REPORT_FORMAT,
       "generated_at":_dt.datetime.now().astimezone().isoformat(timespec="seconds")}
    if a.gates: d["gates"]=gate_info()
    d["verdict"]=compute_verdict(d)
    print(json.dumps(d,indent=2,sort_keys=True)) if a.json else print_human(d)
    return 0 if d["verdict"]["status"]=="OK" else 1

if __name__=="__main__":
    sys.exit(main())
