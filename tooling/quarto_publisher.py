#!/usr/init/env python3
"""
THE MARK INTELLIGENCE GROUP (TMIG)
QUARTO DOCUMENTATION PUBLISHING ENGINE (ASF v1.2)
"""
import os
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"

def setup_quarto():
    print("📚 [QUARTO] Initializing Quarto publishing configuration...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Create Quarto Project Configuration
    quarto_yaml = """project:
  type: website
  output-dir: ../dist/docs

website:
  title: "Aether Sovereign Fabric (ASF v1.2)"
  navbar:
    left:
      - href: index.md
        text: Overview
      - href: architecture.md
        text: Architecture & 75 Components
      - href: ledgers.md
        text: Cryptographic Ledgers

format:
  html:
    theme: cosmo
    css: styles.css
    toc: true
"""
    (DOCS_DIR / "_quarto.yml").write_text(quarto_yaml)

    # 2. Create index page
    index_md = """# Aether Sovereign Fabric

Welcome to the official documentation for the **The Mark Intelligence Group (TMIG)** Aether Sovereign AIOps platform running on native Apple Silicon M4 Max hardware.

## Architecture
- **Aether Cognition (AX):** Local MLX inference and runtime pipelines.
- **Aether Govern (AG):** WORM state ledgers, IAM, and policy enforcement.
- **Aether Compute (AC):** Low-level telemetry and execution gateways.
"""
    (DOCS_DIR / "index.md").write_text(index_md)

    print("💯 [SUCCESS] Quarto config and site structure generated in docs/")

if __name__ == "__main__":
    setup_quarto()
