# Forty Algorithms That Changed Civilization

A live registry. The doc is a projection of
`app/atlas/algorithms.py`. Edit the data in that module
and re-run `python3 -m app.atlas.cli` to regenerate this file.

Total entries: **40** across **7** sections.

## 1. Foundational Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 1 | Euclidean Algorithm (c. 300 BCE) | Mathematics | First known algorithm; computes greatest common divisor (GCD); defines algorithmic reasoning itself. | L0 Boolean logic | `M-04`, `M-01` |
| 2 | Fast Fourier Transform (FFT) | Signal Processing | Converts between time and frequency domains; essential in audio, imaging, and quantum computing. | L2 Combinatory logic | `I-02`, `I-03` |
| 3 | Merge Sort / Quicksort | Computer Science | Core of data sorting and search efficiency; fundamental to database and OS design. | L1 Lambda calculus | `C-01`, `T-14` |
| 4 | Binary Search | Algorithms & Data | The archetype of divide-and-conquer; O(log n) search time. | L1 Lambda calculus | `C-01`, `T-14` |
| 5 | Dynamic Programming (Bellman) | Optimization | Basis for reinforcement learning, route planning, and sequence alignment. | L2 Combinatory logic | `C-01`, `M-21` |
| 6 | Dijkstra's Algorithm / A* Search | Graph Theory | Core of routing, GPS navigation, AI pathfinding, and network optimization. | L1 Lambda calculus | `C-01`, `T-14` |
| 7 | Backpropagation | Machine Learning | Enables deep neural networks to learn via gradient descent. | L3 Turing machine | `S-01`, `S-02` |
| 8 | Gradient Descent / SGD | Optimization | The most used algorithm in modern AI and data fitting. | L3 Turing machine | `S-01`, `M-21` |
| 9 | Monte Carlo Simulation | Statistics & Physics | Models randomness; basis of probabilistic reasoning, nuclear physics, and finance. | L3 Turing machine | `I-10`, `S-01` |
| 10 | Simulated Annealing | Optimization | Mimics physical cooling to find global minima; used in chip design and scheduling. | L5 Interaction combinators | `M-21`, `X-10` |

## 2. Cryptographic & Security Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 11 | RSA | Cryptography | Public-key encryption; enables modern secure communication. | L2 Combinatory logic | `K-01`, `K-03` |
| 12 | Diffie–Hellman Key Exchange | Cryptography | Foundation for secure internet key exchange. | L2 Combinatory logic | `K-01`, `K-04` |
| 13 | SHA-2 / SHA-3 Hashing | Cryptography | Data integrity verification, blockchain proof-of-work. | L2 Combinatory logic | `K-01`, `K-13` |
| 14 | Elliptic Curve Cryptography (ECC) | Cryptography | Efficient encryption; used in Bitcoin, SSL, and blockchain wallets. | L2 Combinatory logic | `K-01`, `K-04` |
| 15 | Zero-Knowledge Proofs (ZKP) | Cryptography | Enables proof without revealing data; central to privacy-preserving blockchain. | L4 Pi calculus | `K-10`, `K-11` |

## 3. Artificial Intelligence & Learning Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 16 | Perceptron / Neural Networks | AI | The foundation of machine learning. | L3 Turing machine | `S-01`, `B-01` |
| 17 | Transformer (Attention Mechanism) | Deep Learning | Core of GPT, BERT, Gemini, Claude, etc.; enables context-rich language understanding. | L7 Category theory | `M-23`, `I-02` |
| 18 | Convolutional Neural Network (CNN) | Computer Vision | Powers vision systems, autonomous vehicles, and medical imaging. | L4 Pi calculus | `S-01`, `B-16` |
| 19 | Reinforcement Learning (Q-Learning / Policy Gradient) | AI | Agents learn via reward feedback; used in robotics and AlphaGo. | L5 Interaction combinators | `M-21`, `N-01` |
| 20 | Expectation-Maximization (EM) | Statistics | Unsupervised learning of latent variables (e.g., clustering, HMMs). | L6 Cellular automata | `S-06`, `S-01` |

## 4. Physics, Mathematics, and Quantum Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 21 | Newton–Raphson Method | Numerical Analysis | Core iterative method for solving nonlinear equations. | L3 Turing machine | `M-04`, `K-24` |
| 22 | Fast Multipole Method (FMM) | Computational Physics | Reduces N-body problems from O(N²) to O(N); used in astrophysics. | L5 Interaction combinators | `M-21`, `C-22` |
| 23 | Shor's Algorithm | Quantum Computing | Polynomial-time factorization; threatens RSA; proves quantum supremacy. | L8 Quantum mechanics | `K-02`, `M-16` |
| 24 | Grover's Algorithm | Quantum Computing | Quadratic speed-up for unstructured search. | L8 Quantum mechanics | `C-01`, `M-17` |
| 25 | Simons' Algorithm | Quantum Foundations | Early quantum algorithm demonstrating exponential speed-up; precursor to Shor's. | L8 Quantum mechanics | `M-23`, `C-14` |

## 5. Economic, Network, and Systems Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 26 | PageRank | Information Retrieval | Google's web ranking engine; models influence and link importance. | L6 Cellular automata | `D-01`, `X-10` |
| 27 | Linear Programming (Simplex / Interior Point) | Optimization | Fundamental to economics, logistics, and control theory. | L5 Interaction combinators | `M-21`, `N-06` |
| 28 | Kalman Filter | Control Systems | Predicts and corrects system states; used in navigation, robotics, and finance. | L6 Cellular automata | `E-01`, `S-04` |
| 29 | Bayesian Inference / Belief Propagation | Probabilistic AI | Backbone of probabilistic reasoning and graphical models. | L6 Cellular automata | `S-06`, `Z-01` |
| 30 | Blockchains (Merkle Tree + Consensus) | Distributed Systems | Decentralized verification and immutable ledgers. | L7 Category theory | `D-02`, `K-01` |

## 6. Advanced / Modern-Era Meta Algorithms

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 31 | Genetic Algorithms / Evolutionary Strategies | Optimization | Mimics evolution to optimize complex systems. | L6 Cellular automata | `Q-06`, `M-21` |
| 32 | Swarm Optimization (Particle Swarm, Ant Colony) | Collective AI | Models emergent intelligence via distributed agents. | L6 Cellular automata | `X-10`, `Q-02` |
| 33 | Diffusion Models (Stable Diffusion, Denoising) | Generative AI | Foundation for modern image/video generation. | L7 Category theory | `Z-12`, `I-02` |
| 34 | Quantum Annealing | Quantum Optimization | Physical realization of optimization using qubit energy minimization. | L8 Quantum mechanics | `M-21`, `C-14` |
| 35 | Transformer Reinforcement Architectures (LLM Swarms) | AGI Systems | Self-referential model orchestration — core of sovereign, autonomous AI networks. | L9 General computation | `I-10`, `M-04` |

## 7. Meta-Historical: Algorithms That Changed Civilization

| # | Algorithm | Domain | Significance | CD Level | Residuals |
|---|-----------|--------|--------------|----------|-----------|
| 36 | Turing Machine | Computation | Formalized the concept of computation itself. | L3 Turing machine | `M-04`, `M-23` |
| 37 | Von Neumann Architecture | Computer Design | Defined all modern computer design. | L3 Turing machine | `A-07`, `A-13` |
| 38 | Shannon Information Theory | Information | Quantified information; foundation of communication and data compression. | L6 Cellular automata | `I-01`, `I-03` |
| 39 | Backpropagation + Transformers Combo | AGI Trajectory | The leap to modern LLMs and AGI trajectory. | L7 Category theory | `S-01`, `M-23` |
| 40 | Gerhardt TOTALITY / Quantum Arbitrage Framework | Total Computation | Unifies symbolic, quantum, and swarm logic into self-referential total computation — a candidate for the next major leap beyond Turing completeness. | L9 General computation | `Ω`, `T-38` |

---

## Registry queries

The registry is importable:

```python
from app.atlas.algorithms import (
    ALGORITHMS, by_section, by_domain, by_level,
    by_residual, search, validate, write_markdown,
)

by_section(3)         # all AI/learning entries
by_level(7)           # category-theory-level entries
by_residual('M-04')   # every entry terminating at Halting
search('transformer') # substring search
validate()            # check residual grounding
write_markdown()      # regenerate docs/algorithms.md
```

## Level summary

| CD Level | Name | Count |
|----------|------|-------|
| L0 | Boolean logic | 1 |
| L1 | Lambda calculus | 3 |
| L2 | Combinatory logic | 6 |
| L3 | Turing machine | 7 |
| L4 | Pi calculus | 2 |
| L5 | Interaction combinators | 4 |
| L6 | Cellular automata | 7 |
| L7 | Category theory | 4 |
| L8 | Quantum mechanics | 4 |
| L9 | General computation | 2 |

---

## Grounding

Every residual ID referenced above is a valid entry
in `app.residual.register`. The validation result is
available by running `validate()`. Entry 40 terminates
at `Ω` (The act of proceeding), the single arity-0
residual in the register.

The register's own residual — `T-38 / C-B4` — applies to
this document: whether its scope is complete cannot be
decided from inside it. Adding entry 41 is the act of
proceeding.
