import json
import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from .constants import DEFAULTS
from .system import ensure_certs, ensure_dirs
from .xray_config_builder import build_xray_config
from .xray_core import start_xray

logger = logging.getLogger(__name__)


@dataclass
class Result:
    success: bool
    message: str = ""


class ConfigPersistence:
    def __init__(self, data_dir: str | Path):
        data_dir = Path(data_dir)
        self._configs_path = data_dir / "configs.json"
        self._config_path = data_dir / "config.json"

    # ── internal helpers ──────────────────────────────────────────

    def _load_store(self) -> dict:
        path = self._configs_path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            default_item = dict(DEFAULTS)
            default_item["id"] = str(uuid4())
            default_item["enabled"] = True
            store = {"configs": [default_item]}
            path.write_text(json.dumps(store, indent=2), encoding="utf-8")
            return store
        try:
            store = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            path.parent.mkdir(parents=True, exist_ok=True)
            default_item = dict(DEFAULTS)
            default_item["id"] = str(uuid4())
            default_item["enabled"] = True
            store = {"configs": [default_item]}
            path.write_text(json.dumps(store, indent=2), encoding="utf-8")
            return store

        migrated = False
        for c in store.get("configs", []):
            if "enabled" not in c:
                c["enabled"] = (c.get("id") == store.get("active_id", ""))
                migrated = True
        if migrated:
            self._save_store(store)
        return store

    def _save_store(self, store: dict) -> None:
        self._configs_path.parent.mkdir(parents=True, exist_ok=True)
        self._configs_path.write_text(json.dumps(store, indent=2), encoding="utf-8")

    def _find_config(self, store: dict, config_id: str) -> dict | None:
        for item in store.get("configs", []):
            if item.get("id") == config_id:
                return item
        return None

    def _write_xray_config(self, config: dict) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def _validate_ports(self, config: dict, store: dict, config_id: str | None = None) -> str | None:
        if not config.get("ws_enabled") and not config.get("tls_enabled"):
            return "Enable at least one inbound."

        if config.get("ws_enabled") and config.get("tls_enabled") and config["ws_port"] == config["tls_port"]:
            return "WS and TLS ports must be different within the same config."

        for other in store.get("configs", []):
            if other.get("id") == config_id:
                continue
            name = other.get("name", "")
            if config.get("ws_enabled") and other.get("ws_enabled") and config["ws_port"] == other.get("ws_port"):
                return f"Port {config['ws_port']} is already used by '{name}'"
            if config.get("tls_enabled") and other.get("tls_enabled") and config["tls_port"] == other.get("tls_port"):
                return f"Port {config['tls_port']} is already used by '{name}'"
            if config.get("ws_enabled") and other.get("tls_enabled") and config["ws_port"] == other.get("tls_port"):
                return f"Port {config['ws_port']} is already used by '{name}'"
            if config.get("tls_enabled") and other.get("ws_enabled") and config["tls_port"] == other.get("ws_port"):
                return f"Port {config['tls_port']} is already used by '{name}'"

        return None

    def _commit(self, store: dict) -> Result:
        ensure_dirs()
        for c in store.get("configs", []):
            if c.get("enabled", True):
                ensure_certs(c["domain"])
        xray_cfg = build_xray_config(store.get("configs", []))
        self._write_xray_config(xray_cfg)
        self._save_store(store)
        start_xray()
        return Result(True, "Config saved and Xray restarted.")

    # ── public API ────────────────────────────────────────────────

    def get_store(self) -> dict:
        return self._load_store()

    def read_xray_config(self) -> str:
        if not self._config_path.exists():
            return ""
        return self._config_path.read_text(encoding="utf-8")

    def write_xray_config(self, config: dict) -> None:
        self._write_xray_config(config)

    def add(self, config: dict) -> Result:
        store = self._load_store()
        error = self._validate_ports(config, store)
        if error:
            return Result(False, error)
        config["id"] = config.get("id") or str(uuid4())
        config["enabled"] = True
        store.setdefault("configs", []).append(config)
        return self._commit(store)

    def update(self, config_id: str, fields: dict) -> Result:
        store = self._load_store()
        existing = self._find_config(store, config_id)
        if not existing:
            return Result(False, "Config not found.")
        merged = dict(existing)
        merged.update(fields)
        error = self._validate_ports(merged, store, config_id)
        if error:
            return Result(False, error)
        existing.update(fields)
        return self._commit(store)

    def delete(self, config_id: str) -> Result:
        store = self._load_store()
        original_len = len(store.get("configs", []))
        if original_len <= 1:
            return Result(False, "Cannot delete the last configuration. At least one config must exist.")
        store["configs"] = [c for c in store.get("configs", []) if c.get("id") != config_id]
        if len(store["configs"]) >= original_len:
            return Result(False, "Config not found.")
        result = self._commit(store)
        result.message = "Config deleted."
        return result

    def toggle(self, config_id: str) -> Result:
        store = self._load_store()
        item = self._find_config(store, config_id)
        if not item:
            return Result(False, "Config not found.")
        item["enabled"] = not item.get("enabled", True)
        label = "enabled" if item["enabled"] else "disabled"
        result = self._commit(store)
        result.message = f"Config {label}."
        return result

    def replace_all(self, configs: list[dict]) -> Result:
        store = {"configs": configs}
        return self._commit(store)
