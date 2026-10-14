#!/usr/bin/env bash
set -uo pipefail
cd "$HOME/aether"

echo "== 1. commit block 6 =="
git add ag/licenses.py tests/test_licenses.py tooling/block6_setup.sh tooling/block6_live_proof.sh sbom/.gitignore 2>/dev/null || true
git status --short
git commit -s -m "feat(ag): real license audit with SPDX expression evaluation and known-symbol classification" || true
git push origin main || true
git log --oneline -1

echo
echo "== 2. install otel deps =="
pip install "opentelemetry-api>=1.30" "opentelemetry-sdk>=1.30" "opentelemetry-exporter-otlp-proto-grpc>=1.30"
python -c "import opentelemetry, opentelemetry.sdk, opentelemetry.exporter.otlp.proto.grpc; print('otel deps ok')"

echo
echo "== 3. probe otel API =="
python3 - <<'PYEOF'
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import inspect

print("== TracerProvider.__init__ ==")
try:
    print(inspect.signature(TracerProvider.__init__))
except Exception as e:
    print("  (signature unavailable:", e, ")")

print()
print("== BatchSpanProcessor.__init__ ==")
try:
    print(inspect.signature(BatchSpanProcessor.__init__))
except Exception as e:
    print("  (signature unavailable:", e, ")")

print()
print("== OTLPSpanExporter.__init__ ==")
try:
    print(inspect.signature(OTLPSpanExporter.__init__))
except Exception as e:
    print("  (signature unavailable:", e, ")")

print()
print("== Resource.create ==")
try:
    print(inspect.signature(Resource.create))
except Exception as e:
    print("  (signature unavailable:", e, ")")

print()
print("== methods present ==")
print("  TracerProvider.shutdown:     ", hasattr(TracerProvider, "shutdown"))
print("  TracerProvider.force_flush:  ", hasattr(TracerProvider, "force_flush"))
print("  BatchSpanProcessor.shutdown: ", hasattr(BatchSpanProcessor, "shutdown"))

print()
print("== span API ==")
tracer = trace.get_tracer("probe")
with tracer.start_as_current_span("probe-span") as span:
    print("  span type:             ", type(span).__name__)
    print("  span.set_attribute:    ", hasattr(span, "set_attribute"))
    print("  span.record_exception: ", hasattr(span, "record_exception"))
    print("  span.set_status:       ", hasattr(span, "set_status"))

print()
print("== propagators ==")
try:
    from opentelemetry.propagate import set_global_textmap  # noqa: F401
    from opentelemetry.propagators.composite import CompositePropagator  # noqa: F401
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator  # noqa: F401
    from opentelemetry.baggage.propagation import W3CBaggagePropagator  # noqa: F401
    print("  composite + w3c propagators available")
except Exception as e:
    print("  propagators error:", e)

print()
print("== otel versions ==")
try:
    from importlib.metadata import version
    for pkg in ("opentelemetry-api", "opentelemetry-sdk", "opentelemetry-exporter-otlp-proto-grpc"):
        try:
            print(f"  {pkg}: {version(pkg)}")
        except Exception:
            print(f"  {pkg}: unknown")
except Exception:
    pass
PYEOF
