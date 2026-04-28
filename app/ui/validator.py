import json
import subprocess
import tempfile
from pathlib import Path

from .constants import XRAY_BIN


def validate_config(config: dict) -> tuple[bool, str]:
    """Run xray --test against config dict. Returns (ok, message)."""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f, indent=2)
            tmp_path = Path(f.name)

        result = subprocess.run(
            [str(XRAY_BIN), "-test", "-c", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        tmp_path.unlink(missing_ok=True)

        if result.returncode == 0:
            return True, "Configuration is valid."
        output = (result.stdout + result.stderr).strip()
        return False, output or "Xray reported an invalid configuration."
    except FileNotFoundError:
        return False, "Xray binary not found — cannot validate."
    except subprocess.TimeoutExpired:
        return False, "Validation timed out."
    except Exception as e:
        return False, f"Validation error: {e}"
