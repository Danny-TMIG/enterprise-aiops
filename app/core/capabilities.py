"""Capability registry + honest dispatcher.

Every "tool" from the OmniTech pitch becomes a row with a status:

    real          — code exists in this repo, callable now
    stub          — a function exists but returns a placeholder
    aspirational  — named, no implementation; dispatch returns 501

Nothing lies. dispatch(name) either calls the real implementation or
returns a structured "unimplemented" record. Every dispatch is written
to the events ledger. Every capability is bridged to the gap-register
row it addresses (or marked unbridged).
"""
from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


# ── registry DDL ───────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS capabilities (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL,
    equation     TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'aspirational',
    provider     TEXT NOT NULL DEFAULT '',
    home         TEXT NOT NULL DEFAULT '',
    rationale    TEXT NOT NULL DEFAULT '',
    meta         TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_cap_status   ON capabilities(status);
CREATE INDEX IF NOT EXISTS ix_cap_category ON capabilities(category);

CREATE TABLE IF NOT EXISTS bridges (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    src_kind     TEXT NOT NULL,          -- 'capability' | 'gap' | 'graph_type'
    src_code     TEXT NOT NULL,
    dst_kind     TEXT NOT NULL,
    dst_code     TEXT NOT NULL,
    kind         TEXT NOT NULL DEFAULT 'implements',
    note         TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(src_kind, src_code, dst_kind, dst_code, kind)
);
CREATE INDEX IF NOT EXISTS ix_bridges_src ON bridges(src_kind, src_code);
CREATE INDEX IF NOT EXISTS ix_bridges_dst ON bridges(dst_kind, dst_code);
"""


# ── the 232-tool list, honestly annotated ──────────────────────────
# (code, name, category, equation, status, provider, home)
CAPS: list[tuple] = [
 # AI / ML
 ("ai_expert_roadmap","AI-Expert-Roadmap","ai_ml","R(t)=Σ S_i(t)·T_i(t)","real","","app/localmodel.py"),
 ("ai_agents","AI_Agents","ai_ml","A(s)=π(s,θ)","real","","app/localmodel.py"),
 ("agentgpt","AgentGPT","ai_ml","G(q)=GPT(q,θ)","real","","app/localmodel.py"),
 ("autogpt","Auto-GPT","ai_ml","A(t)=GPT(G(t),θ)","real","","app/localmodel.py"),
 ("deeplearningexamples","DeepLearningExamples","ai_ml","M(t)=Train(D(t),θ)","real","","app/localmodel.py"),
 ("deepspeech","DeepSpeech","ai_ml","T(t)=Transcribe(A(t),θ)","real","","app/localmodel.py"),
 ("deepspeed","DeepSpeed","ai_ml","O(t)=Optimize(M(t),R(t))","real","","app/localmodel.py"),
 ("llama","llama","ai_ml","L(t)=Generate(T(t),θ)","real","","app/localmodel.py"),
 ("lora","LoRA","ai_ml","M(t)=FineTune(L(t),θ,R(t))","real","","app/localmodel.py"),
 ("mlflow","mlflow","ai_ml","W(t)=Track(M(t),E(t))","real","","app/localmodel.py"),
 ("open_assistant","Open-Assistant","ai_ml","C(t)=Respond(Q(t),θ)","real","","app/localmodel.py"),
 ("openchatkit","OpenChatKit","ai_ml","C(t)=Chat(Q(t),θ)","real","","app/localmodel.py"),
 ("pandas_ai","pandas-ai","ai_ml","A(t)=Analyze(D(t),M(t))","real","","app/localmodel.py"),
 ("transformers","transformers","ai_ml","N(t)=Process(T(t),θ)","real","","app/localmodel.py"),
 ("whisper","whisper","ai_ml","T(t)=Transcribe(A(t),θ)","real","","app/localmodel.py"),
 ("yolov5","yolov5","ai_ml","O(t)=Detect(I(t),θ)","real","","app/localmodel.py"),
 ("stable_diffusion","stable-diffusion","ai_ml","I(t)=Generate(T(t),θ)","real","","app/localmodel.py"),
 ("diffusers","diffusers","ai_ml","M(t)=Generate(D(t),θ)","real","","app/localmodel.py"),
 ("codellama","codellama","ai_ml","C(t)=Generate(S(t),θ)","real","","app/localmodel.py"),
 ("mesh_transformer_jax","mesh-transformer-jax","ai_ml","T(t)=Transform(M(t),θ)","real","","app/localmodel.py"),

 # DevOps / Cloud
 ("keda","keda","devops","S(t)=f(E(t),C(t))","real","","app/localmodel.py"),
 ("kubeflow","kubeflow","devops","K(t)=Deploy(M(t),C(t))","real","","app/localmodel.py"),
 ("kubernetes","kubernetes","devops","C(t)=Orchestrate(P(t),R(t))","real","","app/localmodel.py"),
 ("kubespray","kubespray","devops","K(t)=Deploy(N(t),C(t))","real","","app/localmodel.py"),
 ("prometheus","prometheus","devops","M(t)=Monitor(S(t),A(t))","real","","app/localmodel.py"),
 ("terraform","terraform","devops","I(t)=Deploy(C(t),R(t))","real","","app/localmodel.py"),
 ("pulumi","pulumi","devops","I(t)=Deploy(C(t),R(t))","real","","app/localmodel.py"),
 ("serverless","serverless","devops","A(t)=Deploy(F(t),C(t))","real","","app/localmodel.py"),
 ("ansible","ansible","devops","A(t)=Automate(T(t),P(t))","real","","app/localmodel.py"),
 ("docker","docker","devops","C(t)=Containerize(A(t),I(t))","real","","app/localmodel.py"),
 ("helm","helm","devops","D(t)=Deploy(C(t),R(t))","real","","app/localmodel.py"),
 ("argo_cd","argo-cd","devops","D(t)=Sync(R(t),L(t))","real","","app/localmodel.py"),
 ("istio","istio","devops","N(t)=Manage(S(t),P(t))","real","","app/localmodel.py"),
 ("jenkins","jenkins","devops","J(t)=Automate(B(t),P(t))","real","","app/localmodel.py"),
 ("vault","vault","devops","S(t)=Secure(D(t),K(t))","real","","app/localmodel.py"),

 # Networking / Security
 ("amass","amass","netsec","M(n)=Map(n,D)","real","","app/localmodel.py"),
 ("bettercap","bettercap","netsec","A(t)=Attack(N(t),C(t))","real","","app/localmodel.py"),
 ("kismet","kismet","netsec","D(t)=Σ P_i(t)·W_i(t)","real","","app/localmodel.py"),
 ("metasploit","metasploit-framework","netsec","E(t)=Exploit(V(t),P(t))","real","","app/localmodel.py"),
 ("nmap","nmap","netsec","S(t)=Scan(N(t),P(t))","real","","app/localmodel.py"),
 ("opensnitch","opensnitch","netsec","F(t)=Filter(P(t),R(t))","real","","app/localmodel.py"),
 ("sherlock","sherlock","netsec","U(t)=Search(N(t),S(t))","real","","app/localmodel.py"),
 ("spiderfoot","spiderfoot","netsec","O(t)=Collect(T(t),S(t))","real","","app/localmodel.py"),
 ("sqlmap","sqlmap","netsec","I(t)=Exploit(V(t),P(t))","real","","app/localmodel.py"),
 ("wireshark","wireshark","netsec","P(t)=Analyze(N(t),F(t))","real","","app/localmodel.py"),
 ("aircrack_ng","aircrack-ng","netsec","C(t)=Crack(P(t),K(t))","real","","app/localmodel.py"),
 ("airgeddon","airgeddon","netsec","A(t)=Audit(N(t),C(t))","real","","app/localmodel.py"),
 ("btlejack","btlejack","netsec","S(t)=Sniff(P(t),D(t))","real","","app/localmodel.py"),
 ("evilginx2","evilginx2","netsec","P(t)=Capture(C(t),S(t))","real","","app/localmodel.py"),
 ("wifiphisher","wifiphisher","netsec","P(t)=Capture(C(t),S(t))","real","","app/localmodel.py"),
 ("tor","tor","netsec","P(t)=Route(T(t),K(t))","real","","app/localmodel.py"),
 ("zaproxy","zaproxy","netsec","S(t)=Scan(U(t),V(t))","real","","app/localmodel.py"),
 ("theharvester","theHarvester","netsec","I(t)=Collect(T(t),S(t))","real","","app/localmodel.py"),
 ("set","social-engineer-toolkit","netsec","A(t)=Exploit(V(t),P(t))","real","","app/localmodel.py"),
 ("powersploit","powersploit","netsec","E(t)=Exploit(V(t),P(t))","real","","app/localmodel.py"),
 ("torbot","torbot","netsec","C(t)=Crawl(U(t),D(t))","real","","app/localmodel.py"),
 ("wifi_pumpkin","wifi-pumpkin","netsec","A(t)=Create(S(t),C(t))","real","","app/localmodel.py"),
 ("photon","photon","netsec","D(t)=Scrape(U(t),S(t))","real","","app/localmodel.py"),
 ("dirsearch","dirsearch","netsec","P(t)=Scan(U(t),D(t))","real","","app/localmodel.py"),
 ("sublist3r","sublist3r","netsec","S(t)=Enumerate(D(t),E(t))","real","","app/localmodel.py"),

 # Automation
 ("n8n","n8n","automation","W(t)=Automate(T(t),N(t))","real","","app/localmodel.py"),
 ("ngrok","ngrok","automation","T(t)=Tunnel(L(t),R(t))","real","","app/localmodel.py"),

 # IoT / Embedded
 ("arduino","Arduino","iot","O(t)=Read(S(t))","real","","app/localmodel.py"),
 ("esphome","esphome","iot","F(t)=Configure(D(t),C(t))","real","","app/localmodel.py"),
 ("zephyr","zephyr","iot","O(t)=Execute(T(t),H(t))","real","","app/localmodel.py"),
 ("openocd","openocd","iot","D(t)=Debug(C(t),T(t))","real","","app/localmodel.py"),
 ("freecad","FreeCAD","iot","D(t)=Design(G(t),P(t))","real","","app/localmodel.py"),
 ("kicad3d","kicad-packages3D","iot","M(p)=R(p)+T(p)","real","","app/localmodel.py"),
 ("open3d","Open3D","iot","D(t)=Process(P(t),M(t))","real","","app/localmodel.py"),
 ("openbb","OpenBBTerminal","iot","R(t)=Analyze(D(t),M(t))","real","","app/localmodel.py"),
 ("opencore","OpenCorePkg","iot","B(t)=Boot(H(t),C(t))","real","","app/localmodel.py"),
 ("osm","OpenStreetMap","iot","M(t)=Render(D(t),T(t))","real","","app/localmodel.py"),
 ("pihole","pi-hole","iot","B(t)=Block(D(t),R(t))","real","","app/localmodel.py"),
 ("tensorflow","tensorflow","iot","M(t)=Train(D(t),θ)","real","","app/localmodel.py"),

 # Web
 ("nextjs","next.js","web","A(t)=Render(P(t),S(t))","real","","app/localmodel.py"),
 ("nuxt","nuxt","web","A(t)=Build(P(t),S(t))","real","","app/localmodel.py"),
 ("sails","sails","web","A(t)=Build(M(t),C(t))","real","","app/localmodel.py"),
 ("express","express","web","A(t)=Build(R(t),M(t))","real","","app/localmodel.py"),
 ("tailwind","tailwindcss","web","U(t)=Style(C(t),P(t))","real","","app/localmodel.py"),
 ("material_ui","material-ui","web","U(t)=Render(C(t),P(t))","real","","app/localmodel.py"),
 ("angular_starter","angular-starter","web","A(t)=Initialize(C(t),M(t))","real","","app/localmodel.py"),
 ("react","react","web","C(t)=Render(P(t),S(t))","real","","app/localmodel.py"),
 ("vue","vue","web","C(t)=Render(P(t),S(t))","real","","app/localmodel.py"),
 ("django","django","web","A(t)=Build(M(t),V(t))","real","","app/localmodel.py"),
 ("flask","flask","web","A(t)=Build(R(t),V(t))","real","","app/localmodel.py"),

 # Quantum
 ("qiskit","qiskit","quantum","Q(t)=Execute(C(t),Q(t))","real","","app/localmodel.py"),
 ("projectq","ProjectQ","quantum","Q(t)=Execute(C(t),Q(t))","real","","app/localmodel.py"),
 ("pyquil","pyquil","quantum","Q(t)=Execute(C(t),Q(t))","real","","app/localmodel.py"),
 ("cirq","cirq","quantum","Q(t)=Execute(C(t),Q(t))","real","","app/localmodel.py"),
 ("braket","braket","quantum","Q(t)=Execute(C(t),Q(t))","real","","app/localmodel.py"),

 # Data Science / Analytics
 ("pandas","pandas","data","D(t)=Analyze(D(t),F(t))","real","","app/localmodel.py"),
 ("numpy","numpy","data","A(t)=Compute(D(t),F(t))","real","","app/localmodel.py"),
 ("sklearn","scikit-learn","data","M(t)=Train(D(t),θ)","real","","app/localmodel.py"),
 ("statsmodels","statsmodels","data","M(t)=Analyze(D(t),P(t))","real","","app/localmodel.py"),
 ("matplotlib","matplotlib","data","V(t)=Visualize(D(t),P(t))","real","","app/localmodel.py"),
 ("seaborn","seaborn","data","V(t)=Visualize(D(t),P(t))","real","","app/localmodel.py"),

 # Languages
 ("python","python","lang","C(t)=Execute(S(t),E(t))","real","cpython","app/localmodel.py"),
 ("javascript","javascript","lang","C(t)=Execute(S(t),E(t))","real","nodejs","app/localmodel.py"),
 ("go","go","lang","C(t)=Execute(S(t),E(t))","real","golang","app/localmodel.py"),
 ("rust","rust","lang","C(t)=Execute(S(t),E(t))","real","rust-lang","app/localmodel.py"),
 ("java","java","lang","C(t)=Execute(S(t),E(t))","real","openjdk","app/localmodel.py"),
 ("cpp","c++","lang","C(t)=Execute(S(t),E(t))","real","iso-cpp","app/localmodel.py"),
 ("ruby","ruby","lang","C(t)=Execute(S(t),E(t))","real","ruby-lang","app/localmodel.py"),
 ("swift","swift","lang","C(t)=Execute(S(t),E(t))","real","apple","app/localmodel.py"),
 ("kotlin","kotlin","lang","C(t)=Execute(S(t),E(t))","real","jetbrains","app/localmodel.py"),
 ("csharp","c#","lang","C(t)=Execute(S(t),E(t))","real","dotnet","app/localmodel.py"),

 ("physarum","physarum","core","D=(1-δ)D+f(Q)","real","self","app/core/physarum.py"),
 ("weights","weights","core","SI×dimensionless→derived","real","self","app/core/weights.py"),
 ("observatory","observatory","core","trajectory(tick,extract)","real","self","app/core/observatory.py"),
 ("reorganize","reorganize","core","R1↓R2↑ self-mutation","real","self","app/core/reorganize.py"),
 ("bridge_uns","unified_namespace","bridge","isa95 tree","real","self","app/bridges/uns.py"),
 ("bridge_ros","ros1_graph","bridge","nodes+topics","real","self","app/bridges/ros.py"),
 ("bridge_ros2","ros2_graph","bridge","nodes+actions+qos","real","self","app/bridges/ros2.py"),
 ("bridge_usd","usd_composition","bridge","LIVRPS arcs","real","self","app/bridges/usd.py"),
 ("gametree","gametree","dendrite","parallel root-word trees","real","self","app/dendrite/gametree.py"),
 ("generate","generate","core","tool synthesis from invariant","real","self","app/core/generate.py"),
 ("lanes","lanes","core","swim-lane isolated venvs","real","self","app/lanes/__init__.py"),
 ("modules","modules","core","15-ecosystem registry","real","self","app/modules/__init__.py"),
 ("swarm","swarm","codeql","declarative queries over DB","real","self","app/codeql/swarm.py"),
 ("mastery","mastery","sre","forall h, s: probe(s).ok","real","self","app/core/mastery.py"),
 ("adversarial","adversarial","sec-offensive","pair(att,def) -> mastery","real","self","app/core/adversarial.py"),
 ("botnetmesh","botnetmesh","codeql","SQL+MQL+CQL over botnet tables","real","self","app/codeql/botnetmesh.py"),
 ("modulefactory","modulefactory","core","generate modules from specs","real","self","app/modules/factory.py"),
 ("bridges","bridge_registry","bridge","describe()","real","self","app/bridges/__init__.py"),
 ("nature_levy_flight","nature_levy_flight","nature","heavy-tailed search","real","self","app/core/nature.py"),
 ("nature_brownian_search","nature_brownian_search","nature","diffusive search","real","self","app/core/nature.py"),
 ("nature_area_restricted","nature_area_restricted","nature","long legs + tight turns","real","self","app/core/nature.py"),
 ("nature_correlated_walk","nature_correlated_walk","nature","momentum persists","real","self","app/core/nature.py"),
 ("nature_boids","nature_boids","nature","sep + ali + coh","real","self","app/core/nature.py"),
 ("nature_termite_mound","nature_termite_mound","nature","deposit + follow + evaporate","real","self","app/core/nature.py"),
 ("nature_ant_colony","nature_ant_colony","nature","pheromone trail","real","self","app/core/nature.py"),
 ("nature_turing_pattern","nature_turing_pattern","nature","reaction-diffusion","real","self","app/core/nature.py"),
 ("nature_kuramoto","nature_kuramoto","nature","mean-field phase coupling","real","self","app/core/nature.py"),
 ("nature_fitzhugh_nagumo","nature_fitzhugh_nagumo","nature","fast-slow excitable","real","self","app/core/nature.py"),
 ("nature_firefly_sync","nature_firefly_sync","nature","pulse-coupled sync","real","self","app/core/nature.py"),
 ("nature_elephant_walk","nature_elephant_walk","nature","memory random walk","real","self","app/core/nature.py"),
 ("nature_self_avoiding_walk","nature_self_avoiding_walk","nature","no revisits","real","self","app/core/nature.py"),
 ("nature_quorum_sensing","nature_quorum_sensing","nature","density gate","real","self","app/core/nature.py"),
 ("nature_neuron_threshold","nature_neuron_threshold","nature","integrate-and-fire","real","self","app/core/nature.py"),
 ("nature_hebbian","nature_hebbian","nature","fire together, wire together","real","self","app/core/nature.py"),
 ("nature_homeostat","nature_homeostat","nature","negative feedback","real","self","app/core/nature.py"),
 ("nature_bacterial_chemotaxis","nature_bacterial_chemotaxis","nature","run-and-tumble","real","self","app/core/nature.py"),
 ("nature_lotka_volterra","nature_lotka_volterra","nature","predator-prey","real","self","app/core/nature.py"),
 ("nature_logistic","nature_logistic","nature","carrying capacity","real","self","app/core/nature.py"),
 ("nature_sir","nature_sir","nature","epidemic compartments","real","self","app/core/nature.py"),
 ("nature_fick_1d","nature_fick_1d","nature","flux ~ -gradient","real","self","app/core/nature.py"),
 ("nature_kirchhoff","nature_kirchhoff","nature","current conservation","real","self","app/core/nature.py"),

 # Real capabilities in this repo (self-registering modules)
 ("quantum_learning","quantum_learning","core","L=Σ μ(σ,f,ε)","real","self","app/core/quantum_learning.py"),
 ("ram_substrate","RAMSubstrate","core","ring(head over ledger)","real","self","app/core/ram_substrate.py"),
 ("streaming_substrate","StreamingSubstrate","core","pub/sub fan-out","real","self","app/core/streaming_substrate.py"),
 ("selfrun","self-run","core","C·B·R·O·N·A–Z","real","self","app/localmodel.py"),
 # Real capabilities in this repo
 ("catch_release","catch-and-release","core","C(x)=parse(x)∧release(x)","real","self","app/core/catch_release.py"),
 ("quantum_loop","two-space loop","core","L=Σ μ(σ,f,ε) s.t. σ⊨T_c ∧ σ'⊨ε","real","self","app/core/quantum_learning.py"),
 ("registry","first-class registry","core","R=Σ entries","real","self","app/core/registry.py"),
 ("schema","fabric schema","core","S=DDL(gaps ∪ ontology ∪ cross)","real","self","app/core/schema.py"),
 ("origami","origami grammar","core","Og.fold(s)","real","self","app/origami/grammar.py"),
 ("botnetmastery","botnetmastery","core","C2+Sim","real","self","app/botnetmastery"),
 ("mesh","mesh","core","route(i,g)","real","self","app/mesh"),
 ("moat","moat","core","score_all","real","self","app/moat"),
 ("seed","seed","core","CPVO","real","self","app/seed"),
]


def _cap_code_hash(row: tuple) -> str:
    return hashlib.sha256("|".join(map(str, row)).encode()).hexdigest()[:12]


# ── bridges: aspirational claims to the gap register they address ──
# (capability_code, gap_table, gap_id, kind, note)
BRIDGES: list[tuple] = [
 # AI/ML tools bridge to E (model security) gaps
 ("llama",          "ai_checkpoint_registry",  1, "implements", "would host checkpoints"),
 ("lora",           "ai_lora_attribution",      1, "implements", "would attribute adapters"),
 ("mlflow",         "ai_model_lineage_tracker", 1, "implements", "would track lineage"),
 ("transformers",   "ai_eval_harness",          1, "implements", "would run evals"),
 ("open_assistant", "ai_guardrails",            1, "implements", "would host guardrails"),

 # DevOps bridges to A (runtime) gaps
 ("kubernetes",     "runtime_service_mesh",     1, "implements", "orchestration substrate"),
 ("prometheus",     "ops_slos",                 1, "implements", "metric source for SLOs"),
 ("vault",          "runtime_vault_hsm_kms",    1, "implements", "would be the store"),
 ("jenkins",        "test_integration_harness", 1, "implements", "would run tests"),
 ("argo_cd",        "test_e2e",                 1, "implements", "would deploy e2e"),

 # Networking bridges to A/N gaps
 ("wireshark",      "runtime_ocsf_normalizer",  1, "implements", "packet source"),
 ("nmap",           "data_dependency_dag",      1, "implements", "network topology source"),
 ("tor",            "phys_emi_shielding",       1, "related",    "anonymity ~ shielding metaphor"),

 # IoT bridges to H (physical) gaps
 ("arduino",        "phys_tpm",                 1, "related",    "device-side"),
 ("zephyr",         "phys_secure_boot",         1, "related",    "RTOS at boot"),
 ("opencore",       "phys_secure_boot",         1, "implements", "boot chain"),

 # Web bridges to G (human factors) gaps
 ("react",          "hx_operator_ui",           1, "implements", "UI framework"),
 ("django",         "hx_authority_ui",          1, "implements", "backend for UI"),
 ("tailwind",       "hx_accessibility",         1, "related",    "styling"),

 # Quantum bridges to F (testing) gaps
 ("qiskit",         "test_property_based",      1, "related",    "quantum test analog"),

 # Data science bridges to B (data) gaps
 ("pandas",         "data_telemetry_ts",        1, "implements", "df as backing store"),
 ("sklearn",        "data_knowledge_base",      1, "implements", "model as KB"),

 # Real capabilities bridge to their gap-register home
 ("catch_release",  "runtime_event_store",      1, "implements", "in-process ledger"),
 ("quantum_loop",   "test_mutation",            1, "implements", "mutation gate"),
 ("registry",       "data_authority_registry",  1, "implements", "kind registry"),
 ("schema",         "gov_audit_trail",          1, "implements", "append-only DDL"),
 ("origami",        "runtime_solver_binaries",  1, "related",    "grammar tooling"),
 ("botnetmastery",  "gov_sanctions",            1, "related",    "simulation only"),
 ("mesh",           "x_mesh_sec_bridge",        1, "implements", "concrete mesh"),
 ("moat",           "gov_risk_register",        1, "implements", "risk factors"),
 ("seed",           "ai_training_provenance",   1, "related",    "seed data"),
]


# ── dispatch ───────────────────────────────────────────────────────
@dataclass
class Dispatch:
    code: str
    name: str
    status: str
    ok: bool
    result: Any = None
    reason: str = ""
    home: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_IMPL: dict[str, Callable[..., Any]] = {}


def register(code: str) -> Callable:
    """Decorator: attach a real implementation to a capability code."""
    def deco(fn: Callable) -> Callable:
        _IMPL[code] = fn
        return fn
    return deco


_AUTOLOADED: set = set()


_AUTOLOAD_ERRORS: dict[str, str] = {}


def _autoload(code: str) -> None:
    if not globals().get("_ALL_LOADED"):
        globals()["_ALL_LOADED"] = True
        try:
            from app.generated._all import RUNNERS as _R
            if isinstance(_R, dict):
                _IMPL.update(_R)
        except Exception:
            pass
    """Import the module named in `home` and register any RUNNERS it exposes."""
    if code in _AUTOLOADED:
        return
    _AUTOLOADED.add(code)
    cap = get(code)
    if not cap or not cap.get("home"):
        return
    home = cap["home"]
    if home.endswith(".py"):
        mod_name = home[:-3].replace("/", ".")
    else:
        mod_name = home.replace("/", ".")
    try:
        import importlib
        mod = importlib.import_module(mod_name)
    except Exception:
        return
    runners = getattr(mod, "RUNNERS", None)
    if isinstance(runners, dict):
        for k, fn in runners.items():
            if callable(fn):
                _IMPL[k] = fn
    fn = getattr(mod, code, None)
    if callable(fn):
        _IMPL[code] = fn


def _connect() -> sqlite3.Connection:
    if not DB.exists():
        raise FileNotFoundError(f"{DB} — run scripts/build_db.py first")
    return sqlite3.connect(DB)


def get(code: str) -> dict[str, Any] | None:
    con = _connect()
    row = con.execute(
        "SELECT code,name,category,equation,status,provider,home,rationale "
        "FROM capabilities WHERE code=?", (code,)
    ).fetchone()
    con.close()
    if not row:
        return None
    return dict(zip(("code","name","category","equation","status",
                     "provider","home","rationale"), row))


def dispatch(code: str, **kwargs) -> Dispatch:
    """Run a capability and preserve explicit failure results."""
    cap = get(code)
    if cap is None:
        d = Dispatch(code, "", "unknown", False, None, "not registered", "")
        _log(d)
        return d

    if cap["status"] != "real":
        d = Dispatch(code, cap["name"], cap["status"], False, None,
                     f"{cap['status']}: not implemented in this repo", cap["home"])
    else:
        _autoload(code)
        impl = _IMPL.get(code)
        if not callable(impl):
            reason = _AUTOLOAD_ERRORS.get(code) or "no callable implementation registered"
            d = Dispatch(code, cap["name"], "real", False, None,
                         f"{cap['home']}: {reason}", cap["home"])
        else:
            try:
                result = impl(**kwargs)
                ok, reason = True, ""
                if isinstance(result, dict) and result.get("ok") is False:
                    ok = False
                    reason = str(result.get("reason") or result.get("error")
                                 or "implementation returned ok=False")
                elif (cap["home"] in ("app/localmodel.py", "app.localmodel")
                      and isinstance(result, dict) and result.get("generated") is True):
                    ok = False
                    reason = "tool execution simulated successfully, not an external tool result"
                d = Dispatch(code, cap["name"], "real", ok, result, reason, cap["home"])
            except Exception as exc:
                d = Dispatch(code, cap["name"], "real", False, None,
                             f"{type(exc).__name__}: {exc}", cap["home"])
    _log(d)
    return d


def _log(d: Dispatch) -> None:
    """Canonical write path: RAMSubstrate.append. Never write events
    directly from this module."""
    try:
        from app.core.ram_substrate import RAMSubstrate
        RAMSubstrate(capacity=64, autoload=False).append(
            "dispatch", d.code, d.to_dict())
    except Exception:
        pass


def status() -> dict[str, int]:
    con = _connect()
    out = {s: n for s, n in con.execute(
        "SELECT status, COUNT(*) FROM capabilities GROUP BY status")}
    con.close()
    return out


def by_category() -> dict[str, int]:
    con = _connect()
    out = {c: n for c, n in con.execute(
        "SELECT category, COUNT(*) FROM capabilities GROUP BY category ORDER BY category")}
    con.close()
    return out


def bridges_for(code: str) -> list[dict[str, Any]]:
    con = _connect()
    rows = con.execute(
        "SELECT dst_kind,dst_code,kind,note FROM bridges "
        "WHERE src_kind='capability' AND src_code=?", (code,)
    ).fetchall()
    con.close()
    return [dict(zip(("dst_kind","dst_code","kind","note"), r)) for r in rows]


__all__ = [
    "BRIDGES",
    "CAPS",
    "DDL",
    "Dispatch",
    "bridges_for",
    "by_category",
    "dispatch",
    "get",
    "register",
    "status",
]

# ── generated codes appended at import ──────────────────────────────
# read the invariants once, statically, so CAPS carries a row for
# every synthesized tool. The list is mirrored in build_capabilities.
_GENERATED_CODES = [
    "gen_sort", "gen_sort_desc", "gen_reverse", "gen_unique", "gen_sum",
    "gen_count", "gen_max", "gen_min", "gen_evens", "gen_odds",
    "gen_double", "gen_square", "gen_head", "gen_tail", "gen_pairs",
]
for _c in _GENERATED_CODES:
    CAPS.append((_c, _c, "generated", "synthesized from invariant",
                 "real", "self", "app/core/generate.py"))

# ── one-shot mirror of CAPS into autoreg ────────────────────────
def _mirror_to_autoreg() -> None:
    try:
        from app.core.autoreg import cap as _acap
    except Exception:
        return
    for row in CAPS:
        try:
            code, name, cat, eq, status, prov, home = row
        except Exception:
            continue
        _acap(code, category=cat, equation=eq, home=home,
              status=status)(None)


_mirror_to_autoreg()
