"""Process configuration.

Loaded lazily via get_settings(). Importing this module has no side effects.
All env vars are prefixed SOVEREIGN_ to avoid collisions in shared envs.
"""
from __future__ import annotations

import base64
import os
import stat
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsError(RuntimeError):
    """Raised when configuration is missing or invalid at startup."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SOVEREIGN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    node_id: str = Field(min_length=1, max_length=64)
    environment: Literal["dev", "staging", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    ed25519_private_key_path: Path | None = None
    encryption_salt: SecretStr | None = None
    tensor_swarm_port: int = Field(default=9001, ge=1, le=65535)

    @field_validator("node_id")
    @classmethod
    def _node_id_safe(cls, v: str) -> str:
        if any(c.isspace() for c in v):
            raise ValueError("node_id must not contain whitespace")
        return v

    @field_validator("ed25519_private_key_path")
    @classmethod
    def _key_path_ok(cls, v: Path | None) -> Path | None:
        if v is None:
            return None
        if not v.exists():
            raise ValueError(f"ed25519 private key not found: {v}")
        if not v.is_file():
            raise ValueError(f"ed25519 private key is not a file: {v}")
        if not os.access(v, os.R_OK):
            raise ValueError(f"ed25519 private key is not readable: {v}")

        # The invariant that actually matters: no group or world access bits.
        # This permits 0600, 0400, 0440, etc., and rejects 0644, 0666, 0640.
        # A service account that needs group access can chown appropriately;
        # we refuse anything looser than "owner-only".
        mode = stat.S_IMODE(v.stat().st_mode)
        if mode & 0o077:
            raise ValueError(
                f"ed25519 private key has group/world bits "
                f"{oct(mode)} (must be owner-only, e.g. 0600): {v}"
            )

        try:
            from cryptography.hazmat.primitives import serialization

            serialization.load_pem_private_key(v.read_bytes(), password=None)
        except Exception as e:  # noqa: BLE001 - re-raised with context
            raise ValueError(f"ed25519 private key is not a valid PEM private key: {e}") from e
        return v

    @field_validator("encryption_salt")
    @classmethod
    def _salt_ok(cls, v: SecretStr | None) -> SecretStr | None:
        if v is None:
            return None
        raw = v.get_secret_value()
        try:
            decoded = base64.b64decode(raw, validate=True)
        except Exception as e:  # noqa: BLE001
            raise ValueError("encryption_salt must be valid base64") from e
        if len(decoded) < 32:
            raise ValueError(
                f"encryption_salt must decode to >= 32 bytes (got {len(decoded)})"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache settings. Raises SettingsError with a one-line summary."""
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as e:
        missing = [str(err["loc"][0]) for err in e.errors() if err["type"] == "missing"]
        if missing:
            names = ", ".join(f"SOVEREIGN_{m.upper()}" for m in missing)
            raise SettingsError(f"missing required configuration: {names}") from e
        # Summarize non-missing errors on one line each
        summary = "; ".join(
            f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}"
            for err in e.errors()
        )
        raise SettingsError(f"invalid configuration: {summary}") from e


def reset_settings_cache() -> None:
    """For tests. Do not call in application code."""
    get_settings.cache_clear()
