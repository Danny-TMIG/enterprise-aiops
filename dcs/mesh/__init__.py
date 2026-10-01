"""MESH — taxonomies × TRIAD × UCS as one verifiable pipeline."""
from dcs.mesh.taxonomy import FAMILIES, stage, stages_of
from dcs.mesh.behavior import Behavior, Pipeline, empty
from dcs.mesh.ucs import UCS, UCS_STAGES
from dcs.mesh.laws import LAWS, run_all as run_laws

__all__ = ["FAMILIES", "stage", "stages_of", "Behavior", "Pipeline",
           "empty", "UCS", "UCS_STAGES", "LAWS", "run_laws"]
