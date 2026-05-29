import os
import json
import tempfile
import pytest
from core.config import Config


@pytest.fixture
def tmp_config(tmp_path):
    """Create a Config with a temporary config file."""
    config_file = str(tmp_path / "test_config.json")
    return Config(config_file=config_file)


@pytest.fixture
def config_with_data(tmp_path):
    """Create a Config pre-populated with test data."""
    config_file = str(tmp_path / "test_config.json")
    data = {
        "version": "1.0.0",
        "scan": {"max_threads": 50, "timeout": 3.0},
        "intel": {"nvd_api_key": "test-key-123", "shodan_api_key": ""},
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return Config(config_file=config_file)


class TestConfigDefaults:
    def test_default_version(self, tmp_config):
        assert tmp_config.get("version") == "2.0.0"

    def test_default_scan_threads(self, tmp_config):
        assert tmp_config.get("scan.max_threads") == 100

    def test_default_scan_timeout(self, tmp_config):
        assert tmp_config.get("scan.timeout") == 2.0

    def test_default_proxy_disabled(self, tmp_config):
        assert tmp_config.get("proxy.enabled") is False

    def test_default_verify_ssl(self, tmp_config):
        assert tmp_config.get("verify_ssl") is False

    def test_default_theme(self, tmp_config):
        assert tmp_config.get("ui.theme") == "aero"


class TestConfigGetSet:
    def test_get_nested_key(self, tmp_config):
        assert tmp_config.get("scan.max_threads") == 100

    def test_get_missing_key_returns_default(self, tmp_config):
        assert tmp_config.get("nonexistent.key", "fallback") == "fallback"

    def test_get_missing_key_no_default(self, tmp_config):
        assert tmp_config.get("nonexistent.key") is None

    def test_set_and_get(self, tmp_config):
        tmp_config.set("scan.max_threads", 200)
        assert tmp_config.get("scan.max_threads") == 200

    def test_set_creates_nested(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        cfg = Config(config_file=config_file)
        cfg.set("new.nested.key", "value")
        assert cfg.get("new.nested.key") == "value"

    def test_set_persists(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        cfg = Config(config_file=config_file)
        cfg.set("scan.max_threads", 500)

        # Reload from disk
        cfg2 = Config(config_file=config_file)
        assert cfg2.get("scan.max_threads") == 500


class TestConfigLoad:
    def test_load_user_config(self, config_with_data):
        assert config_with_data.get("version") == "1.0.0"
        assert config_with_data.get("scan.max_threads") == 50

    def test_load_missing_file(self, tmp_path):
        config_file = str(tmp_path / "nonexistent.json")
        cfg = Config(config_file=config_file)
        assert cfg.get("version") == "2.0.0"  # defaults

    def test_load_invalid_json(self, tmp_path):
        config_file = str(tmp_path / "bad.json")
        with open(config_file, "w") as f:
            f.write("{invalid json")
        cfg = Config(config_file=config_file)
        assert cfg.get("version") == "2.0.0"  # defaults

    def test_deep_merge_preserves_defaults(self, config_with_data):
        # scan.web_timeout should come from defaults since not in user config
        assert config_with_data.get("scan.web_timeout") == 10


class TestConfigValidate:
    def test_validate_valid_config(self, tmp_config):
        errors = tmp_config.validate()
        assert errors == []

    def test_validate_fixes_bad_threads(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        with open(config_file, "w") as f:
            json.dump({"scan": {"max_threads": -1}}, f)
        cfg = Config(config_file=config_file)
        errors = cfg.validate()
        assert len(errors) == 1
        assert cfg.get("scan.max_threads") == 100

    def test_validate_fixes_bad_timeout(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        with open(config_file, "w") as f:
            json.dump({"scan": {"timeout": 0}}, f)
        cfg = Config(config_file=config_file)
        errors = cfg.validate()
        assert any("timeout" in e for e in errors)
        assert cfg.get("scan.timeout") == 2.0


class TestConfigApiKeyEncoding:
    def test_encode_decode_roundtrip(self):
        encoded = Config._encode_api_key("my-secret-key")
        assert encoded.startswith("enc:")
        decoded = Config._decode_api_key(encoded)
        assert decoded == "my-secret-key"

    def test_encode_empty_string(self):
        assert Config._encode_api_key("") == ""
        assert Config._encode_api_key(None) is None

    def test_decode_plain_text_passthrough(self):
        assert Config._decode_api_key("plain-key") == "plain-key"

    def test_decode_empty_string(self):
        assert Config._decode_api_key("") == ""
        assert Config._decode_api_key(None) is None

    def test_set_get_api_key(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        cfg = Config(config_file=config_file)
        cfg.set("intel.nvd_api_key", "my-api-key")

        # Read raw JSON to verify it's encoded
        with open(config_file, "r") as f:
            raw = json.load(f)
        assert raw["intel"]["nvd_api_key"].startswith("enc:")

        # get() should return decoded value
        assert cfg.get("intel.nvd_api_key") == "my-api-key"

    def test_double_encode_prevention(self):
        already_encoded = Config._encode_api_key("key")
        assert Config._encode_api_key(already_encoded) == already_encoded


class TestConfigSave:
    def test_save_creates_file(self, tmp_path):
        config_file = str(tmp_path / "new.json")
        cfg = Config(config_file=config_file)
        cfg.set("version", "3.0.0")
        assert os.path.exists(config_file)

    def test_save_preserves_structure(self, tmp_path):
        config_file = str(tmp_path / "test.json")
        cfg = Config(config_file=config_file)
        cfg.set("scan.max_threads", 999)

        with open(config_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["scan"]["max_threads"] == 999
        assert "proxy" in saved
