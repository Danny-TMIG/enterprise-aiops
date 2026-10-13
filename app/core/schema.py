"""Every column, every table. One DDL. Real SQLite. Survives restart.

Sources:
  A-P          gap register (sections A through P)
  ontology     data/ontology.txt (Ontological / Mathematical / Logical)
  registry     first-class registry entry + publication

Standard columns on every row table (short names kept for joins):
  id           INTEGER PK
  code         TEXT UNIQUE  stable slug
  label        TEXT NOT NULL
  status       TEXT NOT NULL DEFAULT 'unknown'   open|partial|closed|na
  owner        TEXT           named human
  authority    TEXT           who accepts residual risk
  source       TEXT           provenance file:line or url
  notes        TEXT
  meta         JSON
  version      INTEGER DEFAULT 1
  hash         TEXT           content hash
  created_at   TEXT
  updated_at   TEXT
  deleted_at   TEXT

Cross-cutting:
  refs         any row -> any row, typed, hashed
  events       append-only ledger, chain hashed
"""
from __future__ import annotations

# ── gap register: (slug, section, ordinal, description) ────────────
GAPS = [
 # A — Runtime & Execution
 ("runtime_solver_binaries",       "A", 1,  "Actual solver binaries (Z3, CVC5, Lean4, Coq, TLA+)"),
 ("runtime_prover_services",       "A", 2,  "Actual prover services"),
 ("runtime_proof_checker_kernel",  "A", 3,  "Proof-checker kernel"),
 ("runtime_sigstore",              "A", 4,  "Real Sigstore (Fulcio + Rekor + CT log)"),
 ("runtime_vault_hsm_kms",         "A", 5,  "Vault / HSM / KMS integration"),
 ("runtime_message_bus",           "A", 6,  "Message bus (NATS / Kafka / NATS JetStream)"),
 ("runtime_service_mesh",          "A", 7,  "Service mesh (Istio / Linkerd / Cilium)"),
 ("runtime_event_store",           "A", 8,  "Event store (immutable append-only)"),
 ("runtime_opa_bundles",           "A", 9,  "Actual OPA / Gatekeeper policy bundles"),
 ("runtime_kyverno_policies",      "A",10,  "Kyverno policies"),
 ("runtime_in_toto_dsse",          "A",11,  "in-toto / DSSE signing library"),
 ("runtime_sbom_generator",        "A",12,  "CycloneDX/SPDX SBOM generator"),
 ("runtime_ocsf_normalizer",       "A",13,  "OCSF normalizer"),
 ("runtime_ebpf_falco",            "A",14,  "eBPF / Falco runtime enforcement"),

 # B — Data & State
 ("data_evidence_graph",           "B", 1,  "Evidence graph database"),
 ("data_threat_control_graph",     "B", 2,  "Threat + control graph database"),
 ("data_checkpoint_registry",      "B", 3,  "Checkpoint registry service"),
 ("data_model_lineage",            "B", 4,  "Model lineage store"),
 ("data_authority_registry",       "B", 5,  "Authority registry"),
 ("data_approval_ledger",          "B", 6,  "Approval ledger"),
 ("data_incident_ledger",          "B", 7,  "Incident ledger"),
 ("data_vulnerability_db",         "B", 8,  "Vulnerability database"),
 ("data_dependency_dag",           "B", 9,  "Dependency DAG"),
 ("data_knowledge_base",           "B",10,  "Knowledge base / RAG store"),
 ("data_telemetry_ts",             "B",11,  "Time-series store for telemetry"),
 ("data_secret_store",             "B",12,  "Secret store (Vault)"),
 ("data_artifact_registry",        "B",13,  "Artifact registry (OCI)"),

 # C — Operational
 ("ops_runbooks",                  "C", 1,  "SOC runbooks per alert type"),
 ("ops_detection_rules",           "C", 2,  "Detection rules (Sigma, YARA, Suricata, Falco)"),
 ("ops_response_playbooks",        "C", 3,  "Response playbooks"),
 ("ops_ics",                       "C", 4,  "Incident command structure"),
 ("ops_on_call",                   "C", 5,  "On-call rotation"),
 ("ops_escalation",                "C", 6,  "Escalation matrix"),
 ("ops_slos",                      "C", 7,  "SLO / SLI / error budgets"),
 ("ops_backups",                   "C", 8,  "Backup procedures"),
 ("ops_restores",                  "C", 9,  "Restore procedures"),
 ("ops_dr_failover",               "C",10,  "DR / failover runbook"),
 ("ops_chaos_suite",               "C",11,  "Chaos engineering suite"),
 ("ops_capacity_model",            "C",12,  "Capacity planning model"),
 ("ops_cost_model",                "C",13,  "Cost model / chargeback"),
 ("ops_cab",                       "C",14,  "Change advisory process"),
 ("ops_postmortem_process",        "C",15,  "Post-incident review process"),
 ("ops_tabletop_schedule",         "C",16,  "Tabletop exercise schedule"),
 ("ops_watch_floor",               "C",17,  "Watch-floor procedures"),

 # D — Governance & Authority
 ("gov_named_authorities",         "D", 1,  "Named accountable authorities"),
 ("gov_raci",                      "D", 2,  "RACI matrix"),
 ("gov_delegation_chain",          "D", 3,  "Authority delegation chain"),
 ("gov_approval_workflow",         "D", 4,  "Approval workflow engine"),
 ("gov_policy_as_code",            "D", 5,  "Policy-as-code library (Rego)"),
 ("gov_risk_register",             "D", 6,  "Risk register"),
 ("gov_waivers",                   "D", 7,  "Exception / waiver process"),
 ("gov_audit_trail",               "D", 8,  "Audit trail persistence"),
 ("gov_dpia",                      "D", 9,  "DPIA"),
 ("gov_ropa",                      "D",10,  "ROPA"),
 ("gov_lia",                       "D",11,  "Legitimate interest assessments"),
 ("gov_export_control",            "D",12,  "Export control review"),
 ("gov_sanctions",                 "D",13,  "Sanctions screening"),
 ("gov_third_party_risk",          "D",14,  "Third-party risk assessments"),

 # E — AI / Model Security
 ("ai_checkpoint_registry",        "E", 1,  "Checkpoint registry service"),
 ("ai_model_lineage_tracker",      "E", 2,  "Model lineage tracker"),
 ("ai_quantization_proofs",        "E", 3,  "Quantization equivalence proofs"),
 ("ai_lora_attribution",           "E", 4,  "LoRA/adapter attribution"),
 ("ai_guardrails",                 "E", 5,  "Guardrail implementation"),
 ("ai_prompt_injection_defenses",  "E", 6,  "Prompt injection defenses"),
 ("ai_rag_poisoning_defenses",     "E", 7,  "RAG poisoning defenses"),
 ("ai_tool_sandboxing",            "E", 8,  "Tool-use sandboxing"),
 ("ai_red_team_harness",           "E", 9,  "Model red-team harness"),
 ("ai_eval_harness",               "E",10,  "Model evaluation harness"),
 ("ai_jailbreak_detection",        "E",11,  "Jailbreak detection"),
 ("ai_exfil_controls",             "E",12,  "Data exfiltration controls"),
 ("ai_checkpoint_local_enforce",   "E",13,  "Checkpoint-local qualification enforcement"),
 ("ai_non_transfer_enforce",       "E",14,  "Non-transfer enforcement"),
 ("ai_training_provenance",        "E",15,  "Training data provenance"),
 ("ai_model_cards",                "E",16,  "Model card generation"),
 ("ai_license_review",             "E",17,  "Foundation model licensing review"),
 ("ai_frontier_evals",             "E",18,  "Frontier model safety evaluations"),

 # F — Testing & Verification
 ("test_integration_harness",      "F", 1,  "Integration test harness"),
 ("test_e2e",                      "F", 2,  "End-to-end test suite"),
 ("test_perf_benchmarks",          "F", 3,  "Performance benchmarks"),
 ("test_fuzzing",                  "F", 4,  "Fuzzing infrastructure"),
 ("test_mutation",                 "F", 5,  "Mutation testing"),
 ("test_property_based",           "F", 6,  "Property-based testing"),
 ("test_conformance",              "F", 7,  "Conformance test suites"),
 ("test_security_vertical",        "F", 8,  "Security vertical slice"),
 ("test_adversarial_ml",           "F", 9,  "Adversarial ML test suite"),
 ("test_load",                     "F",10,  "Load tests"),
 ("test_chaos_drills",             "F",11,  "Chaos drills"),
 ("test_failure_injection",        "F",12,  "Failure injection"),
 ("test_recovery",                 "F",13,  "Recovery tests"),
 ("test_attestation_verify",       "F",14,  "Attestation verification tests"),
 ("test_cross_plane",              "F",15,  "Cross-plane integration tests"),
 ("test_regression_corpus",        "F",16,  "Regression test corpus"),

 # G — Human Factors
 ("hx_operator_ui",                "G", 1,  "Operator UI / dashboard"),
 ("hx_analyst_console",            "G", 2,  "Security analyst console"),
 ("hx_authority_ui",               "G", 3,  "Authority approval UI"),
 ("hx_ir_console",                 "G", 4,  "Incident response console"),
 ("hx_evidence_explorer",          "G", 5,  "Evidence explorer"),
 ("hx_graph_visualizer",           "G", 6,  "Graph visualizer"),
 ("hx_alerting",                   "G", 7,  "Alerting"),
 ("hx_reporting",                  "G", 8,  "Reporting"),
 ("hx_notification",               "G", 9,  "Notification system"),
 ("hx_training",                   "G",10,  "Training material"),
 ("hx_roles",                      "G",11,  "Role definitions & job descriptions"),
 ("hx_comms_plan",                 "G",12,  "Communication plan"),
 ("hx_escalation_ux",              "G",13,  "Escalation UX"),
 ("hx_accessibility",              "G",14,  "Accessibility compliance"),
 ("hx_localization",               "G",15,  "Localization"),

 # H — Physical
 ("phys_hsm",                      "H", 1,  "HSM deployment"),
 ("phys_tpm",                      "H", 2,  "TPM provisioning"),
 ("phys_secure_boot",              "H", 3,  "Secure boot chain"),
 ("phys_firmware_attestation",     "H", 4,  "Firmware attestation"),
 ("phys_jtag",                     "H", 5,  "JTAG / debug port protection"),
 ("phys_sidechannel",              "H", 6,  "Side-channel protections"),
 ("phys_rf_monitoring",            "H", 7,  "RF monitoring"),
 ("phys_access_controls",          "H", 8,  "Physical access controls"),
 ("phys_tamper_evident",           "H", 9,  "Tamper-evident enclosures"),
 ("phys_environmental",            "H",10,  "Environmental controls"),
 ("phys_emi_shielding",            "H",11,  "Faraday / EMI shielding"),
 ("phys_cable_locks",              "H",12,  "Cable / port locks"),
 ("phys_media_sanitization",       "H",13,  "Media sanitization procedures"),

 # I — Regulatory (regimes become rows; evidence/audit are refs)
 ("reg_nist_csf",                  "I", 1,  "NIST CSF 2.0"),
 ("reg_nist_800_53",               "I", 2,  "NIST SP 800-53"),
 ("reg_nist_800_207",              "I", 3,  "NIST SP 800-207 Zero Trust"),
 ("reg_nist_800_218",              "I", 4,  "NIST SP 800-218 SSDF"),
 ("reg_nist_ai_rmf",               "I", 5,  "NIST AI RMF"),
 ("reg_iso_27001",                 "I", 6,  "ISO 27001"),
 ("reg_iso_27017",                 "I", 7,  "ISO 27017"),
 ("reg_iso_27018",                 "I", 8,  "ISO 27018"),
 ("reg_iso_42001",                 "I", 9,  "ISO 42001"),
 ("reg_iso_5230",                  "I",10,  "ISO 5230 OpenChain"),
 ("reg_iso_25010",                 "I",11,  "ISO/IEC 25010"),
 ("reg_soc2",                      "I",12,  "SOC 2"),
 ("reg_fedramp",                   "I",13,  "FedRAMP"),
 ("reg_pci_dss",                   "I",14,  "PCI DSS"),
 ("reg_hipaa",                     "I",15,  "HIPAA"),
 ("reg_gdpr",                      "I",16,  "GDPR / UK GDPR"),
 ("reg_ccpa",                      "I",17,  "CCPA / CPRA"),
 ("reg_dora",                      "I",18,  "DORA"),
 ("reg_nis2",                      "I",19,  "NIS2"),
 ("reg_cmmc",                      "I",20,  "CMMC"),
 ("reg_eo_14028",                  "I",21,  "EO 14028"),
 ("reg_eo_14110",                  "I",22,  "EO 14110"),
 ("reg_eu_ai_act",                 "I",23,  "EU AI Act"),
 ("reg_fips_140_3",                "I",24,  "FIPS 140-3"),
 ("reg_common_criteria",           "I",25,  "Common Criteria"),

 # J — Legal & Contractual
 ("legal_clas",                    "J", 1,  "Contributor License Agreements"),
 ("legal_dco",                     "J", 2,  "DCO enforcement"),
 ("legal_trademark",               "J", 3,  "Trademark policy"),
 ("legal_copyright_assignment",    "J", 4,  "Copyright assignment process"),
 ("legal_patent_grant",            "J", 5,  "Patent grant / retaliation"),
 ("legal_license_compat",          "J", 6,  "License compatibility review"),
 ("legal_third_party_licenses",    "J", 7,  "Third-party license inventory"),
 ("legal_agpl_disclosure",         "J", 8,  "Open source disclosure AGPL §13"),
 ("legal_dpas",                    "J", 9,  "Data Processing Agreements"),
 ("legal_subprocessors",           "J",10,  "Sub-processor list GDPR Art. 28"),
 ("legal_sccs",                    "J",11,  "Standard Contractual Clauses"),
 ("legal_bcrs",                    "J",12,  "Binding Corporate Rules"),
 ("legal_cbtas",                   "J",13,  "Cross-border transfer assessments"),
 ("legal_tos",                     "J",14,  "Terms of Service / AUP"),
 ("legal_slas",                    "J",15,  "SLA definitions"),
 ("legal_bug_bounty",              "J",16,  "Bug bounty program"),
 ("legal_vdp",                     "J",17,  "Vulnerability disclosure policy"),
 ("legal_cvd",                     "J",18,  "Coordinated disclosure process"),

 # K — Operational Maturity
 ("mat_slos",                      "K", 1,  "SLO definitions"),
 ("mat_slis",                      "K", 2,  "SLI measurements"),
 ("mat_error_budgets",             "K", 3,  "Error budget policy"),
 ("mat_toil",                      "K", 4,  "Toil measurement"),
 ("mat_oncall_load",               "K", 5,  "On-call load analysis"),
 ("mat_change_failure_rate",       "K", 6,  "Change failure rate"),
 ("mat_mttr_mttd",                 "K", 7,  "MTTR / MTTD baselines"),
 ("mat_deploy_frequency",          "K", 8,  "Deployment frequency baseline"),
 ("mat_lead_time",                 "K", 9,  "Lead time for change"),
 ("mat_capacity_headroom",         "K",10,  "Capacity headroom policy"),
 ("mat_cost_per_txn",              "K",11,  "Cost per transaction"),
 ("mat_carbon",                    "K",12,  "Carbon accounting"),
 ("mat_vendor_tiers",              "K",13,  "Vendor risk tiers"),
 ("mat_bcp",                       "K",14,  "Business continuity plan"),
 ("mat_drp",                       "K",15,  "Disaster recovery plan"),
 ("mat_crisis_comms",              "K",16,  "Crisis communications plan"),

 # L — Culture & Process
 ("cul_security_champions",        "L", 1,  "Security champions program"),
 ("cul_threat_modeling",           "L", 2,  "Threat modeling ceremony"),
 ("cul_design_review_board",       "L", 3,  "Design review board"),
 ("cul_adrs",                      "L", 4,  "Architecture Decision Records"),
 ("cul_rfcs",                      "L", 5,  "RFC process"),
 ("cul_game_days",                 "L", 6,  "Game days"),
 ("cul_purple_team",               "L", 7,  "Purple-team cycles"),
 ("cul_red_team_engagements",      "L", 8,  "Red-team engagements"),
 ("cul_tabletops",                 "L", 9,  "Tabletop exercises"),
 ("cul_post_incident_reviews",     "L",10,  "Post-incident reviews"),
 ("cul_lessons",                   "L",11,  "Lessons-learned database"),
 ("cul_knowledge_transfer",        "L",12,  "Knowledge transfer process"),
 ("cul_succession",                "L",13,  "Succession planning"),
 ("cul_burnout",                   "L",14,  "Burnout monitoring"),

 # M — Reference Documentation
 ("doc_ref_architecture",          "M", 1,  "Reference architecture document"),
 ("doc_adr_library",               "M", 2,  "ADR library"),
 ("doc_runbook_library",           "M", 3,  "Runbook library"),
 ("doc_playbook_library",          "M", 4,  "Playbook library"),
 ("doc_glossary",                  "M", 5,  "Glossary"),
 ("doc_threat_models",             "M", 6,  "Threat model documents"),
 ("doc_dfds",                      "M", 7,  "Data flow diagrams"),
 ("doc_network_topology",          "M", 8,  "Network topology diagrams"),
 ("doc_trust_boundaries",          "M", 9,  "Trust boundary diagrams"),
 ("doc_sequence_diagrams",         "M",10,  "Sequence diagrams"),
 ("doc_deployment_guides",         "M",11,  "Deployment guides"),
 ("doc_migration_guides",          "M",12,  "Migration guides"),
 ("doc_deprecation_policy",        "M",13,  "Deprecation policy"),
 ("doc_versioning_policy",         "M",14,  "Versioning policy"),
 ("doc_compat_matrix",             "M",15,  "Compatibility matrix"),
 ("doc_error_taxonomy",            "M",16,  "Error taxonomy"),
 ("doc_event_contracts",           "M",17,  "Event contracts"),
 ("doc_api_specs",                 "M",18,  "API specifications"),
 ("doc_schema_registry",           "M",19,  "Schema registry"),

 # N — Cross-Plane Integration
 ("x_mesh_sec_bridge",             "N", 1,  "OP4CSE-MESH <-> OP4CSE-SEC"),
 ("x_sec_devsecops_bridge",        "N", 2,  "security plane <-> DevSecOps"),
 ("x_checkpoint_ses_bridge",       "N", 3,  "checkpoint fabric <-> SES addresses"),
 ("x_assurance_detection_bridge",  "N", 4,  "ASSURANCE hypotheses <-> detection rules"),
 ("x_evidence_authority_bridge",   "N", 5,  "evidence graph <-> authority ledger"),
 ("x_threat_dag_bridge",           "N", 6,  "threat+control graph <-> DAG"),
 ("x_ooda_pipeline_bridge",        "N", 7,  "OODA <-> pipeline stages"),
 ("x_ir_runtime_bridge",           "N", 8,  "compiler IR targets <-> runtime"),
 ("x_fsf_enforcement_bridge",      "N", 9,  "FSF/SPDX/REUSE <-> enforcement"),
 ("x_iso_guards_bridge",           "N",10,  "ISO/NIST/OpenSSF <-> guards"),
]

STD_COLS = """
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT NOT NULL,
    label        TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'unknown',
    owner        TEXT,
    authority    TEXT,
    source       TEXT,
    notes        TEXT,
    meta         TEXT NOT NULL DEFAULT '{}',
    version      INTEGER NOT NULL DEFAULT 1,
    hash         TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at   TEXT,
    UNIQUE(code)
"""

CROSS_TABLES = """
CREATE TABLE IF NOT EXISTS ontology (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    domain       TEXT NOT NULL,
    name         TEXT NOT NULL,
    code         TEXT NOT NULL UNIQUE,
    index_in_domain INTEGER NOT NULL,
    index_global    INTEGER NOT NULL,
    meta         TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_ontology_domain ON ontology(domain);
CREATE INDEX IF NOT EXISTS ix_ontology_name   ON ontology(name);

CREATE TABLE IF NOT EXISTS registry_entries (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    domain       TEXT NOT NULL,
    name         TEXT NOT NULL,
    key          TEXT NOT NULL UNIQUE,
    path         TEXT NOT NULL,
    ordinal      INTEGER NOT NULL,
    first_class  INTEGER NOT NULL DEFAULT 0,
    meta         TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_registry_domain ON registry_entries(domain);

CREATE TABLE IF NOT EXISTS registry_publications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    version      TEXT NOT NULL,
    authority    TEXT NOT NULL,
    total        INTEGER NOT NULL,
    sha256       TEXT NOT NULL,
    payload      TEXT NOT NULL,
    published_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS refs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    src_table    TEXT NOT NULL,
    src_id       INTEGER NOT NULL,
    dst_table    TEXT NOT NULL,
    dst_id       INTEGER,
    dst_key      TEXT,
    kind         TEXT NOT NULL DEFAULT 'related',
    meta         TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_refs_src ON refs(src_table, src_id);
CREATE INDEX IF NOT EXISTS ix_refs_dst ON refs(dst_table, dst_id);

CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    seq          INTEGER NOT NULL UNIQUE,
    kind         TEXT NOT NULL,
    subject      TEXT NOT NULL,
    payload      TEXT NOT NULL,
    prev_hash    TEXT,
    hash         TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_events_kind ON events(kind);
"""

def ddl() -> str:
    parts = []
    for slug, _section, _ord_, _desc in GAPS:
        parts.append(f"CREATE TABLE IF NOT EXISTS {slug} ({STD_COLS});")
        parts.append(f"CREATE INDEX IF NOT EXISTS ix_{slug}_status ON {slug}(status);")
        parts.append(f"CREATE INDEX IF NOT EXISTS ix_{slug}_owner  ON {slug}(owner);")
    parts.append(CROSS_TABLES)
    return "\n".join(parts)

TABLE_NAMES = [slug for slug, *_ in GAPS] + [
    "ontology", "registry_entries", "registry_publications", "refs", "events",
]

__all__ = ["CROSS_TABLES", "GAPS", "STD_COLS", "TABLE_NAMES", "ddl"]


# ── self-registration as capability `schema` ───────────────────────
def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("schema")
    def _entry(*args, **kwargs):
        return {"module": "app.core.schema", "code": "schema"}


_self_register()
