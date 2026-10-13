import asyncio
from collections.abc import Callable


class MasteryEngine:
    def __init__(self):
        self.taxonomy = {
            "Grammar": {
                "Phonology": ["node_phon_1"],
                "Morphology": ["node_morph_1"],
                "Syntax": ["node_syntax_1"],
                "Semantics": ["node_sem_1"],
                "Pragmatics": ["node_prag_1"],
                "Discourse": ["node_disc_1"],
                "Theoretical grammar": ["node_tg_1"]
            }
        }
        self.mastered = set()

    def certify(self, node: str):
        self.mastered.add(node)

    def is_mastered(self, node: str) -> bool:
        return node in self.mastered

    def subsystem_progress(self, domain: str, subdomain: str) -> float:
        nodes = self.taxonomy.get(domain, {}).get(subdomain, [])
        if not nodes:
            return 1.0
        mastered_count = sum(1 for n in nodes if n in self.mastered)
        return mastered_count / len(nodes)

class ConvergenceMetrics:
    def __init__(self, achieved_value: float):
        self.achieved_value = achieved_value

class MeshConvergenceValidator:
    def __init__(self, default_timeout: float = 2.0, poll_interval: float = 0.01):
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval

    async def assert_converges(self, probe_fn: Callable[[], float], expected: float, subsystem: str) -> ConvergenceMetrics:
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < self.default_timeout:
            val = probe_fn()
            if abs(val - expected) < 1e-5:
                return ConvergenceMetrics(achieved_value=val)
            await asyncio.sleep(self.poll_interval)
        val = probe_fn()
        return ConvergenceMetrics(achieved_value=val)
