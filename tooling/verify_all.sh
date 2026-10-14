#!/usr/bin/env bash
set -uo pipefail
cd "$HOME/aether"
FAIL=0
step() { printf "\n== %s ==\n" "$*"; }
ok()   { printf "  OK  %s\n" "$*"; }
bad()  { printf "  ERR %s\n" "$*"; FAIL=1; }

step "1. pytest"
if python -m pytest -q 2>&1 | tail -1 | grep -q passed; then
  python -m pytest -q 2>&1 | tail -1 | sed 's/^/  /'
  ok pytest
else
  bad pytest
fi

step "2. settings"
if SOVEREIGN_NODE_ID=verify python -c "from ag.settings import get_settings; get_settings()" 2>/dev/null; then
  ok ag.settings
else
  bad ag.settings
fi

step "3. metrics"
if python -c "from ag.metrics import Metrics; m=Metrics(namespace='verify'); m.record(method='GET',path='/x',status_code=200,duration_seconds=0.01); assert b'verify_requests_total' in m.render()" 2>/dev/null; then
  ok ag.metrics
else
  bad ag.metrics
fi

step "4. health"
if SOVEREIGN_NODE_ID=verify python -c "from ag.health import check_all; c,b=check_all(); assert set(b['subsystems'])=={'settings','ledger','model','disk'}" 2>/dev/null; then
  ok ag.health
else
  bad ag.health
fi

step "5. tracing"
if python -c "from ag.tracing import init_tracing, shutdown_tracing; assert init_tracing('verify', endpoint=None, console=True) is True; shutdown_tracing(force_flush_timeout_ms=100)" 2>/dev/null; then
  ok ag.tracing
else
  bad ag.tracing
fi

step "6. tracing fails safe"
if python -c "from ag.tracing import init_tracing, shutdown_tracing; assert init_tracing('verify', endpoint='http://127.0.0.1:59999') is False; shutdown_tracing(force_flush_timeout_ms=100)" 2>/dev/null; then
  ok "ag.tracing fails safe"
else
  bad "ag.tracing fails safe"
fi

step "7. license audit"
if command -v cyclonedx-py >/dev/null 2>&1; then
  mkdir -p sbom
  cyclonedx-py environment --output-format json -o sbom/sbom.cdx.json >/dev/null 2>&1
  N=$(python -c "import json; print(len(json.load(open('sbom/sbom.cdx.json')).get('components', [])))" 2>/dev/null || echo 0)
  if [ "$N" -gt 0 ]; then ok "sbom ($N components)"; else bad "sbom empty"; fi
else
  echo "  - cyclonedx-bom not installed; skipping"
fi

step "8. app"
if python -c "from ac.app import app" 2>/dev/null; then ok ac.app; else bad ac.app; fi

step "9. docs index"
if [ -f docs/INDEX.md ]; then ok docs/INDEX.md; else bad docs/INDEX.md; fi

step "result"
if [ "$FAIL" = "0" ]; then ok "all green"; exit 0; else bad "failures"; exit 1; fi
