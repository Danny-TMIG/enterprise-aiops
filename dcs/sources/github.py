"""GitHub source — attestations from the GitHub REST API."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from dcs.sources import Attestation, B, source

API = "https://api.github.com"


def _get(path: str) -> tuple[bool, Any]:
    tok = os.environ.get("GITHUB_TOKEN", "")
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return True, json.load(r)
    except Exception as e:
        return False, str(e)


def _repo() -> str | None:
    return os.environ.get("DCS_REPO")


@source("DCS-DA-001")
def readme_present() -> Attestation:
    repo = _repo()
    if not repo:
        return Attestation("DCS-DA-001", B.U, "github", "DCS_REPO not set")
    ok, data = _get(f"/repos/{repo}/readme")
    if not ok:
        return Attestation("DCS-DA-001", B.U, "github", f"api: {data}")
    return Attestation(
        "DCS-DA-001", B.T, "github", "readme present", {"url": data.get("html_url", "")}
    )


@source("DCS-AUT-001")
def workflows_present() -> Attestation:
    repo = _repo()
    if not repo:
        return Attestation("DCS-AUT-001", B.U, "github", "DCS_REPO not set")
    ok, data = _get(f"/repos/{repo}/contents/.github/workflows")
    if not ok:
        return Attestation("DCS-AUT-001", B.U, "github", f"api: {data}")
    if not isinstance(data, list):
        return Attestation("DCS-AUT-001", B.F, "github", "no workflows directory")
    return Attestation(
        "DCS-AUT-001", B.T, "github", f"{len(data)} workflow(s) present", {"count": len(data)}
    )


@source("DCS-COH-001")
def default_branch() -> Attestation:
    repo = _repo()
    if not repo:
        return Attestation("DCS-COH-001", B.U, "github", "DCS_REPO not set")
    ok, data = _get(f"/repos/{repo}")
    if not ok:
        return Attestation("DCS-COH-001", B.U, "github", f"api: {data}")
    return Attestation("DCS-COH-001", B.T, "github", f"default: {data.get('default_branch', '')}")
