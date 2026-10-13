#!/usr/init/env python3
from __future__ import annotations

import json
from pathlib import Path

TAXONOMY = {
    "Grammar": {
        "Phonology": [
            "Consonant", "Vowel", "Allophone", "Feature", "Syllable", 
            "Phonotactics", "Prosody", "Morphophonology"
        ],
        "Morphology": [
            "Morpheme", "Inflection", "Derivation", "Compounding", 
            "Conversion", "Reduplication", "Suppletion", "Alternation", 
            "Apophony", "Umlaut", "Ablaut", "Metathesis", "Haplology", 
            "Elision", "Epenthesis", "Prothesis", "Paragoge", "Syncope", 
            "Apocope", "Aphaeresis", "Synaeresis", "Diaeresis", "Assimilation", 
            "Dissimilation", "Lenition", "Fortition", "Palatalization", 
            "Velarization", "Labialization", "Nasalization", "Aspiration", 
            "Deaspiration", "Voicing", "Devoicing", "Flapping", "Tapping", 
            "Trilling", "Spirantization", "Affrication", "Glottalization", 
            "Tonogenesis", "Sandhi"
        ],
        "Syntax": [
            "Word", "Phrase", "Clause", "Sentence", "Clause function", 
            "Grammatical relation", "Thematic role", "Syntactic operation"
        ],
        "Semantics": [
            "Reference", "Sense", "Denotation", "Connotation", "Predication", 
            "Quantification", "Scope", "Binding", "Tense", "Aspect", "Mood", 
            "Modality", "Evidentiality", "Presupposition", "Entailment", 
            "Implicature", "Truth conditions", "Compositionality", "Thematic roles", 
            "Event structure", "Lexical semantics", "Formal semantics", 
            "Cognitive semantics", "Frame semantics", "Prototype semantics", 
            "Componential analysis", "Field theory", "Sense relation"
        ],
        "Pragmatics": [
            "Speech act", "Implicature", "Presupposition", "Deixis", "Politeness", 
            "Face", "Relevance", "Context", "Common ground", "Information structure", 
            "Cohesion", "Coherence"
        ],
        "Discourse": [
            "Text", "Conversation", "Turn-taking", "Adjacency pair", "Repair", 
            "Genre", "Register", "Style", "Cohesion", "Coherence", "Anaphora", 
            "Cataphora", "Exophora", "Endophora", "Topic chain", "Paragraph", 
            "Narrative", "Exposition", "Argumentation", "Description"
        ],
        "Theoretical grammar": [
            "Traditional grammar", "Structural grammar", "Generative grammar", 
            "Dependency grammar", "Construction grammar", "Cognitive grammar", 
            "Functional grammar", "Systemic functional grammar", "Lexical-functional grammar", 
            "Head-driven phrase structure grammar", "Categorial grammar", "Tree adjoining grammar", 
            "Optimality theory", "Role and reference grammar", "Word grammar", 
            "Universal grammar", "Montague grammar", "Generalized phrase structure grammar", 
            "Relational grammar", "Stratificational grammar", "Tagmemics", 
            "Prague school", "Copenhagen school", "London school", "American structuralism", 
            "Descriptivism", "Prescriptivism", "Pedagogical grammar", "Comparative grammar", 
            "Historical grammar", "Synchronic grammar", "Diachronic grammar", "Language-specific grammar"
        ]
    }
}

def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    app_dir = repo_root / "app" / "grammar"
    app_dir.mkdir(parents=True, exist_ok=True)

    tests_dir = repo_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write taxonomy schema
    schema_path = app_dir / "taxonomy.json"
    schema_path.write_text(json.dumps(TAXONOMY, indent=2))
    print(f" -> Created taxonomy schema at {schema_path}")

    # 2. Write mastery engine module
    engine_code = '''from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Set

class MasteryEngine:
    def __init__(self) -> None:
        schema_file = Path(__file__).parent / "taxonomy.json"
        self.taxonomy: Dict[str, Dict[str, List[str]]] = json.loads(schema_file.read_text())
        self.mastered_nodes: Set[str] = set()

    def certify(self, node: str) -> None:
        self.mastered_nodes.add(node)

    def is_mastered(self, node: str) -> bool:
        return node in self.mastered_nodes

    def subsystem_progress(self, domain: str, subcategory: str) -> float:
        nodes = self.taxonomy.get(domain, {}).get(subcategory, [])
        if not nodes:
            return 0.0
        passed = sum(1 for n in nodes if n in self.mastered_nodes)
        return passed / len(nodes)
'''.strip() + "\n"
    
    (app_dir / "engine.py").write_text(engine_code)
    print(f" -> Created mastery engine at {app_dir / 'engine.py'}")

    # 3. Write test suite covering all taxonomy branches
    test_code = '''from __future__ import annotations
import pytest
from app.grammar.engine import MasteryEngine

def test_linguistic_mastery_pipeline() -> None:
    engine = MasteryEngine()
    
    # Verify taxonomy keys exist
    assert "Grammar" in engine.taxonomy
    subdomains = engine.taxonomy["Grammar"]
    
    expected_subdomains = [
        "Phonology", "Morphology", "Syntax", 
        "Semantics", "Pragmatics", "Discourse", "Theoretical grammar"
    ]
    for sub in expected_subdomains:
        assert sub in subdomains
        assert len(subdomains[sub]) > 0

    # Simulate gating certification
    for sub, nodes in subdomains.items():
        for node in nodes:
            engine.certify(node)
            assert engine.is_mastered(node)
            assert engine.subsystem_progress("Grammar", sub) == 1.0

    print("All linguistic mastery gates verified successfully.")
'''.strip() + "\n"

    (tests_dir / "test_linguistic_mastery.py").write_text(test_code)
    print(f" -> Created test suite at {tests_dir / 'test_linguistic_mastery.py'}")

if __name__ == "__main__":
    main()
