"""
Aether Sovereign Fabric — Local Envelope Secrets Manager
Manages encrypted secrets and signing keys for node identity.
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
import json
from typing import Optional

class SovereignSecretsManager:
    def __init__(self, key_path: str = "storage/master.key", vault_path: str = "storage/secrets.enc"):
        self.key_path = Path(key_path)
        self.vault_path = Path(vault_path)
        self._init_vault()

    def _init_vault(self) -> None:
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)

        self.cipher = Fernet(self.key_path.read_bytes())
        if not self.vault_path.exists():
            self._save_vault({})

    def _load_vault(self) -> dict:
        if not self.vault_path.exists():
            return {}
        decrypted_data = self.cipher.decrypt(self.vault_path.read_bytes())
        return json.loads(decrypted_data.decode("utf-8"))

    def _save_vault(self, data: dict) -> None:
        encrypted_data = self.cipher.encrypt(json.dumps(data).encode("utf-8"))
        self.vault_path.write_bytes(encrypted_data)

    def set_secret(self, key: str, value: str) -> None:
        vault = self._load_vault()
        vault[key] = value
        self._save_vault(vault)

    def get_secret(self, key: str) -> Optional[str]:
        vault = self._load_vault()
        return vault.get(key)
