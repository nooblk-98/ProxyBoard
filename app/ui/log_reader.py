import time
from pathlib import Path

from .constants import LOG_DIR

ACCESS_LOG = LOG_DIR / "access.log"
ERROR_LOG = LOG_DIR / "error.log"


def tail_file(path: Path, lines: int = 100) -> list[str]:
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return [l.rstrip() for l in all_lines[-lines:]]
    except Exception:
        return []


def stream_log(path: Path, poll_interval: float = 1.0):
    """Generator that yields new lines from a log file as SSE data."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        f.seek(0, 2)  # seek to end
        while True:
            line = f.readline()
            if line:
                yield f"data: {line.rstrip()}\n\n"
            else:
                time.sleep(poll_interval)
                yield ": ping\n\n"
