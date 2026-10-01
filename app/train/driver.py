"""TrainDriver: N runs, each pollinating the mesh."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.train.core import Trainer, TrainConfig, Run
from app.train.mesh import MeshOfMeshes, weave, criss_cross, trans, pollinate
from app.train.cd_state import CDState, resolve_cd
from app.train.publish import publish, PublishBundle


@dataclass
class TrainGeneration:
    index: int
    run: Run
    cd: CDState
    publish: PublishBundle
    delta_from_prev: Dict[str, float] = field(default_factory=dict)

    def to_dict(self):
        return {
            "index": self.index,
            "run": self.run.to_dict(),
            "cd": self.cd.to_dict(),
            "publish": self.publish.to_dict(),
            "delta_from_prev": self.delta_from_prev,
        }


@dataclass
class TrainDriver:
    cfg: TrainConfig = field(default_factory=TrainConfig)
    generations: int = 3

    def run(self) -> dict:
        trainer = Trainer(self.cfg)
        gens: List[TrainGeneration] = []
        mesh = MeshOfMeshes()
        prev_rates: Dict[tuple, float] = {}

        for i in range(self.generations):
            r = trainer.run_once(index=i)
            mesh.add_run(r)
            cd = resolve_cd(r)
            pub = publish(r, chain_id=f"train-{i}")

            cur_rates = {(t.kind, t.solver, t.difficulty): t.rate
                         for t in r.tiles}
            delta: Dict[str, float] = {}
            for key, v in cur_rates.items():
                kstr = "/".join(key)
                p = prev_rates.get(key, 0.0)
                delta[kstr] = round(v - p, 4)
            prev_rates = cur_rates

            gens.append(TrainGeneration(index=i, run=r, cd=cd,
                                        publish=pub,
                                        delta_from_prev=delta))

        # weave / criss-cross / trans / pollinate
        cc = []
        for i in range(len(mesh.runs)):
            for j in range(i + 1, len(mesh.runs)):
                cc.append(criss_cross(mesh.runs[i], mesh.runs[j]))
        tr = trans(mesh.runs)
        pl: List[Dict] = []
        for i in range(len(mesh.runs)):
            for j in range(i + 1, len(mesh.runs)):
                pl.extend(pollinate(mesh.runs[i], mesh.runs[j]))

        return {
            "generations": [g.to_dict() for g in gens],
            "mesh": mesh.to_dict(),
            "criss_cross": cc,
            "trans": tr,
            "pollinate": pl,
        }
