TAXONOMIES = {
    "G_GENERATOR": ["G0 Bootstrap", "G1 Parse", "G2 Analyze", "G3 Transform", "G4 Synthesize", "G5 Emit", "G6 Validate", "G7 Execute", "G8 Coordinate", "G9 Observe", "G10 Persist", "G11 Publish", "G12 Self-Evolve"],
    "C_COMPILER": ["C0 Bootstrap Compiler", "C1 Front-End", "C2 Semantic Compiler", "C3 Intermediate Representation", "C4 Analysis", "C5 Optimization", "C6 Transformation", "C7 Back-End", "C8 Linking", "C9 Verification", "C10 Artifact Generation", "C11 Runtime Preparation", "C12 Incremental Compilation", "C13 Distributed Compilation", "C14 Diagnostics", "C15 Publication", "C16 Self-Hosting"]
}

def get_atlas_summary():
    return {k: len(v) for k, v in TAXONOMIES.items()}
