"""Contract binding for GOV-FED-001-federation-gateway-and-domain-exchange-coordinator.

Emitted/consumed schema: contracts/canonical/federation-gateway.schema.json
$id: asf.gov.federation_gateway.v1

This component is Deferred per ASF v1.2. The schema exists so the shape of a
future federation decision is declared and testable, not so that runtime
federation is asserted. Production federation activation requires the gate
items recorded in
deploy/profiles/enterprise-multidepartment/federation-activation-gate.json.
"""

SCHEMA_PATH = "contracts/canonical/federation-gateway.schema.json"
SCHEMA_ID   = "asf.gov.federation_gateway.v1"
