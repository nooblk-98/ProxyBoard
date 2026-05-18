from .config_persistence import ConfigPersistence
from .constants import CONFIG_PATH, DATA_DIR
from .routes import create_app
from .system import ensure_certs, ensure_dirs
from .watchdog import start_watchdog
from .xray_config_builder import build_xray_config
from .xray_core import is_xray_running, start_xray


def bootstrap() -> None:
    ensure_dirs()
    persistence = ConfigPersistence(DATA_DIR)
    store = persistence.get_store()

    if not CONFIG_PATH.exists():
        for c in store.get("configs", []):
            ensure_certs(c["domain"])
        persistence.write_xray_config(build_xray_config(store.get("configs", [])))
    start_xray()
    start_watchdog(is_xray_running, start_xray)


def get_app():
    return create_app()
