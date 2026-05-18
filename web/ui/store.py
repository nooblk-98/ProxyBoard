def _coerce_int(value: str, field: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a number") from exc
    if number < 1 or number > 65535:
        raise ValueError(f"{field} must be 1-65535")
    return number


def _summary(item: dict) -> str:
    parts = []
    if item.get("ws_enabled"):
        parts.append(f"WS:{item.get('ws_port')}")
    if item.get("tls_enabled"):
        parts.append(f"WS+TLS:{item.get('tls_port')}")
    return " | ".join(parts) if parts else "Disabled"
