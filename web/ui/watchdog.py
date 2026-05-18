import logging
import threading

logger = logging.getLogger(__name__)

_watchdog_thread: threading.Thread | None = None
_stop_event = threading.Event()


def start_watchdog(is_running_fn, restart_fn, interval: int = 10) -> None:
    global _watchdog_thread, _stop_event
    _stop_event.clear()

    def _loop():
        while not _stop_event.wait(interval):
            try:
                if not is_running_fn():
                    restart_fn()
            except Exception:
                logger.warning("watchdog iteration failed", exc_info=True)

    _watchdog_thread = threading.Thread(target=_loop, daemon=True, name="xray-watchdog")
    _watchdog_thread.start()


def stop_watchdog() -> None:
    _stop_event.set()
