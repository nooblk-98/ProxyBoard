from .constants import DEFAULTS


def build_xray_config(configs: list) -> dict:
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
                "id": form.get("ws_uuid", ""),
                "level": 0,
                "email": form.get("ws_email", ""),
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
                "id": form.get("tls_uuid", ""),
                "level": 0,
                "email": form.get("tls_email", ""),
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
