import json
from pathlib import Path
from uuid import uuid4

import pytest


def _make_sample_config(overrides: dict | None = None) -> dict:
    cfg = {
        "id": str(uuid4()),
        "name": "Test Config",
        "domain": "test.example.com",
        "protocol": "vless",
        "enabled": True,
        "ws_enabled": True,
        "ws_port": 8080,
        "ws_path": "/ws",
        "ws_uuid": str(uuid4()),
        "ws_email": "test@example.com",
        "ws_host": "test.example.com",
        "tls_enabled": True,
        "tls_port": 8443,
        "tls_path": "/wstls",
        "tls_uuid": str(uuid4()),
        "tls_email": "test-tls@example.com",
        "tls_cert": "/data/certs/cert.pem",
        "tls_key": "/data/certs/key.pem",
        "tls_host": "test.example.com",
        "dns": "1.1.1.1",
        "fingerprint": "randomized",
        "alpn": "h2,h3,http/1.1",
    }
    if overrides:
        cfg.update(overrides)
    return cfg


@pytest.fixture
def sample_config():
    return _make_sample_config()


@pytest.fixture
def sample_config_vmess():
    return _make_sample_config({"protocol": "vmess"})


@pytest.fixture
def sample_config_ws_only():
    return _make_sample_config({"tls_enabled": False})


@pytest.fixture
def sample_config_tls_only():
    return _make_sample_config({"ws_enabled": False})


@pytest.fixture
def temp_data_dir(tmp_path) -> Path:
    dd = tmp_path / "data"
    dd.mkdir()
    return dd


@pytest.fixture
def store_with_configs(temp_data_dir) -> dict:
    """Write a configs.json with 2 sample configs and return the store."""
    configs = [
        _make_sample_config({"id": "cfg-1", "name": "Alpha", "ws_port": 10001, "tls_port": 10002}),
        _make_sample_config({"id": "cfg-2", "name": "Beta", "ws_port": 10003, "tls_port": 10004}),
    ]
    store = {"configs": configs}
    path = temp_data_dir / "configs.json"
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return store
