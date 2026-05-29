import pytest
from core.config import Config
from modules.http_utils import get_session, get_verify_setting


@pytest.fixture
def config_ssl_off(tmp_path):
    config = Config(config_file=str(tmp_path / "config.json"))
    config.set("verify_ssl", False)
    return config


@pytest.fixture
def config_ssl_on(tmp_path):
    config = Config(config_file=str(tmp_path / "config.json"))
    config.set("verify_ssl", True)
    return config


class TestGetSession:
    def test_session_default_verify_false(self):
        session = get_session(None)
        assert session.verify is False

    def test_session_verify_from_config_off(self, config_ssl_off):
        session = get_session(config_ssl_off)
        assert session.verify is False

    def test_session_verify_from_config_on(self, config_ssl_on):
        session = get_session(config_ssl_on)
        assert session.verify is True

    def test_session_has_user_agent(self):
        session = get_session(None)
        assert "Chrome" in session.headers.get("User-Agent", "")

    def test_session_proxy_config(self, tmp_path):
        config = Config(config_file=str(tmp_path / "config.json"))
        config.set("proxy.enabled", True)
        config.set("proxy.http", "http://proxy:8080")
        session = get_session(config)
        assert session.proxies.get("http") == "http://proxy:8080"

    def test_session_socks5_proxy(self, tmp_path):
        config = Config(config_file=str(tmp_path / "config.json"))
        config.set("proxy.enabled", True)
        config.set("proxy.socks5", "127.0.0.1:1080")
        session = get_session(config)
        assert "socks5h://" in session.proxies.get("http", "")

    def test_session_no_proxy_when_disabled(self, tmp_path):
        config = Config(config_file=str(tmp_path / "config.json"))
        config.set("proxy.enabled", False)
        session = get_session(config)
        assert session.proxies == {}


class TestGetVerifySetting:
    def test_default_false(self):
        assert get_verify_setting(None) is False

    def test_config_false(self, config_ssl_off):
        assert get_verify_setting(config_ssl_off) is False

    def test_config_true(self, config_ssl_on):
        assert get_verify_setting(config_ssl_on) is True
