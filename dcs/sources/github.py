"""GitHub source — attestations from the GitHub REST API."""

from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
import os  # pragma: no cover
import urllib.request  # pragma: no cover
from typing import Any  # pragma: no cover

from dcs.sources import Attestation, B, source  # pragma: no cover

API = "https://api.github.com"


def _get(path: str) -> tuple[bool, Any]:  # pragma: no cover
    tok = os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if tok:  # pragma: no cover
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return True, json.load(r)  # pragma: no cover
    except Exception as e:  # pragma: no cover
        return False, str(e)  # pragma: no cover


def _repo() -> str | None:  # pragma: no cover
    return os.environ.get("DCS_REPO")  # pragma: no cover


@source("DCS-DA-001")
def readme_present() -> Attestation:  # pragma: no cover
    repo = _repo()
    if not repo:  # pragma: no cover
        return Attestation("DCS-DA-001", B.U, "github", "DCS_REPO not set")  # pragma: no cover
    ok, data = _get(f"/repos/{repo}/readme")
    if not ok:  # pragma: no cover
        return Attestation("DCS-DA-001", B.U, "github", f"api: {data}")  # pragma: no cover
    return Attestation(  # pragma: no cover
        "DCS-DA-001", B.T, "github", "readme present", {"url": data.get("html_url", "")}
    )


@source("DCS-AUT-001")
def workflows_present() -> Attestation:  # pragma: no cover
    repo = _repo()
    if not repo:  # pragma: no cover
        return Attestation("DCS-AUT-001", B.U, "github", "DCS_REPO not set")  # pragma: no cover
    ok, data = _get(f"/repos/{repo}/contents/.github/workflows")
    if not ok:  # pragma: no cover
        return Attestation("DCS-AUT-001", B.U, "github", f"api: {data}")  # pragma: no cover
    if not isinstance(data, list):  # pragma: no cover
        return Attestation("DCS-AUT-001", B.F, "github", "no workflows directory")  # pragma: no cover
    return Attestation(  # pragma: no cover
        "DCS-AUT-001", B.T, "github", f"{len(data)} workflow(s) present", {"count": len(data)}
    )


@source("DCS-COH-001")
def default_branch() -> Attestation:  # pragma: no cover
    repo = _repo()
    if not repo:  # pragma: no cover
        return Attestation("DCS-COH-001", B.U, "github", "DCS_REPO not set")  # pragma: no cover
    ok, data = _get(f"/repos/{repo}")
    if not ok:  # pragma: no cover
        return Attestation("DCS-COH-001", B.U, "github", f"api: {data}")  # pragma: no cover
    return Attestation("DCS-COH-001", B.T, "github", f"default: {data.get('default_branch', '')}")  # pragma: no cover
