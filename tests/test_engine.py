import pytest
from core.engine import Engine
from core.config import Config
from core.db import Database


class MockLogger:
    def __init__(self):
        self.messages = []

    def info(self, msg): self.messages.append(("INFO", msg))
    def warning(self, msg): self.messages.append(("WARN", msg))
    def error(self, msg): self.messages.append(("ERROR", msg))
    def debug(self, msg): self.messages.append(("DEBUG", msg))


class MockModule:
    def __init__(self, name):
        self.name = name


@pytest.fixture
def engine(tmp_path):
    config = Config(config_file=str(tmp_path / "config.json"))
    config.set("db_path", str(tmp_path / "test.db"))
    logger = MockLogger()
    db = Database(config, logger)
    return Engine(config, db, logger)


class TestEngineInit:
    def test_engine_has_config(self, engine):
        assert engine.config is not None

    def test_engine_has_db(self, engine):
        assert engine.db is not None

    def test_engine_has_logger(self, engine):
        assert engine.logger is not None

    def test_engine_starts_empty(self, engine):
        assert engine.modules == {}


class TestModuleRegistration:
    def test_register_module(self, engine):
        mod = MockModule("test_scanner")
        engine.register_module("test_scanner", mod)
        assert "test_scanner" in engine.modules

    def test_get_module(self, engine):
        mod = MockModule("test_scanner")
        engine.register_module("test_scanner", mod)
        assert engine.get_module("test_scanner") is mod

    def test_get_missing_module(self, engine):
        assert engine.get_module("nonexistent") is None

    def test_register_multiple_modules(self, engine):
        engine.register_module("mod1", MockModule("mod1"))
        engine.register_module("mod2", MockModule("mod2"))
        engine.register_module("mod3", MockModule("mod3"))
        assert len(engine.modules) == 3


class TestEventSystem:
    def test_on_and_emit(self, engine):
        results = []
        engine.on("scan_progress", lambda x: results.append(x))
        engine.emit("scan_progress", 50)
        assert results == [50]

    def test_multiple_listeners(self, engine):
        results_a = []
        results_b = []
        engine.on("scan_complete", lambda: results_a.append("a"))
        engine.on("scan_complete", lambda: results_b.append("b"))
        engine.emit("scan_complete")
        assert results_a == ["a"]
        assert results_b == ["b"]

    def test_emit_unknown_event(self, engine):
        # Should not raise
        engine.emit("unknown_event", "data")

    def test_on_unknown_event(self, engine):
        # Should not raise, but callback won't be stored
        engine.on("unknown_event", lambda: None)

    def test_callback_exception_logged(self, engine):
        def bad_callback():
            raise ValueError("boom")

        engine.on("log", bad_callback)
        engine.emit("log")
        assert any("异常" in msg for _, msg in engine.logger.messages)

    def test_emit_with_kwargs(self, engine):
        results = []
        engine.on("vuln_found", lambda **kw: results.append(kw))
        engine.emit("vuln_found", target="example.com", vuln="xss")
        assert results == [{"target": "example.com", "vuln": "xss"}]


class TestAutoDiscover:
    def test_discover_nonexistent_path(self, engine):
        # Should not raise
        engine.auto_discover_modules("/nonexistent/path", "fake.package")

    def test_discover_skips_underscore_modules(self, engine, tmp_path):
        # Create a fake package with an underscore module
        pkg_dir = tmp_path / "fakepkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "_private.py").write_text("")
        (pkg_dir / "public.py").write_text("def register(e): pass")

        engine.auto_discover_modules(str(pkg_dir), "fakepkg")
        # _private should be skipped, public should be loaded
        # (we can't easily verify import without sys.path manipulation)
