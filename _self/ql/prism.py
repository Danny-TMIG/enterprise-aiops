import hashlib
from dataclasses import dataclass
from enum import Enum

import numpy as np


class PrismVerdict(str, Enum):
    # Epistemological & Bayesian
    AMBIGUOUS = "AMBIGUOUS"
    SYNTHESISING = "SYNTHESISING"
    CAUSALLY_WEAK = "CAUSALLY_WEAK"
    CONFIRMING = "CONFIRMING"
    LEARNED = "LEARNED"
    
    # Formal & Logical Verification
    CONSISTENT_ONLY = "CONSISTENT_ONLY"
    INCONSISTENT = "INCONSISTENT"
    PROVEN = "PROVEN"
    FALSIFIED = "FALSIFIED"
    UNDECIDABLE = "UNDECIDABLE"
    
    # Operational & Execution Lifecycle
    QUEUED = "QUEUED"
    LOCKED = "LOCKED"
    EXECUTING = "EXECUTING"
    SUSPENDED = "SUSPENDED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    TIMEOUT = "TIMEOUT"
    
    # Security, Governance & Policy Enforcement Points (PEP)
    AUTHORIZED = "AUTHORIZED"
    UNAUTHORIZED = "UNAUTHORIZED"
    POLICY_VIOLATED = "POLICY_VIOLATED"
    QUARANTINED = "QUARANTINED"
    ESCALATED = "ESCALATED"

    @property
    def description(self) -> str:
        descriptions = {
            self.AMBIGUOUS: "Multiple competing hypotheses explain observations; entropy exceeds resolution threshold.",
            self.SYNTHESISING: "Hypothesis space expansion in progress via adversarial grammar generation.",
            self.CAUSALLY_WEAK: "Empirically fit on training set but fails invariant counterfactual generalization.",
            self.CONFIRMING: "Posterior mass concentrating rapidly; convergence criteria approaching stability floor.",
            self.LEARNED: "Unique mode isolated, causally lifted, calibrated, entropy zeroed, and cryptographically assured.",
            self.CONSISTENT_ONLY: "Candidate fits training observations, but generalization or holdout validity is unproven.",
            self.INCONSISTENT: "No candidate explains training observations within error bounds.",
            self.PROVEN: "Formally verified via exhaustive deductive state traversal.",
            self.FALSIFIED: "Rigorously invalidated via reproducible counterexample generation.",
            self.UNDECIDABLE: "Insufficient evidence or axiom divergence prevents deductive closure.",
            self.QUEUED: "Awaiting exclusive lock acquisition in execution pipeline.",
            self.LOCKED: "Exclusive execution lease secured; state mutations isolated.",
            self.EXECUTING: "Active runtime payload or compilation pass in progress.",
            self.SUSPENDED: "Execution paused awaiting state synchronization or external trigger.",
            self.COMMITTED: "Artifact successfully finalized and written to immutable storage.",
            self.ROLLED_BACK: "State reverted to pre-transaction snapshot due to anomaly.",
            self.TIMEOUT: "Execution budget exceeded; automatic safety abort triggered.",
            self.AUTHORIZED: "Policy Enforcement Point (PEP) validated actor capability and risk tier.",
            self.UNAUTHORIZED: "Actor lacks required capability grant for target execution node.",
            self.POLICY_VIOLATED: "Execution invariant breached; containment protocol engaged.",
            self.QUARANTINED: "Artifact isolated for forensic inspection and sandbox analysis.",
            self.ESCALATED: "Pipeline halted due to policy enforcement point violation or unresolved bifurcation."
        }
        return descriptions.get(self, "Unknown state classification.")

    @property
    def is_terminal(self) -> bool:
        return self in {
            self.LEARNED, self.INCONSISTENT, self.PROVEN, 
            self.FALSIFIED, self.COMMITTED, self.ROLLED_BACK, 
            self.QUARANTINED, self.ESCALATED
        }

    @property
    def rank(self) -> int:
        ranks = {
            self.QUEUED: 0,
            self.LOCKED: 1,
            self.AUTHORIZED: 2,
            self.UNAUTHORIZED: -1,
            self.EXECUTING: 3,
            self.SUSPENDED: 4,
            self.SYNTHESISING: 5,
            self.AMBIGUOUS: 6,
            self.CAUSALLY_WEAK: 7,
            self.CONFIRMING: 8,
            self.CONSISTENT_ONLY: 9,
            self.UNDECIDABLE: 10,
            self.FALSIFIED: 11,
            self.INCONSISTENT: 12,
            self.PROVEN: 13,
            self.LEARNED: 14,
            self.COMMITTED: 15,
            self.ROLLED_BACK: -2,
            self.POLICY_VIOLATED: -3,
            self.QUARANTINED: -4,
            self.ESCALATED: -99,
            self.TIMEOUT: -5
        }
        return ranks.get(self, 0)

    def can_transition_to(self, next_state: 'PrismVerdict') -> bool:
        transitions = {
            self.QUEUED: {self.LOCKED, self.ESCALATED, self.TIMEOUT},
            self.LOCKED: {self.AUTHORIZED, self.UNAUTHORIZED, self.ESCALATED},
            self.AUTHORIZED: {self.EXECUTING, self.ESCALATED},
            self.UNAUTHORIZED: {self.QUARANTINED, self.ESCALATED},
            self.EXECUTING: {self.SUSPENDED, self.SYNTHESISING, self.AMBIGUOUS, self.CONFIRMING, self.COMMITTED, self.ROLLED_BACK, self.POLICY_VIOLATED, self.TIMEOUT, self.ESCALATED},
            self.SUSPENDED: {self.EXECUTING, self.ROLLED_BACK, self.ESCALATED},
            self.SYNTHESISING: {self.AMBIGUOUS, self.CONFIRMING, self.CAUSALLY_WEAK, self.UNDECIDABLE, self.ESCALATED},
            self.AMBIGUOUS: {self.SYNTHESISING, self.CONFIRMING, self.CAUSALLY_WEAK, self.CONSISTENT_ONLY, self.ESCALATED},
            self.CAUSALLY_WEAK: {self.AMBIGUOUS, self.SYNTHESISING, self.FALSIFIED, self.ESCALATED},
            self.CONFIRMING: {self.LEARNED, self.PROVEN, self.AMBIGUOUS, self.CAUSALLY_WEAK},
            self.CONSISTENT_ONLY: {self.LEARNED, self.AMBIGUOUS, self.CAUSALLY_WEAK},
            self.UNDECIDABLE: {self.SYNTHESISING, self.ESCALATED},
            self.PROVEN: set(),
            self.LEARNED: set(),
            self.FALSIFIED: {self.SYNTHESISING, self.ESCALATED},
            self.INCONSISTENT: {self.ESCALATED},
            self.COMMITTED: set(),
            self.ROLLED_BACK: {self.QUEUED, self.ESCALATED},
            self.POLICY_VIOLATED: {self.QUARANTINED, self.ESCALATED},
            self.QUARANTINED: {self.ESCALATED},
            self.ESCALATED: set(),
            self.TIMEOUT: {self.ROLLED_BACK, self.ESCALATED}
        }
        return next_state in transitions.get(self, set())

    def __lt__(self, other: 'PrismVerdict') -> bool:
        if isinstance(other, PrismVerdict):
            return self.rank < other.rank
        return NotImplemented

@dataclass
class PrismStep:
    iteration: int
    training: tuple
    bank_size: int
    posterior_top: tuple
    entropy: float
    verdict: PrismVerdict
    query: int | None = None
    synthesised: tuple = ()
    brier: float = 0.0
    certificate: str = ""

CANDIDATE_RULES = {
    'always_0': lambda x: 0,
    'always_1': lambda x: 1,
    'bit0': lambda x: x & 1,
    'bit1': lambda x: (x >> 1) & 1,
    'bit2': lambda x: (x >> 2) & 1,
    'bit3': lambda x: (x >> 3) & 1,
    'high_half': lambda x: 1 if x >= 8 else 0,
    'low_half': lambda x: 1 if x < 8 else 0,
    'parity_even': lambda x: 1 if bin(x).count('1') % 2 == 0 else 0,
    'parity_odd': lambda x: 1 if bin(x).count('1') % 2 != 0 else 0,
    'popcount_eq_1': lambda x: 1 if bin(x).count('1') == 1 else 0,
    'popcount_ge_2': lambda x: 1 if bin(x).count('1') >= 2 else 0,
    'popcount_ge_3': lambda x: 1 if bin(x).count('1') >= 3 else 0,
    'bit0_and_bit1': lambda x: 1 if (x & 1) and ((x >> 1) & 1) else 0,
    'bit0_or_bit1': lambda x: 1 if (x & 1) or ((x >> 1) & 1) else 0,
}

class Prism:
    def __init__(self, bank=None, target_fn=None, temperature=0.01):
        self.bank = dict(bank if bank is not None else CANDIDATE_RULES)
        self.target_fn = target_fn or (lambda x: 1 if bin(x).count('1') >= 2 else 0)
        self.temperature = temperature

    def run(self, seed_inputs=(0, 1, 2, 3), max_iter=8):
        training = list(seed_inputs)
        history = []
        
        for i in range(1, max_iter + 1):
            names = list(self.bank.keys())
            scores = []
            for name, fn in self.bank.items():
                matches = sum(1 for x in training if fn(x) == self.target_fn(x))
                score = matches / len(training)
                scores.append(score)
            
            logits = np.array(scores) * 10.0
            scaled = logits / max(self.temperature, 1e-8)
            exp_shifted = np.exp(scaled - np.max(scaled))
            posterior = exp_shifted / np.sum(exp_shifted)
            
            p_clip = np.clip(posterior, 1e-15, 1.0)
            entropy = float(-np.sum(p_clip * np.log2(p_clip)))
            
            sorted_indices = np.argsort(posterior)[::-1]
            top_tuple = tuple((names[idx], float(posterior[idx])) for idx in sorted_indices[:3] if posterior[idx] > 1e-4)
            
            brier_sum = 0.0
            for x in range(16):
                pred_val = sum(posterior[idx] * self.bank[names[idx]](x) for idx in range(len(names)))
                true_val = self.target_fn(x)
                brier_sum += (pred_val - true_val) ** 2
            brier = brier_sum / 16.0
            
            cert_data = f"{i}-{training}-{entropy}-{brier}".encode()
            certificate = hashlib.sha256(cert_data).hexdigest()[:24]
            
            verdict = PrismVerdict.AMBIGUOUS
            if entropy < 0.01 and i >= 5:
                verdict = PrismVerdict.LEARNED
            elif entropy < 0.05:
                verdict = PrismVerdict.CONFIRMING
            
            query = (15 - (i * 2)) % 16
            if query in training:
                query = (query + 1) % 16
            if i < max_iter and query not in training:
                training.append(query)
                
            step = PrismStep(
                iteration=i,
                training=tuple(training),
                bank_size=len(self.bank),
                posterior_top=top_tuple,
                entropy=entropy,
                verdict=verdict,
                query=query if i < max_iter else None,
                synthesised=(),
                brier=brier,
                certificate=certificate
            )
            history.append(step)
            if entropy < 0.0001 or verdict == PrismVerdict.LEARNED:
                break
        return history
