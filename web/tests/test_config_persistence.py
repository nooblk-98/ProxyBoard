from unittest.mock import patch

import pytest
from ui.config_persistence import ConfigPersistence


@pytest.fixture
def persistence(temp_data_dir):
    with (
        patch("ui.config_persistence.start_xray"),
        patch("ui.config_persistence.ensure_certs"),
        patch("ui.config_persistence.ensure_dirs"),
    ):
        yield ConfigPersistence(str(temp_data_dir))


class TestConfigPersistence:
    def test_get_store_creates_default_if_missing(self, persistence):
        store = persistence.get_store()
        assert "configs" in store
        assert len(store["configs"]) == 1
        assert store["configs"][0]["enabled"] is True

    def test_get_store_returns_saved_data(self, persistence, store_with_configs):
        store = persistence.get_store()
        assert len(store["configs"]) == 2
        names = {c["name"] for c in store["configs"]}
        assert names == {"Alpha", "Beta"}

    # ── add ──────────────────────────────────────────────────────

    def test_add_config(self, persistence, sample_config):
        result = persistence.add(sample_config)
        assert result.success is True
        store = persistence.get_store()
        assert len(store["configs"]) == 2  # default + new

    def test_add_config_port_collision_ws(self, persistence):
        sample_config = {
            "id": "new-cfg", "name": "Collider",
            "ws_enabled": True, "ws_port": 10001, "tls_enabled": False,
        }
        persistence._load_store = lambda: {
            "configs": [
                {
                    "id": "existing", "name": "Existing",
                    "ws_enabled": True, "ws_port": 10001, "tls_enabled": False,
                }
            ]
        }
        persistence._save_store = lambda s: None
        result = persistence.add(sample_config)
        assert result.success is False
        assert "10001" in result.message

    def test_add_config_no_transport(self, persistence):
        result = persistence.add({"ws_enabled": False, "tls_enabled": False})
        assert result.success is False
        assert "Enable at least one" in result.message

    # ── update ───────────────────────────────────────────────────

    def test_update_config(self, persistence, store_with_configs):
        result = persistence.update("cfg-1", {"name": "Alpha Updated"})
        assert result.success is True
        store = persistence.get_store()
        updated = next(c for c in store["configs"] if c["id"] == "cfg-1")
        assert updated["name"] == "Alpha Updated"

    def test_update_nonexistent_config(self, persistence):
        result = persistence.update("nonexistent", {"name": "Nope"})
        assert result.success is False
        assert "not found" in result.message.lower()

    def test_update_port_collision(self, persistence, store_with_configs):
        fields = {"ws_enabled": True, "ws_port": 10003, "tls_enabled": False}
        result = persistence.update("cfg-1", fields)
        assert result.success is False
        assert "10003" in result.message

    def test_update_preserves_enabled_status(self, persistence, store_with_configs):
        result = persistence.update("cfg-1", {"name": "Still Enabled"})
        assert result.success is True
        store = persistence.get_store()
        updated = next(c for c in store["configs"] if c["id"] == "cfg-1")
        assert updated["enabled"] is True

    # ── delete ───────────────────────────────────────────────────

    def test_delete_config(self, persistence, store_with_configs):
        result = persistence.delete("cfg-1")
        assert result.success is True
        store = persistence.get_store()
        assert len(store["configs"]) == 1

    def test_delete_last_config_refused(self, persistence):
        result = persistence.delete("nonexistent")  # only default = 1 config
        assert result.success is False
        assert "last configuration" in result.message.lower()

    def test_delete_nonexistent(self, persistence, store_with_configs):
        result = persistence.delete("nonexistent")
        assert result.success is False

    # ── toggle ───────────────────────────────────────────────────

    def test_toggle_config(self, persistence, store_with_configs):
        result = persistence.toggle("cfg-1")
        assert result.success is True
        store = persistence.get_store()
        toggled = next(c for c in store["configs"] if c["id"] == "cfg-1")
        assert toggled["enabled"] is False

    def test_toggle_back(self, persistence, store_with_configs):
        persistence.toggle("cfg-1")
        result = persistence.toggle("cfg-1")
        assert result.success is True
        store = persistence.get_store()
        toggled = next(c for c in store["configs"] if c["id"] == "cfg-1")
        assert toggled["enabled"] is True

    def test_toggle_nonexistent(self, persistence):
        result = persistence.toggle("nonexistent")
        assert result.success is False

    # ── replace_all ──────────────────────────────────────────────

    def test_replace_all(self, persistence, store_with_configs, sample_config):
        result = persistence.replace_all([sample_config])
        assert result.success is True
        store = persistence.get_store()
        assert len(store["configs"]) == 1
        assert store["configs"][0]["name"] == "Test Config"

    def test_replace_all_empty(self, persistence):
        result = persistence.replace_all([])
        assert result.success is True
        store = persistence.get_store()
        assert len(store["configs"]) == 0

    # ── read_xray_config ─────────────────────────────────────────

    def test_read_xray_config_missing(self, persistence):
        assert persistence.read_xray_config() == ""

    def test_read_xray_config_present(self, persistence, temp_data_dir):
        path = temp_data_dir / "config.json"
        path.write_text('{"test": true}', encoding="utf-8")
        assert persistence.read_xray_config() == '{"test": true}'

    # ── write_xray_config ────────────────────────────────────────

    def test_write_xray_config(self, persistence, temp_data_dir):
        persistence.write_xray_config({"hello": "world"})
        path = temp_data_dir / "config.json"
        assert path.exists()
        import json
        assert json.loads(path.read_text(encoding="utf-8")) == {"hello": "world"}

    # ── validation edge cases ───────────────────────────────────

    def test_same_ws_tls_port_rejected(self, persistence):
        config = {
            "id": "x", "ws_enabled": True, "ws_port": 8080,
            "tls_enabled": True, "tls_port": 8080,
        }
        store = {"configs": []}
        error = persistence._validate_ports(config, store)
        assert error is not None
        assert "same config" in error.lower()
