#!/usr/bin/env python3
"""Real clause/control/evidence families per standard."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = {
  "ISO/IEC 12207": {"clauses":["6.1 System Context","6.2 Software Specific","6.3 Software Reuse","6.4 Software Services"],"controls":["lifecycle","process","activity","task"],"evidence":["process_record","task_output"]},
  "ISO/IEC 15288": {"clauses":["6.1 Agreement","6.2 Organizational","6.3 Technical Mgmt","6.4 Technical"],"controls":["agreement","organizational","technical_mgmt","technical"],"evidence":["process_artifact","decision_record"]},
  "ISO/IEC 25010": {"clauses":["8.1 Functional","8.2 Performance","8.3 Compatibility","8.4 Usability","8.5 Reliability","8.6 Security","8.7 Maintainability","8.8 Portability"],"controls":["functional","performance","compatibility","usability","reliability","security","maintainability","portability"],"evidence":["quality_measure","test_report"]},
  "ISO/IEC 27001": {"clauses":["A.5 Policies","A.6 Org","A.8 Asset","A.9 Access","A.10 Crypto","A.12 Ops","A.13 Comms","A.14 Dev","A.15 Supplier","A.16 Incident","A.17 Continuity","A.18 Compliance"],"controls":["policy","access","crypto","ops","comms","dev","supplier","incident","continuity","compliance"],"evidence":["control_evidence","audit_log"]},
  "ISO 9001": {"clauses":["4 Context","5 Leadership","6 Planning","7 Support","8 Operation","9 Performance","10 Improvement"],"controls":["context","leadership","planning","support","operation","performance","improvement"],"evidence":["qms_record","review_minutes"]},
  "IEEE 730": {"clauses":["4 SQA Process","5 SQA Plan","6 SQA Activities","7 SQA Records"],"controls":["sqa_process","sqa_plan","sqa_activity","sqa_record"],"evidence":["sqa_report","review_record"]},
  "IEEE 830": {"clauses":["1 Introduction","2 Overall Description","3 Specific Reqs","4 External Interfaces","5 Appendices"],"controls":["intro","overall","specific","interface","appendix"],"evidence":["srs","trace_matrix"]},
  "IEEE 1012": {"clauses":["5 V&V Concepts","6 V&V Processes","7 V&V Activities","8 V&V Reporting"],"controls":["concept","process","activity","reporting"],"evidence":["vandv_plan","vandv_report"]},
  "NIST SP 800-53": {"clauses":["AC Access","AU Audit","CM Config","CP Contingency","IA Ident","IR Incident","RA Risk","SA Acquisition","SC Comms","SI Integrity","SR Supply"],"controls":["access","audit","config","contingency","ident","incident","risk","acquisition","comms","integrity","supply"],"evidence":["control_assessment","poam"]},
  "NIST CSF 2.0": {"clauses":["GV Govern","ID Identify","PR Protect","DE Detect","RS Respond","RC Recover"],"controls":["govern","identify","protect","detect","respond","recover"],"evidence":["csf_profile","maturity_assessment"]},
  "NIST SP 800-218 SSDF": {"clauses":["PO Prepare","PS Protect","PW Produce","RV Respond"],"controls":["prepare","protect","produce","respond"],"evidence":["ssdf_practice","vuln_record"]},
  "OWASP ASVS 4.0": {"clauses":["V1 Arch","V2 Authn","V3 Session","V4 Access","V5 Validate","V6 Crypto","V7 Error","V8 Data","V9 Comms","V12 Files","V13 API","V14 Config"],"controls":["arch","authn","session","access","validate","crypto","error","data","comms","files","api","config"],"evidence":["asvs_report","test_log"]},
  "OWASP SAMM 2.0": {"clauses":["Governance","Design","Implementation","Verification","Operations"],"controls":["governance","design","implementation","verification","operations"],"evidence":["samm_scorecard","improvement_roadmap"]},
  "CMMI DEV 3.0": {"clauses":["RD Requirements","TS Technical","PI Integration","VER Verification","VAL Validation","CM Config","PPQA Process QA","MA Measurement"],"controls":["requirements","technical","integration","verification","validation","config","qa","measurement"],"evidence":["process_appraisal","work_product"]},
  "ITIL 4": {"clauses":["Service Value System","Guiding Principles","Practices","Continual Improvement"],"controls":["svs","principles","practices","improvement"],"evidence":["service_record","csi_register"]},
  "COBIT 2019": {"clauses":["EDM","APO","BAI","DSS","MEA"],"controls":["edm","apo","bai","dss","mea"],"evidence":["cobit_assessment","governance_artifact"]},
  "IEC 61508": {"clauses":["SIL1","SIL2","SIL3","SIL4"],"controls":["sil1","sil2","sil3","sil4"],"evidence":["safety_case","sil_analysis"]},
  "DO-178C": {"clauses":["DAL A","DAL B","DAL C","DAL D","DAL E"],"controls":["dal_a","dal_b","dal_c","dal_d","dal_e"],"evidence":["objective","cert_package"]},
  "SLSA 1.0": {"clauses":["Level 1","Level 2","Level 3","Level 4"],"controls":["level1","level2","level3","level4"],"evidence":["provenance","build_attestation"]},
  "EU AI Act": {"clauses":["Prohibited","High-Risk","Limited-Risk","Minimal-Risk"],"controls":["prohibited","high_risk","limited_risk","minimal_risk"],"evidence":["ai_conformity","risk_assessment"]},
  "ISO/IEC 42001": {"clauses":["4 Context","5 Leadership","6 Planning","7 Support","8 Operation","9 Performance","10 Improvement"],"controls":["context","leadership","planning","support","operation","performance","improvement"],"evidence":["ai_ms_record","ai_risk_assessment"]},
  "PCI DSS 4.0": {"clauses":["1 Network","2 Config","3 Data","4 Transit","5 Malware","6 Dev","7 Access","8 Ident","9 Physical","10 Logging","11 Testing","12 Policy"],"controls":["network","config","data","transit","malware","dev","access","ident","physical","logging","testing","policy"],"evidence":["roc","aoc"]},
  "GDPR": {"clauses":["Art5 Principles","Art6 Lawful","Art15 Access","Art17 Erasure","Art25 Design","Art32 Security","Art33 Breach"],"controls":["principles","lawful","access","erasure","design","security","breach"],"evidence":["dpia","processing_record"]},
  "HIPAA": {"clauses":["Administrative","Physical","Technical","Organizational","Policies"],"controls":["admin","physical","technical","org","policies"],"evidence":["risk_analysis","baa"]},
  "FedRAMP Rev 5": {"clauses":["AC","AU","CM","CP","IA","IR","RA","SA","SC","SI"],"controls":["access","audit","config","contingency","ident","incident","risk","acquisition","comms","integrity"],"evidence":["sar","poam"]},
  "FIPS 140-3": {"clauses":["Level 1","Level 2","Level 3","Level 4"],"controls":["level1","level2","level3","level4"],"evidence":["cmvp_cert","module_spec"]},
  "CycloneDX 1.5": {"clauses":["metadata","components","dependencies","vulnerabilities","services"],"controls":["metadata","components","deps","vulns","services"],"evidence":["bom","vex"]},
  "SPDX 2.3": {"clauses":["Package","File","Snippet","License","Relationship"],"controls":["package","file","snippet","license","relationship"],"evidence":["spdx_doc","license_list"]},
}
DEFAULT = {"clauses":["Clause 1","Clause 2","Clause 3","Clause 4"],"controls":["traceable","reviewed","approved","verified"],"evidence":["artifact","record"]}
SDLC = json.loads((ROOT/"standards/sdlc.json").read_text())
stds = sorted({r["identity"]["standard"] for r in SDLC["requirements"]})
reg = {s: REGISTRY.get(s, DEFAULT) for s in stds}
(ROOT/"standards/registry.json").write_text(json.dumps({"registry":reg,"count":len(reg)},indent=2))
print(f"registry: {len(reg)} standards")
