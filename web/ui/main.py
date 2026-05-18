from .constants import CONFIG_PATH
from .routes import create_app
from .store import _load_store, build_config, write_config
from .system import ensure_dirs, ensure_certs
from .watchdog import start_watchdog
from .xray_core import is_xray_running, start_xray


def bootstrap() -> None:
    ensure_dirs()
    store = _load_store()

    if not CONFIG_PATH.exists():
        for c in store.get("configs", []):
            ensure_certs(c["domain"])
        write_config(build_config(store.get("configs", [])))
    start_xray()
    start_watchdog(is_xray_running, start_xray)


def get_app():
    return create_app()
