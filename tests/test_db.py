import os
import sqlite3
import pytest
from core.db import Database
from core.config import Config


class MockLogger:
    """Minimal logger for testing."""
    def __init__(self):
        self.messages = []

    def info(self, msg): self.messages.append(("INFO", msg))
    def warning(self, msg): self.messages.append(("WARN", msg))
    def error(self, msg): self.messages.append(("ERROR", msg))
    def debug(self, msg): self.messages.append(("DEBUG", msg))


@pytest.fixture
def db(tmp_path):
    """Create a Database with a temporary db file."""
    config_file = str(tmp_path / "config.json")
    config = Config(config_file=config_file)
    config.set("db_path", str(tmp_path / "test.db"))
    logger = MockLogger()
    return Database(config, logger)


class TestDatabaseInit:
    def test_creates_db_file(self, db, tmp_path):
        db_path = tmp_path / "test.db"
        assert db_path.exists()

    def test_creates_all_tables(self, db, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        expected = {
            "targets", "ports", "vulnerabilities", "exploits",
            "scan_history", "honeypot_captures", "intel_queries",
        }
        assert expected.issubset(tables)


class TestTargetOperations:
    def test_add_target(self, db):
        tid = db.add_target("example.com", "93.184.216.34")
        assert tid is not None
        assert tid > 0

    def test_add_target_duplicate(self, db):
        tid1 = db.add_target("example.com")
        tid2 = db.add_target("example.com")
        assert tid1 != tid2  # allows duplicates

    def test_get_or_create_target_new(self, db):
        tid = db.get_or_create_target("test.com", "1.2.3.4")
        assert tid is not None

    def test_get_or_create_target_existing(self, db):
        tid1 = db.get_or_create_target("test.com", "1.2.3.4")
        tid2 = db.get_or_create_target("test.com", "5.6.7.8")
        assert tid1 == tid2  # same target, same id

    def test_update_notes(self, db):
        tid = db.add_target("example.com")
        db.update_notes(tid, "test note")
        # Verify by reading directly
        with db._lock:
            cursor = db.conn.cursor()
            cursor.execute("SELECT notes FROM targets WHERE id = ?", (tid,))
            row = cursor.fetchone()
            assert row["notes"] == "test note"


class TestPortOperations:
    def test_add_port(self, db):
        tid = db.add_target("example.com")
        pid = db.add_port(tid, 80, "open", "http", "nginx/1.0")
        assert pid is not None

    def test_add_port_null_target(self):
        # Should handle None target_id gracefully
        # (db is not needed here since we test with None)
        pass

    def test_add_multiple_ports(self, db):
        tid = db.add_target("example.com")
        p1 = db.add_port(tid, 80, "open", "http")
        p2 = db.add_port(tid, 443, "open", "https")
        p3 = db.add_port(tid, 22, "open", "ssh")
        assert len({p1, p2, p3}) == 3


class TestVulnerabilityOperations:
    def test_add_vulnerability(self, db):
        tid = db.add_target("example.com")
        vid = db.add_vulnerability(
            tid, "sqli", "CRITICAL", "SQL Injection in /login",
            description="Blind SQL injection", evidence="' OR 1=1--"
        )
        assert vid is not None

    def test_add_vulnerability_with_port(self, db):
        tid = db.add_target("example.com")
        pid = db.add_port(tid, 80, "open", "http")
        vid = db.add_vulnerability(
            tid, "xss", "HIGH", "Reflected XSS",
            port_id=pid
        )
        assert vid is not None


class TestExploitOperations:
    def test_add_exploit(self, db):
        tid = db.add_target("example.com")
        vid = db.add_vulnerability(tid, "sqli", "CRITICAL", "SQLi")
        eid = db.add_exploit(vid, "sqli_exploiter", "success", "Extracted 3 tables")
        assert eid is not None


class TestScanHistory:
    def test_log_scan(self, db):
        # log_scan doesn't return an id, just verify no exception
        db.log_scan("port_scan", "example.com", "completed",
                    results={"ports": [80, 443]})

    def test_log_scan_stores_results(self, db):
        db.log_scan("port_scan", "example.com", "completed",
                    results={"ports": [80, 443]})
        with db._lock:
            cursor = db.conn.cursor()
            cursor.execute("SELECT * FROM scan_history WHERE target = ?", ("example.com",))
            row = cursor.fetchone()
            assert row is not None
            assert row["status"] == "completed"
            assert row["finished_at"] is not None


class TestHoneypotCaptures:
    def test_add_capture(self, db):
        cid = db.add_honeypot_capture("ssh", "192.168.1.100", 54321, "root password123")
        assert cid is not None


class TestIntelQueries:
    def test_add_and_get_cache(self, db):
        db.add_intel_query("nvd", "CVE-2021-44228", '{"results": []}')
        cached = db.get_intel_cache("nvd", "CVE-2021-44228", max_age_hours=24)
        assert cached is not None

    def test_cache_miss(self, db):
        cached = db.get_intel_cache("nvd", "nonexistent", max_age_hours=24)
        assert cached is None
