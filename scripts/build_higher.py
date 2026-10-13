#!/usr/bin/env python3
"""Highest levels of the fabric: graph-type ontology, authority chain,
approvals, attestations, SPARSE checkpoints, knowledge-graph edges,
and the fixed-point top that hashes the whole thing.

Levels
  L0  events                  (already present, append-only chain)
  L1  graph_types             ontology of every graph kind listed
  L2  authority               named humans + delegation chain
  L3  approval                decisions with residual-risk acceptance
  L4  attestation             signatures over individual subjects
  L5  sparse_checkpoint       Merkle roots over event ranges, sparse mode
  L6  kg_edge                 typed edges over every table above
  L7  fabric_top              one row: hash of everything else + itself
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "fabric.sqlite3"


# ── L1: graph types. (code, label, family, directed, acyclic, hyper, bipartite)
GRAPH_TYPES = [
    ("DAG","Directed Acyclic Graph","structural",1,1,0,0),
    ("DCG","Directed Cyclic Graph","structural",1,0,0,0),
    ("UDAG","Undirected Acyclic Graph","structural",0,1,0,0),
    ("UG","Undirected Graph","structural",0,None,0,0),
    ("DG","Directed Graph","structural",1,None,0,0),
    ("MDAG","Mixed Directed Acyclic Graph","structural",1,1,0,0),
    ("PDAG","Partially Directed Acyclic Graph","structural",1,1,0,0),
    ("CPDAG","Completed Partially Directed Acyclic Graph","structural",1,1,0,0),
    ("ADMG","Acyclic Directed Mixed Graph","structural",1,1,0,0),
    ("MAG","Maximal Ancestral Graph","structural",1,1,0,0),
    ("PAG","Partial Ancestral Graph","structural",1,1,0,0),
    ("CG","Chain Graph","structural",None,None,0,0),
    ("FG","Factor Graph","probabilistic",0,1,0,1),
    ("HG","Hypergraph","structural",None,None,1,0),
    ("DHG","Directed Hypergraph","structural",1,None,1,0),
    ("BG","Bipartite Graph","structural",0,None,0,1),
    ("MPG","Multipartite Graph","structural",0,None,0,0),
    ("Kn","Complete Graph","structural",None,None,0,0),
    ("Null","Null Graph","structural",None,None,0,0),
    ("Tree","Tree (Rooted / Unrooted)","structural",1,1,0,0),
    ("Forest","Forest","structural",1,1,0,0),
    ("Arborescence","Arborescence","structural",1,1,0,0),
    ("Polytree","Polytree","structural",1,1,0,0),
    ("SPG","Series-Parallel Graph","structural",0,None,0,0),
    ("Planar","Planar Graph","structural",0,None,0,0),
    ("Dual","Dual Graph","structural",0,None,0,0),
    ("Line","Line Graph","structural",0,None,0,0),
    ("Clique","Clique Graph","structural",0,None,0,0),
    ("Intersection","Intersection Graph","structural",0,None,0,0),
    ("Interval","Interval Graph","structural",0,None,0,0),
    ("Chordal","Chordal Graph","structural",0,1,0,0),
    ("CircularArc","Circular-Arc Graph","structural",0,None,0,0),
    ("Permutation","Permutation Graph","structural",0,None,0,0),
    ("Comparability","Comparability Graph","structural",0,None,0,0),
    ("CoComparability","Co-comparability Graph","structural",0,None,0,0),
    ("Distance","Distance Graph","structural",0,None,0,0),
    ("UnitDisk","Unit Disk Graph","geometric",0,None,0,0),
    ("Geometric","Geometric Graph","geometric",0,None,0,0),
    ("ErdosRenyi","Random Graph (Erdős–Rényi)","random",0,None,0,0),
    ("SmallWorld","Small-World Graph","random",0,None,0,0),
    ("ScaleFree","Scale-Free Graph","random",0,None,0,0),
    ("Expander","Expander Graph","random",0,None,0,0),
    ("Cayley","Cayley Graph","algebraic",1,None,0,0),
    ("DeBruijn","De Bruijn Graph","algebraic",1,None,0,0),
    ("Kautz","Kautz Graph","algebraic",1,None,0,0),
    ("Hypercube","Hypercube Graph","algebraic",0,None,0,0),
    ("Grid","Grid Graph","geometric",0,None,0,0),
    ("Lattice","Lattice Graph","geometric",0,None,0,0),
    ("TensorProduct","Tensor Product Graph","product",0,None,0,0),
    ("CartesianProduct","Cartesian Product Graph","product",0,None,0,0),
    ("StrongProduct","Strong Product Graph","product",0,None,0,0),
    ("LexProduct","Lexicographic Product Graph","product",0,None,0,0),
    ("FlowNetwork","Flow Network","flow",1,None,0,0),
    ("Residual","Residual Graph","flow",1,None,0,0),
    ("StateTransition","State Transition Graph","dynamical",1,None,0,0),
    ("CFG","Control Flow Graph","program",1,None,0,0),
    ("DFG","Data Flow Graph","program",1,1,0,0),
    ("PDG","Program Dependence Graph","program",1,1,0,0),
    ("SDG","System Dependence Graph","program",1,1,0,0),
    ("CallGraph","Call Graph","program",1,None,0,0),
    ("Interprocedural","Interprocedural Graph","program",1,None,0,0),
    ("Execution","Execution Graph","program",1,1,0,0),
    ("Task","Task Graph","execution",1,1,0,0),
    ("Job","Job Graph","execution",1,1,0,0),
    ("Workflow","Workflow Graph","execution",1,1,0,0),
    ("Build","Build Graph","execution",1,1,0,0),
    ("Dependency","Dependency Graph","execution",1,1,0,0),
    ("KG","Knowledge Graph","semantic",1,0,0,0),
    ("Semantic","Semantic Graph","semantic",1,0,0,0),
    ("Property","Property Graph","semantic",1,0,0,0),
    ("Labeled","Labeled Graph","semantic",None,None,0,0),
    ("Attributed","Attributed Graph","semantic",None,None,0,0),
    ("Heterogeneous","Heterogeneous Graph","semantic",None,None,0,0),
    ("Homogeneous","Homogeneous Graph","semantic",None,None,0,0),
    ("Dynamic","Dynamic Graph","temporal",None,None,0,0),
    ("Temporal","Temporal Graph","temporal",None,None,0,0),
    ("Streaming","Streaming Graph","temporal",None,None,0,0),
    ("Probabilistic","Probabilistic Graph","probabilistic",None,None,0,0),
    ("BN","Bayesian Network","probabilistic",1,1,0,0),
    ("MRF","Markov Random Field","probabilistic",0,None,0,0),
    ("CRF","Conditional Random Field","probabilistic",0,None,0,0),
    ("InfluenceDiagram","Influence Diagram","probabilistic",1,1,0,0),
    ("Causal","Causal Graph","causal",1,1,0,0),
    ("SCM","Structural Causal Model Graph","causal",1,1,0,0),
    ("AndOr","And-Or Graph","ai",1,1,0,0),
    ("Scene","Scene Graph","ai",1,1,0,0),
    ("Concept","Concept Graph","ai",1,0,0,0),
    ("OntologyGraph","Ontology Graph","ai",1,0,0,0),
    ("Event","Event Graph","ai",1,0,0,0),
    ("Interaction","Interaction Graph","ai",0,None,0,0),
    ("Social","Social Graph","ai",0,None,0,0),
    ("Communication","Communication Graph","ai",0,None,0,0),
    ("NetworkTopology","Network Topology Graph","network",0,None,0,0),
    ("Routing","Routing Graph","network",1,None,0,0),
    ("Overlay","Overlay Network Graph","network",0,None,0,0),
    ("P2P","Peer-to-Peer Graph","network",0,None,0,0),
    ("Blockchain","Blockchain Graph (Transaction Graph)","network",1,1,0,0),
    ("MerkleDAG","Merkle DAG","content",1,1,0,0),
    ("ContentAddressable","Content-Addressable Graph","content",1,1,0,0),
    ("VCS","Version Control Graph (Git DAG)","content",1,1,0,0),
    ("Computation","Computation Graph (Autograd Graph)","ai",1,1,0,0),
    ("Tensor","Tensor Graph","ai",1,1,0,0),
    ("NN","Neural Network Graph","ai",1,1,0,0),
    ("Attention","Attention Graph","ai",1,1,0,0),
    ("MessagePassing","Message Passing Graph","ai",1,1,0,0),
    ("GNN","Graph Neural Network (GNN Graph)","ai",1,1,0,0),
    ("Factorization","Factorization Graph","algebraic",0,None,0,1),
    ("Constraint","Constraint Graph","constraint",0,None,0,0),
    ("SAT","SAT Graph","constraint",0,None,0,0),
    ("ClauseVariable","Clause-Variable Graph","constraint",0,None,0,1),
    ("Search","Search Graph","search",1,None,0,0),
    ("GameTree","Game Tree (Game Graph)","search",1,1,0,0),
    ("Minimax","Minimax Graph","search",1,1,0,0),
    ("MCTS","Monte Carlo Tree Graph","search",1,1,0,0),
    ("Proof","Proof Graph","logic",1,1,0,0),
    ("Inference","Inference Graph","logic",1,1,0,0),
    ("Resolution","Resolution Graph","logic",1,1,0,0),
    ("Rewrite","Rewrite Graph","logic",1,None,0,0),
    ("Term","Term Graph","logic",1,None,0,0),
    ("CatDiagram","Category-Theoretic Graph (Diagram)","category",1,None,0,0),
    ("Functor","Functor Graph","category",1,None,0,0),
    ("Morphism","Morphism Graph","category",1,None,0,0),
    ("Sheaf","Sheaf Graph","category",1,None,0,0),
    ("FiberBundle","Fiber Bundle Graph","category",1,None,0,0),
    ("Topological","Topological Graph","topology",0,None,0,0),
    ("SimplicialComplex","Simplicial Complex","topology",0,None,1,0),
    ("CellComplex","Cell Complex","topology",0,None,1,0),
    ("CWComplex","CW Complex","topology",0,None,1,0),
    ("Nerve","Nerve Graph","topology",0,None,0,0),
    ("Reeb","Reeb Graph","topology",1,1,0,0),
    ("Mapper","Mapper Graph","topology",0,None,0,0),
    ("Persistence","Persistence Graph","topology",1,1,0,0),
    ("Spectral","Spectral Graph","spectral",0,None,0,0),
    ("Laplacian","Laplacian Graph","spectral",0,None,0,0),
    ("Energy","Energy Graph","spectral",0,None,0,0),
    ("InteractionEnergy","Interaction Energy Graph","spectral",0,None,0,0),
    ("FlowField","Flow Field Graph","field",1,None,0,0),
    ("VectorField","Vector Field Graph","field",1,None,0,0),
    ("PhaseSpace","Phase Space Graph","dynamical",1,None,0,0),
    ("StateSpace","State Space Graph","dynamical",1,None,0,0),
    ("Attractor","Attractor Graph","dynamical",1,None,0,0),
    ("TransitionSystem","Transition System Graph","dynamical",1,None,0,0),
    ("Kripke","Kripke Structure","dynamical",1,None,0,0),
    ("Petri","Petri Net","dynamical",1,None,1,1),
    ("ColoredPetri","Colored Petri Net","dynamical",1,None,1,1),
    ("TimedPetri","Timed Petri Net","dynamical",1,None,1,1),
    ("SignalFlow","Signal Flow Graph","hardware",1,1,0,0),
    ("BlockDiagram","Block Diagram Graph","hardware",1,1,0,0),
    ("Circuit","Circuit Graph","hardware",1,1,0,0),
    ("Netlist","Netlist Graph","hardware",1,1,0,0),
    ("Timing","Timing Graph","hardware",1,1,0,0),
    ("Placement","Placement Graph","hardware",0,None,0,0),
    ("RoutingResource","Routing Resource Graph","hardware",0,None,0,0),
    ("PowerGrid","Power Grid Graph","hardware",0,None,0,0),
    ("ClockTree","Clock Tree Graph","hardware",1,1,0,0),
    ("HardwareDep","Hardware Dependency Graph","hardware",1,1,0,0),
    ("NoC","NoC Graph","hardware",0,None,0,0),
    ("Interconnect","Interconnect Graph","hardware",0,None,0,0),
    ("GPUTask","GPU Task Graph","hardware",1,1,0,0),
    ("CUDA","CUDA Graph","hardware",1,1,0,0),
    ("KernelDep","Kernel Dependency Graph","hardware",1,1,0,0),
    ("MemoryAccess","Memory Access Graph","hardware",1,None,0,0),
    ("CacheCoherence","Cache Coherence Graph","hardware",0,None,0,0),
    ("IO","IO Graph","hardware",1,None,0,0),
    ("Filesystem","Filesystem Graph","memory",1,1,0,0),
    ("DirectoryTree","Directory Tree","memory",1,1,0,0),
    ("Object","Object Graph","memory",1,None,0,0),
    ("Heap","Heap Graph","memory",1,None,0,0),
    ("Reference","Reference Graph","memory",1,None,0,0),
    ("Pointer","Pointer Graph","memory",1,None,0,0),
    ("Alias","Alias Graph","memory",0,None,0,0),
    ("Ownership","Ownership Graph","memory",1,1,0,0),
    ("Borrow","Borrow Graph","memory",1,1,0,0),
    ("Region","Region Graph","memory",1,1,0,0),
    ("Lifetime","Lifetime Graph","memory",1,1,0,0),
    ("Version","Version Graph","content",1,1,0,0),
    ("Diff","Diff Graph","content",1,1,0,0),
    ("Patch","Patch Graph","content",1,1,0,0),
    ("Merge","Merge Graph","content",1,1,0,0),
    ("Conflict","Conflict Graph","content",0,None,0,0),
    ("Cluster","Cluster Graph","cluster",0,None,0,0),
    ("Partition","Partition Graph","cluster",0,None,0,0),
    ("Community","Community Graph","cluster",0,None,0,0),
    ("Affinity","Affinity Graph","cluster",0,None,0,0),
    ("Similarity","Similarity Graph","cluster",0,None,0,0),
    ("DistanceMatrix","Distance Matrix Graph","cluster",0,None,0,1),
    ("kNN","k-NN Graph","cluster",1,None,0,0),
    ("Epsilon","ε-Graph","cluster",0,None,0,0),
    ("Delaunay","Delaunay Graph","geometric",0,None,0,0),
    ("Voronoi","Voronoi Graph","geometric",0,None,0,0),
    ("SpanningTree","Spanning Tree (MST Graph)","opt",0,1,0,0),
    ("ShortestPathTree","Shortest Path Tree","opt",1,1,0,0),
    ("Cut","Cut Graph","opt",0,None,0,0),
    ("Matching","Matching Graph","opt",0,None,0,0),
    ("Flow","Flow Graph","opt",1,None,0,0),
    ("ResidualCap","Residual Capacity Graph","opt",1,None,0,0),
    ("AugmentingPath","Augmenting Path Graph","opt",1,None,0,0),
    ("DualFlow","Dual Flow Graph","opt",1,None,0,0),
    ("Transportation","Transportation Graph","supply",1,None,0,1),
    ("SupplyChain","Supply Chain Graph","supply",1,1,0,0),
    ("Logistics","Logistics Graph","supply",1,1,0,0),
    ("Process","Process Graph","supply",1,1,0,0),
    ("Manufacturing","Manufacturing Graph","supply",1,1,0,0),
    ("ResourceAlloc","Resource Allocation Graph","systems",1,None,0,1),
    ("Deadlock","Deadlock Graph","systems",1,None,0,0),
    ("WaitFor","Wait-for Graph","systems",1,None,0,0),
    ("Scheduling","Scheduling Graph","systems",1,1,0,0),
    ("Timeline","Timeline Graph","systems",1,1,0,0),
    ("Gantt","Gantt Graph","systems",1,1,0,0),
    ("Precedence","Precedence Graph","systems",1,1,0,0),
    ("CSP","Constraint Satisfaction Graph","systems",0,None,0,0),
    ("DepResolution","Dependency Resolution Graph","systems",1,1,0,0),
    ("ExecutionPlan","Execution Plan Graph","systems",1,1,0,0),
    ("QueryPlan","Query Plan Graph","systems",1,1,0,0),
    ("RelAlgebra","Relational Algebra Graph","systems",1,1,0,0),
    ("Join","Join Graph","systems",0,None,0,0),
    ("Index","Index Graph","systems",1,1,0,0),
    ("DataLineage","Data Lineage Graph","data",1,1,0,0),
    ("ETL","ETL Graph","data",1,1,0,0),
    ("Pipeline","Pipeline Graph","data",1,1,0,0),
    ("FeatureStore","Feature Store Graph","data",1,1,0,0),
    ("Embedding","Embedding Graph","data",0,None,0,0),
    ("VectorIndex","Vector Index Graph","data",0,None,0,0),
    ("Retrieval","Retrieval Graph","data",1,None,0,0),
    ("RAG","RAG Graph","data",1,None,0,0),
    ("Agent","Agent Graph","agent",1,1,0,0),
    ("Tool","Tool Graph","agent",1,1,0,0),
    ("Policy","Policy Graph","agent",1,1,0,0),
    ("Reward","Reward Graph","agent",0,None,0,0),
    ("Value","Value Graph","agent",0,None,0,0),
    ("Decision","Decision Graph","agent",1,1,0,0),
    ("InfluenceNetwork","Influence Network","agent",1,1,0,0),
    ("Belief","Belief Graph","agent",0,None,0,0),
    ("Uncertainty","Uncertainty Graph","agent",0,None,0,0),
    ("Risk","Risk Graph","security",1,1,0,0),
    ("Attack","Attack Graph","security",1,1,0,0),
    ("Threat","Threat Graph","security",1,1,0,0),
    ("Trust","Trust Graph","security",1,None,0,0),
    ("Reputation","Reputation Graph","security",0,None,0,0),
    ("AccessControl","Access Control Graph","security",1,1,0,0),
    ("Permission","Permission Graph","security",1,1,0,0),
    ("Identity","Identity Graph","security",0,None,0,0),
    ("Federation","Federation Graph","security",0,None,0,0),
    ("Compliance","Compliance Graph","security",1,1,0,0),
    ("Audit","Audit Graph","security",1,1,0,0),
    ("Provenance","Provenance Graph","security",1,1,0,0),
    ("Trace","Trace Graph","observability",1,1,0,0),
    ("Telemetry","Telemetry Graph","observability",1,1,0,0),
    ("Observability","Observability Graph","observability",1,1,0,0),
    ("Metric","Metric Graph","observability",0,None,0,0),
    ("Log","Log Graph","observability",1,None,0,0),
    ("EventStream","Event Stream Graph","observability",1,None,0,0),
    ("CausalEvent","Causal Event Graph","observability",1,1,0,0),
    ("TemporalCausal","Temporal Causal Graph","observability",1,1,0,0),
    ("SpatioTemporal","Spatio-Temporal Graph","observability",None,None,0,0),
    ("Mobility","Mobility Graph","physical",1,None,0,0),
    ("Traffic","Traffic Graph","physical",1,None,0,0),
    ("TransportNetwork","Transportation Network Graph","physical",1,None,0,0),
    ("Infrastructure","Infrastructure Graph","physical",0,None,0,0),
    ("UtilityGrid","Utility Grid Graph","physical",0,None,0,0),
    ("PowerNetwork","Power Network Graph","physical",0,None,0,0),
    ("WaterNetwork","Water Network Graph","physical",0,None,0,0),
    ("CommNetwork","Communication Network Graph","physical",0,None,0,0),
    ("Internet","Internet Graph","physical",0,None,0,0),
    ("ASLevel","AS-Level Graph","physical",0,None,0,0),
    ("RouterLevel","Router-Level Graph","physical",0,None,0,0),
    ("Wireless","Wireless Network Graph","physical",0,None,0,0),
    ("Sensor","Sensor Network Graph","physical",0,None,0,0),
    ("IoT","IoT Graph","physical",0,None,0,0),
    ("Swarm","Swarm Graph","physical",0,None,0,0),
    ("MultiAgent","Multi-Agent Interaction Graph","physical",0,None,0,0),
    ("Coordination","Coordination Graph","physical",0,None,0,0),
    ("Coalition","Coalition Graph","physical",0,None,0,0),
    ("GameTheoretic","Game-Theoretic Graph","physical",0,None,0,0),
    ("Market","Market Graph","economics",1,None,0,1),
    ("Economic","Economic Graph","economics",1,None,0,0),
    ("Trade","Trade Graph","economics",1,None,0,0),
    ("FinancialTxn","Financial Transaction Graph","economics",1,None,0,0),
    ("Payment","Payment Graph","economics",1,None,0,0),
    ("Credit","Credit Graph","economics",0,None,0,0),
    ("Fraud","Fraud Graph","economics",1,None,0,0),
    ("SupplyDemand","Supply-Demand Graph","economics",0,None,0,1),
    ("MatchingMarket","Matching Market Graph","economics",0,None,0,1),
    ("Auction","Auction Graph","economics",0,None,0,1),
    ("OrderBook","Order Book Graph","economics",0,None,0,0),
    ("Price","Price Graph","economics",0,None,0,0),
    ("Signal","Signal Graph","signal",1,None,0,0),
    ("TimeSeries","Time Series Graph","signal",1,None,0,0),
    ("Correlation","Correlation Graph","signal",0,None,0,0),
    ("Causation","Causation Graph","signal",1,1,0,0),
    ("Granger","Granger Graph","signal",1,1,0,0),
    ("TransferEntropy","Transfer Entropy Graph","signal",1,None,0,0),
    ("InfoFlow","Information Flow Graph","signal",1,None,0,0),
    ("Entropy","Entropy Graph","signal",0,None,0,0),
    ("MutualInfo","Mutual Information Graph","signal",0,None,0,0),
    ("Compression","Compression Graph","signal",1,1,0,0),
    ("Coding","Coding Graph","signal",1,1,0,0),
    ("ErrorCorrecting","Error-Correcting Graph","signal",1,1,0,0),
    ("Tanner","Tanner Graph","signal",0,None,0,1),
    ("LDPC","LDPC Graph","signal",0,None,0,1),
    ("Turbo","Turbo Graph","signal",0,None,0,1),
    ("QuantumCircuit","Quantum Circuit Graph","quantum",1,1,0,0),
    ("TensorNetwork","Tensor Network Graph","quantum",0,None,1,0),
    ("ZXCalculus","ZX-Calculus Graph","quantum",1,None,1,0),
    ("QuantumInteraction","Quantum Interaction Graph","quantum",0,None,0,0),
    ("Entanglement","Entanglement Graph","quantum",0,None,0,0),
    ("Measurement","Measurement Graph","quantum",1,None,0,0),
    ("Stabilizer","Stabilizer Graph","quantum",1,1,0,0),
    ("QuantumError","Quantum Error Graph","quantum",0,None,0,0),
    ("SpinNetwork","Spin Network","quantum",0,None,0,0),
    ("CausalSet","Causal Set","quantum",1,1,0,0),
    ("ProcessNetwork","Process Network","quantum",1,None,0,0),
    ("Reaction","Reaction Graph","chemical",1,1,0,0),
    ("Molecular","Molecular Graph","chemical",0,None,0,0),
    ("ChemReactionNetwork","Chemical Reaction Network","chemical",1,1,0,0),
    ("Metabolic","Metabolic Network","biological",1,1,0,0),
    ("GeneRegulatory","Gene Regulatory Network","biological",1,1,0,0),
    ("ProteinInteraction","Protein Interaction Graph","biological",0,None,0,0),
    ("Connectome","Neural Connectome Graph","biological",1,None,0,0),
    ("BrainNetwork","Brain Network Graph","biological",0,None,0,0),
    ("Cognitive","Cognitive Graph","semantic",1,0,0,0),
    ("Conceptual","Conceptual Graph","semantic",1,0,0,0),
    ("Language","Language Graph","semantic",1,0,0,0),
    ("SyntaxTree","Syntax Tree (Parse Graph)","linguistic",1,1,0,0),
    ("DependencyParse","Dependency Parse Graph","linguistic",1,1,0,0),
    ("SemanticRole","Semantic Role Graph","linguistic",1,1,0,0),
    ("Coreference","Coreference Graph","linguistic",0,None,0,0),
    ("Discourse","Discourse Graph","linguistic",1,1,0,0),
    ("KRGraph","Knowledge Representation Graph","semantic",1,0,0,0),
]

LEVELS_DDL = """
-- ── L1 graph-type ontology ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS graph_types (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT NOT NULL UNIQUE,
    label        TEXT NOT NULL,
    family       TEXT NOT NULL,
    directed     INTEGER,
    acyclic      INTEGER,
    hyper        INTEGER NOT NULL DEFAULT 0,
    bipartite    INTEGER NOT NULL DEFAULT 0,
    meta         TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_graph_types_family ON graph_types(family);

-- ── L2 authority: named humans + delegation chain ─────────────
CREATE TABLE IF NOT EXISTS authority (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    code           TEXT NOT NULL UNIQUE,
    name           TEXT NOT NULL,          -- named human, not a role
    role           TEXT NOT NULL,
    delegated_from INTEGER REFERENCES authority(id),
    scope          TEXT NOT NULL DEFAULT 'global',
    valid_from     TEXT NOT NULL DEFAULT (datetime('now')),
    valid_to       TEXT,
    meta           TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS authority_key (
    authority_id INTEGER PRIMARY KEY REFERENCES authority(id),
    alg          TEXT NOT NULL DEFAULT 'hmac-sha256',
    key_hex      TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ── L3 approval ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS approval (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT NOT NULL UNIQUE,
    authority_id  INTEGER NOT NULL REFERENCES authority(id),
    subject_table TEXT NOT NULL,
    subject_id    INTEGER NOT NULL,
    decision      TEXT NOT NULL,   -- approve|reject|waive|abstain
    rationale     TEXT,
    residual_risk REAL,            -- required for waive
    decided_at    TEXT NOT NULL DEFAULT (datetime('now')),
    meta          TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_approval_subject ON approval(subject_table, subject_id);

-- ── L4 attestation ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attestation (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT NOT NULL UNIQUE,
    subject_table TEXT NOT NULL,
    subject_id    INTEGER NOT NULL,
    payload_hash  TEXT NOT NULL,
    signer_id     INTEGER NOT NULL REFERENCES authority(id),
    alg           TEXT NOT NULL DEFAULT 'hmac-sha256',
    signature     TEXT NOT NULL,
    issued_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_attestation_subject ON attestation(subject_table, subject_id);

-- ── L5 SPARSE checkpoint ─────────────────────────────────────
-- mode='contiguous' attests the whole [seq_lo,seq_hi] range.
-- mode='sparse'     attests a subset, listed in covered_seqs JSON.
CREATE TABLE IF NOT EXISTS sparse_checkpoint (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT NOT NULL UNIQUE,
    mode          TEXT NOT NULL DEFAULT 'contiguous',
    seq_lo        INTEGER NOT NULL,
    seq_hi        INTEGER NOT NULL,
    covered_seqs  TEXT,                 -- JSON list; null for contiguous
    tree_degree   INTEGER NOT NULL DEFAULT 2,
    leaf_count    INTEGER NOT NULL,
    merkle_root   TEXT NOT NULL,
    signer_id     INTEGER NOT NULL REFERENCES authority(id),
    signature     TEXT NOT NULL,
    issued_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_sparse_range ON sparse_checkpoint(seq_lo, seq_hi);

-- ── L6 kg edges ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS kg_edge (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    src_kind       TEXT NOT NULL,
    src_id         INTEGER NOT NULL,
    dst_kind       TEXT NOT NULL,
    dst_id         INTEGER NOT NULL,
    graph_type     TEXT NOT NULL REFERENCES graph_types(code),
    label          TEXT NOT NULL DEFAULT '',
    weight         REAL NOT NULL DEFAULT 1.0,
    meta           TEXT NOT NULL DEFAULT '{}',
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_kg_src ON kg_edge(src_kind, src_id);
CREATE INDEX IF NOT EXISTS ix_kg_dst ON kg_edge(dst_kind, dst_id);
CREATE INDEX IF NOT EXISTS ix_kg_type ON kg_edge(graph_type);

-- ── L7 the fixed point ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fabric_top (
    id          INTEGER PRIMARY KEY CHECK (id = 1),
    digest      TEXT NOT NULL,
    level_count INTEGER NOT NULL,
    row_total   INTEGER NOT NULL,
    note        TEXT NOT NULL DEFAULT
      'digest = sha256 over ordered digests of every table except this one',
    built_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ── the reconciliation view ───────────────────────────────────
CREATE VIEW IF NOT EXISTS v_authority_approval_attestation AS
SELECT
    a.code            AS authority,
    a.name            AS signer_name,
    ap.code           AS approval,
    ap.decision,
    ap.residual_risk,
    at.code           AS attestation,
    at.signature      AS att_sig,
    sc.code           AS checkpoint,
    sc.mode,
    sc.seq_lo, sc.seq_hi,
    sc.merkle_root
FROM approval ap
JOIN authority a ON a.id = ap.authority_id
LEFT JOIN attestation at
    ON at.subject_table = ap.subject_table
   AND at.subject_id    = ap.subject_id
LEFT JOIN sparse_checkpoint sc
    ON sc.signer_id = a.id
   AND sc.seq_lo  <= ap.id
   AND ap.id      <= sc.seq_hi;

CREATE VIEW IF NOT EXISTS v_fabric AS
SELECT
    (SELECT digest       FROM fabric_top)                 AS top_digest,
    (SELECT COUNT(*)     FROM graph_types)                AS graph_types,
    (SELECT COUNT(*)     FROM authority)                  AS authorities,
    (SELECT COUNT(*)     FROM approval)                   AS approvals,
    (SELECT COUNT(*)     FROM attestation)                AS attestations,
    (SELECT COUNT(*)     FROM sparse_checkpoint)          AS checkpoints,
    (SELECT COUNT(*)     FROM kg_edge)                    AS kg_edges,
    (SELECT COUNT(*)     FROM events)                     AS events,
    (SELECT COUNT(*)     FROM ontology)                   AS ontology,
    (SELECT COUNT(*)     FROM registry_entries)           AS registry;
"""


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def merkle_root(leaves: list[str], degree: int = 2) -> str:
    if not leaves:
        return sha256_hex(b"")
    level = list(leaves)
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), degree):
            chunk = level[i:i+degree]
            nxt.append(sha256_hex("".join(chunk).encode()))
        level = nxt
    return level[0]


def sign(key_hex: str, payload: str) -> str:
    return hmac.new(bytes.fromhex(key_hex), payload.encode(), hashlib.sha256).hexdigest()


def seed(con: sqlite3.Connection) -> None:
    # graph types
    for code, label, family, d, a, h, b in GRAPH_TYPES:
        con.execute(
            "INSERT OR IGNORE INTO graph_types "
            "(code,label,family,directed,acyclic,hyper,bipartite) "
            "VALUES (?,?,?,?,?,?,?)",
            (code, label, family, d, a, h, b),
        )

    # authorities: three named humans, one delegation edge
    auths = [
        ("AUTH-CISO", "Dana Reyes",   "CISO",   None,      "global"),
        ("AUTH-DPO",  "Lior Katz",    "DPO",    None,      "personal-data"),
        ("AUTH-ENG",  "Sam Okafor",   "EngLead", "AUTH-CISO", "engineering"),
    ]
    for code, name, role, delegate, scope in auths:
        con.execute(
            "INSERT OR IGNORE INTO authority "
            "(code,name,role,scope) VALUES (?,?,?,?)",
            (code, name, role, scope),
        )
        if delegate:
            con.execute(
                "UPDATE authority SET delegated_from = "
                "(SELECT id FROM authority WHERE code = ?) "
                "WHERE code = ?",
                (delegate, code),
            )
        # key per authority
        con.execute(
            "INSERT OR IGNORE INTO authority_key (authority_id, key_hex) "
            "SELECT id, ? FROM authority WHERE code = ?",
            (secrets.token_hex(32), code),
        )

    # approvals: pick a few gap rows and decide
    def auth_id(code): return con.execute(
        "SELECT id FROM authority WHERE code=?", (code,)).fetchone()[0]

    targets = [
        ("AUTH-CISO", "gov_named_authorities", 1, "approve", None),
        ("AUTH-CISO", "runtime_sigstore",       1, "waive",   0.35),
        ("AUTH-ENG",  "runtime_event_store",    1, "approve", None),
    ]
    for i, (a_code, table, sid, decision, risk) in enumerate(targets, 1):
        code = f"AP-{i:03d}"
        con.execute(
            "INSERT OR IGNORE INTO approval "
            "(code, authority_id, subject_table, subject_id, decision, "
            " rationale, residual_risk) VALUES (?,?,?,?,?,?,?)",
            (code, auth_id(a_code), table, sid, decision,
             f"{decision} {table}#{sid}", risk),
        )

    # attestations: sign every approval with its authority's key
    rows = con.execute(
        "SELECT ap.id, ap.code, ap.authority_id, a.code "
        "FROM approval ap JOIN authority a ON a.id = ap.authority_id"
    ).fetchall()
    for ap_id, ap_code, a_id, _ in rows:
        key = con.execute(
            "SELECT key_hex FROM authority_key WHERE authority_id=?",
            (a_id,),
        ).fetchone()[0]
        payload = f"approval:{ap_code}:{ap_id}"
        sig = sign(key, payload)
        con.execute(
            "INSERT OR IGNORE INTO attestation "
            "(code, subject_table, subject_id, payload_hash, signer_id, signature) "
            "VALUES (?,?,?,?,?,?)",
            (f"AT-{ap_code}", "approval", ap_id,
             sha256_hex(payload.encode()), a_id, sig),
        )

    # SPARSE checkpoint: pick every 5th event seq in a range, Merkle them
    evs = [r[0] for r in con.execute(
        "SELECT seq FROM events ORDER BY seq").fetchall()]
    if evs:
        lo, hi = evs[0], evs[-1]
        # sparse subset: every 5th event
        covered = evs[::5] or [lo]
        leaves = [sha256_hex(str(s).encode()) for s in covered]
        root = merkle_root(leaves, degree=2)
        signer = auth_id("AUTH-CISO")
        key = con.execute(
            "SELECT key_hex FROM authority_key WHERE authority_id=?",
            (signer,),
        ).fetchone()[0]
        sig = sign(key, f"checkpoint:{lo}:{hi}:{root}")
        con.execute(
            "INSERT OR IGNORE INTO sparse_checkpoint "
            "(code, mode, seq_lo, seq_hi, covered_seqs, tree_degree, "
            " leaf_count, merkle_root, signer_id, signature) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (f"CK-{lo}-{hi}", "sparse", lo, hi,
             json.dumps(covered), 2, len(covered), root, signer, sig),
        )

    # kg edges: approval --approves--> subject (typed by a graph type)
    graph_type_for_table = {
        "gov_named_authorities": "AccessControl",
        "runtime_sigstore":      "Provenance",
        "runtime_event_store":   "EventStream",
    }
    for ap_id, ap_code, subject_table, subject_id in con.execute(
        "SELECT id, code, subject_table, subject_id FROM approval"
    ):
        gt = graph_type_for_table.get(subject_table, "KG")
        con.execute(
            "INSERT INTO kg_edge "
            "(src_kind, src_id, dst_kind, dst_id, graph_type, label) "
            "VALUES (?,?,?,?,?,?)",
            ("approval", ap_id, subject_table, subject_id, gt, "approves"),
        )


def digest_all(con: sqlite3.Connection) -> tuple[str, int, int]:
    """sha256 over ordered digests of every user table except fabric_top."""
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "AND name NOT IN ('fabric_top') ORDER BY name"
    )]
    h = hashlib.sha256()
    rows_total = 0
    for t in tables:
        h.update(t.encode()); h.update(b"\x00")
        for row in con.execute(f"SELECT * FROM {t} ORDER BY rowid"):
            h.update(repr(row).encode()); h.update(b"\n")
            rows_total += 1
    return h.hexdigest(), len(tables), rows_total


def main() -> int:
    if not DB.exists():
        print(f"  ! {DB} missing — run scripts/build_db.py first")
        return 2
    con = sqlite3.connect(DB)
    con.executescript(LEVELS_DDL)
    seed(con)
    con.commit()

    digest, lvls, rows = digest_all(con)
    con.execute(
        "INSERT OR REPLACE INTO fabric_top (id, digest, level_count, row_total) "
        "VALUES (1, ?, ?, ?)",
        (digest, lvls, rows),
    )
    con.commit()

    # report
    print("── higher levels built ──")
    for t in ("graph_types", "authority", "authority_key", "approval",
              "attestation", "sparse_checkpoint", "kg_edge", "fabric_top"):
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<18} {n}")

    print()
    print("── fabric_top ──")
    row = con.execute(
        "SELECT digest, level_count, row_total, built_at FROM fabric_top"
    ).fetchone()
    print(f"  digest   {row[0][:32]}…")
    print(f"  levels   {row[1]}")
    print(f"  rows     {row[2]}")
    print(f"  built    {row[3]}")

    print()
    print("── authority chain ──")
    for code, name, role, df in con.execute("""
        SELECT a.code, a.name, a.role, p.code
        FROM authority a LEFT JOIN authority p ON p.id = a.delegated_from
        ORDER BY a.code
    """):
        print(f"  {code:<10} {name:<12} {role:<8} from {df or '—'}")

    print()
    print("── reconciliation view ──")
    for r in con.execute(
        "SELECT authority, approval, decision, checkpoint, mode, "
        "seq_lo, seq_hi FROM v_authority_approval_attestation"
    ):
        print(f"  {r[0]:<9} {r[1]:<7} {r[2]:<8} {r[3] or '—':<14} "
              f"{r[4] or '—':<11} [{r[5]},{r[6]}]")

    print()
    print("── fabric view (one row) ──")
    cols = [c[0] for c in con.execute("SELECT * FROM v_fabric").description]
    vals = con.execute("SELECT * FROM v_fabric").fetchone()
    for c, v in zip(cols, vals):
        print(f"  {c:<14} {v}")

    # restart test
    con.close()
    con2 = sqlite3.connect(DB)
    row2 = con2.execute("SELECT digest FROM fabric_top").fetchone()
    ok = row2 and row2[0] == digest
    integ = con2.execute("PRAGMA integrity_check").fetchone()[0]
    con2.close()
    print()
    print("── restart test ──")
    print(f"  second open digest matches  {ok}")
    print(f"  sqlite integrity            {integ}")
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
