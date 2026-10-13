"""Connectors — one adapter per SaaS tool.

A connector exposes a small set of capabilities (sense / act /
coordinate / allocate / verify / learn). By default all work is
local. A real HTTP call happens only when MURMUR_LIVE=1 AND the
tool's env var is set. Nothing is fetched by default.
"""
from __future__ import annotations

import json
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LOG_PATH = Path(".murmur/connectors.jsonl")


def _log(tool: str, verb: str, payload: dict[str, Any], ok: bool,
         detail: str = "") -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": time.time(), "tool": tool, "verb": verb,
           "payload": payload, "ok": ok, "detail": detail}
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def _live() -> bool:
    return os.environ.get("MURMUR_LIVE") == "1"


def _post(url: str, payload: dict[str, Any], timeout: float = 5.0) -> bool:
    try:
        import urllib.request
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


@dataclass
class Connector:
    name: str
    category: str
    env_key: str = ""
    capabilities: list[str] = field(default_factory=list)
    local: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None

    def remote_url(self) -> str | None:
        if not self.env_key:
            return None
        return os.environ.get(self.env_key)

    def call(self, verb: str, payload: dict[str, Any]) -> dict[str, Any]:
        if verb not in self.capabilities:
            return {"ok": False, "detail": "unsupported verb"}

        if _live() and self.remote_url():
            ok = _post(self.remote_url(), {"verb": verb, "payload": payload})
            _log(self.name, verb, payload, ok, "remote")
            return {"ok": ok, "detail": "remote"}

        if self.local:
            try:
                result = self.local(verb, payload)
                _log(self.name, verb, payload, True, "local")
                return {"ok": True, "result": result, "detail": "local"}
            except Exception as e:
                _log(self.name, verb, payload, False, type(e).__name__)
                return {"ok": False, "detail": type(e).__name__}

        _log(self.name, verb, payload, True, "noop")
        return {"ok": True, "detail": "noop"}


# ── local implementations ─────────────────────────────────────
def _pass(verb, payload):
    return {"verb": verb, "echo": payload.get("summary", "")}


def _metric(verb, payload):
    return {"value": float(payload.get("value", 0.0))}


def _issue(verb, payload):
    return {"id": f"murmur-{int(time.time()*1000)}",
            "title": payload.get("summary", "murmur action")}


def _message(verb, payload):
    return {"sent_to": payload.get("channel", "default"),
            "text": payload.get("summary", "")}


# ── the 46-tool registry ──────────────────────────────────────
def _reg() -> dict[str, Connector]:
    tools: list[dict[str, Any]] = [
        # observability / product / analytics
        ("Amplitude",   "observability", "AMPLITUDE_KEY",   _metric),
        ("Mixpanel",    "observability", "MIXPANEL_TOKEN",  _metric),
        ("Hex",         "observability", "HEX_API_KEY",     _metric),
        ("Databricks",  "observability", "DATABRICKS_HOST", _metric),
        ("Snowflake",   "observability", "SNOWFLAKE_DSN",   _metric),
        ("Tableau",     "observability", "TABLEAU_URL",     _metric),
        # CRM / sales
        ("Apollo",      "crm",           "APOLLO_API_KEY",  _pass),
        ("Clay",        "crm",           "CLAY_API_KEY",    _pass),
        ("HubSpot",     "crm",           "HUBSPOT_TOKEN",   _issue),
        ("LinkedIn",    "crm",           "LINKEDIN_TOKEN",  _message),
        ("Outreach",    "crm",           "OUTREACH_TOKEN",  _message),
        ("Salesloft",   "crm",           "SALESLOFT_TOKEN", _message),
        ("Salesforce",  "crm",           "SALESFORCE_URL",  _issue),
        ("ZoomInfo",    "crm",           "ZOOMINFO_KEY",    _pass),
        # support
        ("Intercom",    "support",       "INTERCOM_TOKEN",  _message),
        ("Zendesk",     "support",       "ZENDESK_URL",     _issue),
        # comms / collaboration
        ("Slack",       "comms",         "SLACK_WEBHOOK",   _message),
        ("Zoom",        "comms",         "ZOOM_TOKEN",      _pass),
        ("Loom",        "comms",         "LOOM_TOKEN",      _pass),
        ("Mailchimp",   "comms",         "MAILCHIMP_KEY",   _message),
        # dev / work
        ("GitHub",      "dev",           "GITHUB_TOKEN",    _issue),
        ("Vercel",      "dev",           "VERCEL_TOKEN",    _pass),
        ("Jira",        "dev",           "JIRA_URL",        _issue),
        ("ClickUp",     "dev",           "CLICKUP_TOKEN",   _issue),
        ("Trello",      "dev",           "TRELLO_KEY",      _issue),
        ("monday.com",  "dev",           "MONDAY_TOKEN",    _issue),
        ("Notion",      "dev",           "NOTION_TOKEN",    _pass),
        ("Nooks",       "crm",           "NOOKS_TOKEN",     _pass),
        # HR
        ("Greenhouse",  "hr",            "GREENHOUSE_KEY",  _pass),
        ("Rippling",    "hr",            "RIPPLING_TOKEN",  _pass),
        ("Workday",     "hr",            "WORKDAY_URL",     _pass),
        # finance
        ("Stripe",      "finance",       "STRIPE_KEY",      _metric),
        ("QuickBooks",  "finance",       "QBO_TOKEN",       _pass),
        ("Ramp",        "finance",       "RAMP_TOKEN",      _pass),
        ("NetSuite",    "finance",       "NETSUITE_URL",    _pass),
        ("Shopify",     "finance",       "SHOPIFY_TOKEN",   _metric),
        # office / docs
        ("Google",      "office",        "GOOGLE_TOKEN",    _pass),
        ("Microsoft 365", "office",      "MS365_TOKEN",     _pass),
        ("Dropbox",     "office",        "DROPBOX_TOKEN",   _pass),
        ("Box",         "office",        "BOX_TOKEN",       _pass),
        ("DocuSign",    "office",        "DOCUSIGN_KEY",    _pass),
        ("Calendly",    "office",        "CALENDLY_KEY",    _pass),
        ("Canva",       "office",        "CANVA_TOKEN",     _pass),
        ("Figma",       "office",        "FIGMA_TOKEN",     _pass),
        # misc / data
        ("Ashby",       "data",          "ASHBY_KEY",       _pass),
    ]
    out: dict[str, Connector] = {}
    for name, cat, env, impl in tools:
        out[name] = Connector(
            name=name, category=cat, env_key=env,
            capabilities=["sense", "interpret", "act",
                          "coordinate", "allocate",
                          "verify", "learn"],
            local=impl,
        )
    return out


REGISTRY: dict[str, Connector] = _reg()


def list_tools() -> list[str]:
    return sorted(REGISTRY)


def by_category() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name, c in REGISTRY.items():
        out.setdefault(c.category, []).append(name)
    return {k: sorted(v) for k, v in out.items()}


def call(tool: str, verb: str, payload: dict[str, Any]) -> dict[str, Any]:
    c = REGISTRY.get(tool)
    if not c:
        return {"ok": False, "detail": "unknown tool"}
    return c.call(verb, payload)
