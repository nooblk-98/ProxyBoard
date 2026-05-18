import json
from pathlib import Path
from uuid import uuid4

from .constants import CONFIG_PATH, CONFIGS_PATH, DEFAULTS, DOMAIN


def _coerce_int(value: str, field: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a number") from exc
    if number < 1 or number > 65535:
        raise ValueError(f"{field} must be 1-65535")
    return number


def _load_store() -> dict:
    if not CONFIGS_PATH.exists():
        default_item = dict(DEFAULTS)
        default_item["id"] = str(uuid4())
        default_item["enabled"] = True
        store = {"configs": [default_item]}
        CONFIGS_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")
        return store
    try:
        store = json.loads(CONFIGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        default_item = dict(DEFAULTS)
        default_item["id"] = str(uuid4())
        default_item["enabled"] = True
        store = {"configs": [default_item]}
        CONFIGS_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")
        return store

    migrated = False
    for c in store.get("configs", []):
        if "enabled" not in c:
            c["enabled"] = (c.get("id") == store.get("active_id", ""))
            migrated = True
    if migrated:
        _save_store(store)
    return store


def _save_store(store: dict) -> None:
    CONFIGS_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _find_config(store: dict, config_id: str) -> dict | None:
    for item in store.get("configs", []):
        if item.get("id") == config_id:
            return item
    return None


def _summary(item: dict) -> str:
    parts = []
    if item.get("ws_enabled"):
        parts.append(f"WS:{item.get('ws_port')}")
    if item.get("tls_enabled"):
        parts.append(f"WS+TLS:{item.get('tls_port')}")
    return " | ".join(parts) if parts else "Disabled"


def build_config(configs: list) -> dict:
    inbounds = []
    dns_server = DEFAULTS["dns"]
    for form in configs:
        if not form.get("enabled", True):
            continue

        if dns_server == DEFAULTS["dns"] and form.get("dns"):
            dns_server = form["dns"]

        domain = form["domain"]
        ws_enabled = form.get("ws_enabled", False)
        tls_enabled = form.get("tls_enabled", False)
        ws_host = form.get("ws_host", domain)
        tls_host = form.get("tls_host", domain)
        protocol = form.get("protocol", "vless")
        cid = form.get("id", "")

        if ws_enabled:
            ws_client = {
                "id": form["ws_uuid"],
                "level": 0,
                "email": form["ws_email"],
            }
            if protocol == "vmess":
                ws_client["alterId"] = 0
            inbounds.append(
                {
                    "port": form["ws_port"],
                    "listen": "0.0.0.0",
                    "protocol": protocol,
                    "tag": f"ws-{cid}",
                    "settings": {
                        "clients": [ws_client],
                        **({"decryption": "none"} if protocol == "vless" else {}),
                    },
                    "streamSettings": {
                        "network": "ws",
                        "wsSettings": {
                            "path": form["ws_path"],
                            "host": ws_host,
                        },
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"],
                        "metadataOnly": False,
                    },
                }
            )

        if tls_enabled:
            tls_client = {
                "id": form["tls_uuid"],
                "level": 0,
                "email": form["tls_email"],
            }
            if protocol == "vmess":
                tls_client["alterId"] = 0
            inbounds.append(
                {
                    "port": form["tls_port"],
                    "listen": "0.0.0.0",
                    "protocol": protocol,
                    "tag": f"ws-tls-{cid}",
                    "settings": {
                        "clients": [tls_client],
                        **({"decryption": "none"} if protocol == "vless" else {}),
                    },
                    "streamSettings": {
                        "network": "ws",
                        "security": "tls",
                        "tlsSettings": {
                            "serverName": tls_host,
                            "certificates": [
                                {
                                    "certificateFile": form["tls_cert"],
                                    "keyFile": form["tls_key"],
                                }
                            ],
                            "minVersion": "1.2",
                            "maxVersion": "1.3",
                            "cipherSuites": "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256",
                            "fingerprint": form.get("fingerprint", "randomized"),
                            "alpn": [s.strip() for s in form.get("alpn", "h2,h3,http/1.1").split(",")],
                            "allowInsecure": False,
                        },
                        "wsSettings": {
                            "path": form["tls_path"],
                            "host": tls_host,
                        },
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"],
                        "metadataOnly": False,
                    },
                }
            )

    inbounds.append(
        {
            "listen": "127.0.0.1",
            "port": 10085,
            "protocol": "dokodemo-door",
            "settings": {
                "address": "127.0.0.1"
            },
            "tag": "api"
        }
    )

    return {
        "log": {
            "loglevel": "info",
            "access": "/data/logs/access.log",
            "error": "/data/logs/error.log",
        },
        "api": {
            "tag": "api",
            "services": ["StatsService"]
        },
        "stats": {},
        "policy": {
            "levels": {
                "0": {
                    "statsUserUplink": True,
                    "statsUserDownlink": True
                }
            },
            "system": {
                "statsInboundUplink": True,
                "statsInboundDownlink": True,
                "statsOutboundUplink": True,
                "statsOutboundDownlink": True
            }
        },
        "inbounds": inbounds,
        "outbounds": [
            {"protocol": "freedom", "settings": {}, "tag": "direct"},
            {"protocol": "blackhole", "settings": {}, "tag": "blocked"},
        ],
        "dns": {
            "servers": [
                {
                    "address": dns_server,
                    "port": 53
                }
            ]
        },
        "routing": {
            "domainStrategy": "IPOnDemand",
            "rules": [
                {"type": "field", "inboundTag": ["api"], "outboundTag": "api"},
                {"type": "field", "domain": ["geosite:private"], "outboundTag": "blocked"},
                {"type": "field", "ip": ["geoip:private"], "outboundTag": "blocked"},
            ],
        },
    }


def read_config_text() -> str:
    if not CONFIG_PATH.exists():
        return ""
    return CONFIG_PATH.read_text(encoding="utf-8")


def write_config(config: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
