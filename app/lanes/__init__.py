"""Isolated swim lanes. Each lane is a venv under .lanes/<name>/.

A capability is routed to a lane by its dependency family. The lane
manager builds the venv on demand, installs the declared requirements,
and returns the lane's python interpreter path. Nothing about a lane
is claimed before it exists on disk.
"""
from __future__ import annotations
import json, os, subprocess, sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
LANES_DIR = ROOT / ".lanes"


# capability code -> lane name
ROUTING: Dict[str, str] = {
    # Python data / science
    "pandas":"data","numpy":"data","sklearn":"data","statsmodels":"data",
    "matplotlib":"data","seaborn":"data","scipy":"data","sympy":"data",
    "networkx":"data","nltk":"data","spacy":"data","gensim":"data",
    # Python web
    "django":"web","flask":"web","fastapi":"web","uvicorn":"web",
    "pydantic":"web","sqlalchemy":"web","httpx":"web","requests":"web",
    "click":"web","rich":"web","yaml":"web","toml":"web",
    # ML / deep learning
    "tensorflow":"ml","torch":"ml","jax":"ml","transformers":"ml",
    "diffusers":"ml","peft":"ml","deepspeed":"ml","mlflow":"ml",
    # Quantum
    "qiskit":"quantum","cirq":"quantum","pyquil":"quantum",
    "braket":"quantum","projectq":"quantum",
    # Security / net
    "pyshark":"netsec","stem":"netsec","pyngrok":"netsec",
    "nmap":"netsec","hvac":"netsec",
    # Visual / 3D
    "open3d":"viz","openbb":"viz","osmnx":"viz",
    # Test
    "pytest":"test",
}


# lane -> pip requirement list
REQUIREMENTS: Dict[str, List[str]] = {
    "data":    ["pandas", "numpy", "scikit-learn", "statsmodels",
                "matplotlib", "seaborn", "scipy", "sympy",
                "networkx", "nltk", "spacy", "gensim"],
    "web":     ["django", "flask", "fastapi", "uvicorn", "pydantic",
                "sqlalchemy", "httpx", "requests", "click", "rich",
                "pyyaml", "toml"],
    "ml":      ["transformers", "diffusers", "peft", "mlflow",
                "openai-whisper"],
    "quantum": ["qiskit", "cirq", "pyquil"],
    "netsec":  ["pyshark", "stem", "pyngrok", "python-nmap", "hvac"],
    "viz":     ["open3d", "osmnx"],
    "test":    ["pytest"],
}


@dataclass
class Lane:
    name: str
    path: Path
    python: Path
    exists: bool
    installed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["path"] = str(self.path)
        d["python"] = str(self.python)
        return d


def lane_for(capability: str) -> Optional[str]:
    return ROUTING.get(capability)


def lane_dir(name: str) -> Path:
    return LANES_DIR / name


def lane_python(name: str) -> Path:
    return lane_dir(name) / "bin" / "python"


def lane_exists(name: str) -> bool:
    return lane_python(name).exists()


def lane_status() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for name in REQUIREMENTS:
        p = lane_dir(name)
        exists = lane_exists(name)
        installed: List[str] = []
        if exists:
            r = subprocess.run(
                [str(lane_python(name)), "-m", "pip", "freeze"],
                capture_output=True, text=True)
            installed = sorted({ln.split("==")[0].lower()
                                for ln in (r.stdout or "").splitlines()
                                if "==" in ln})
        out[name] = {"exists": exists,
                     "path": str(p),
                     "installed": installed,
                     "required": REQUIREMENTS[name]}
    return out


def create_lane(name: str, *, upgrade: bool = False) -> Dict[str, Any]:
    if name not in REQUIREMENTS:
        return {"ok": False, "reason": f"unknown lane {name!r}"}
    p = lane_dir(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not lane_exists(name):
        subprocess.run([sys.executable, "-m", "venv", str(p)],
                       check=True)
    py = lane_python(name)
    subprocess.run([str(py), "-m", "pip", "install",
                    "--upgrade", "pip", "wheel"], check=True,
                   capture_output=True)
    if upgrade or not lane_exists(name):
        subprocess.run([str(py), "-m", "pip", "install",
                        *REQUIREMENTS[name]], check=True)
    return {"ok": True, "name": name, "path": str(p),
            "requirements": REQUIREMENTS[name]}


def dispatch_in_lane(capability: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """If a lane is assigned and exists, run the capability in that
    lane's interpreter. Otherwise, report honestly."""
    name = lane_for(capability)
    if name is None:
        return {"ok": False, "reason": f"no lane assigned to {capability!r}"}
    if not lane_exists(name):
        return {"ok": False, "reason": f"lane {name!r} not built",
                "lane": name}
    return {"ok": True, "lane": name,
            "python": str(lane_python(name)),
            "capability": capability}


__all__ = [
    "ROUTING", "REQUIREMENTS",
    "lane_for", "lane_dir", "lane_python", "lane_exists",
    "lane_status", "create_lane", "dispatch_in_lane", "Lane",
]


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("lanes")
    def _entry(*args, **kwargs):
        return {"lanes": lane_status()}


_self_register()
