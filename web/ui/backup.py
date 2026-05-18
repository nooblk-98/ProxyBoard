import json
from datetime import datetime, timezone

from .constants import CONFIGS_PATH


def export_backup() -> tuple[str, str]:
    """Return (json_string, filename) for the current configs backup."""
    if CONFIGS_PATH.exists():
        data = CONFIGS_PATH.read_text(encoding="utf-8")
    else:
        data = json.dumps({"configs": []}, indent=2)
    filename = f"noobx-backup-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    return data, filename


def import_backup(raw: str) -> tuple[bool, str | list]:
    """Validate backup JSON and return parsed configs. Returns (ok, configs_or_error)."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    if not isinstance(payload, dict):
        return False, "Backup must be a JSON object."
    if "configs" not in payload:
        return False, "Missing 'configs' key — not a valid ProxyBoard backup."
    if not isinstance(payload["configs"], list):
        return False, "'configs' must be a list."

    return True, payload["configs"]
