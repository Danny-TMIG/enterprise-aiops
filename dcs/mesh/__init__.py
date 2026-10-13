"""MESH — taxonomies × TRIAD × UCS as one verifiable pipeline."""

from dcs.mesh.behavior import Behavior, Pipeline, empty  # pragma: no cover
from dcs.mesh.laws import LAWS  # pragma: no cover
from dcs.mesh.laws import run_all as run_laws  # pragma: no cover
from dcs.mesh.taxonomy import FAMILIES, stage, stages_of  # pragma: no cover
from dcs.mesh.ucs import UCS, UCS_STAGES  # pragma: no cover

__all__ = [
    "FAMILIES",
    "LAWS",
    "UCS",
    "UCS_STAGES",
    "Behavior",
    "Pipeline",
    "empty",
    "run_laws",
    "stage",
    "stages_of",
]
