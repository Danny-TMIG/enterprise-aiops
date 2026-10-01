"""MESH — taxonomies × TRIAD × UCS as one verifiable pipeline."""

from dcs.mesh.behavior import Behavior, Pipeline, empty
from dcs.mesh.laws import LAWS
from dcs.mesh.laws import run_all as run_laws
from dcs.mesh.taxonomy import FAMILIES, stage, stages_of
from dcs.mesh.ucs import UCS, UCS_STAGES

__all__ = [
    "FAMILIES",
    "stage",
    "stages_of",
    "Behavior",
    "Pipeline",
    "empty",
    "UCS",
    "UCS_STAGES",
    "LAWS",
    "run_laws",
]
