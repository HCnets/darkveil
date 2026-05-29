import sqlite3
import json
import threading
from datetime import datetime

# Schema version tracking
SCHEMA_VERSION = 2

MIGRATIONS = {
    1: [
        # Initial schema (version 1)
        """CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );""",
        """CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT NOT NULL,
            ip TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS ports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            port INTEGER NOT NULL,
            state TEXT NOT NULL,
            service TEXT,
            version TEXT,
            banner TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES targets(id)
        );""",
        """CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            port_id INTEGER,
            vuln_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            evidence TEXT,
            recommendation TEXT,
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES targets(id),
            FOREIGN KEY (port_id) REFERENCES ports(id)
        );""",
        """CREATE TABLE IF NOT EXISTS exploits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vuln_id INTEGER,
            module_name TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(id)
        );""",
        """CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT NOT NULL,
            target TEXT NOT NULL,
            status TEXT NOT NULL,
            results_json TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS honeypot_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            source_port INTEGER,
            data TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS intel_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            query TEXT NOT NULL,
            results_json TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
    ],
    2: [
        # Version 2: add OWASP/CWE columns
        "ALTER TABLE vulnerabilities ADD COLUMN owasp_category TEXT;",
        "ALTER TABLE vulnerabilities ADD COLUMN cwe_id TEXT;",
    ],
}


class Database:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self._lock = threading.Lock()
        db_path = config.get("db_path", "darkveil.db")
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._run_migrations()
            logger.info(f"数据库已连接: {db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def _get_schema_version(self):
        """Get current schema version from the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            )
            if not cursor.fetchone():
                return 0
            cursor.execute("SELECT MAX(version) FROM schema_version")
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0
        except sqlite3.OperationalError:
            return 0

    def _set_schema_version(self, version):
        """Record the current schema version."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (version,))
        self.conn.commit()

    def _run_migrations(self):
        """Apply pending schema migrations in order."""
        current = self._get_schema_version()
        target = SCHEMA_VERSION

        if current >= target:
            return

        with self._lock:
            for version in range(current + 1, target + 1):
                if version not in MIGRATIONS:
                    continue
                for sql in MIGRATIONS[version]:
                    try:
                        self.conn.execute(sql)
                    except sqlite3.OperationalError:
                        # Column/table already exists, skip
                        pass
                self._set_schema_version(version)
                self.logger.info(f"数据库迁移完成: v{version}")
            self.conn.commit()

    def add_target(self, host, ip=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO targets (host, ip) VALUES (?, ?)", (host, ip))
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_target 失败: {e}")
            return None

    def get_or_create_target(self, host, ip=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT id FROM targets WHERE host = ?", (host,))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE targets SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
                        (row["id"],),
                    )
                    self.conn.commit()
                    return row["id"]
                cursor.execute("INSERT INTO targets (host, ip) VALUES (?, ?)", (host, ip))
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"get_or_create_target 失败: {e}")
            return None

    def update_notes(self, target_id, notes):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("UPDATE targets SET notes = ? WHERE id = ?", (notes, target_id))
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"update_notes 失败: {e}")

    def add_port(self, target_id, port, state, service=None, version=None, banner=None):
        if target_id is None:
            return None
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO ports (target_id, port, state, service, version, banner) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (target_id, port, state, service, version, banner),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_port 失败: {e}")
            return None

    def add_vulnerability(self, target_id, vuln_type, severity, title,
                          description=None, evidence=None, recommendation=None, port_id=None,
                          owasp_category=None, cwe_id=None):
        if target_id is None:
            return None
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO vulnerabilities (target_id, port_id, vuln_type, severity, "
                    "title, description, evidence, recommendation, owasp_category, cwe_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (target_id, port_id, vuln_type, severity, title, description,
                     evidence, recommendation, owasp_category, cwe_id),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_vulnerability 失败: {e}")
            return None

    def add_exploit(self, module_name, status, result=None, vuln_id=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO exploits (vuln_id, module_name, status, result) VALUES (?, ?, ?, ?)",
                    (vuln_id, module_name, status, result),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_exploit 失败: {e}")
            return None

    def log_scan(self, scan_type, target, status, results=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                results_json = json.dumps(results, ensure_ascii=False, default=str) if results else None
                cursor.execute(
                    "INSERT INTO scan_history (scan_type, target, status, results_json, finished_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (scan_type, target, status, results_json, datetime.now().isoformat()),
                )
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"log_scan 失败: {e}")

    def get_targets(self):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM targets ORDER BY last_seen DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_targets 失败: {e}")
            return []

    def get_ports(self, target_id):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM ports WHERE target_id = ? ORDER BY port", (target_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_ports 失败: {e}")
            return []

    def get_vulnerabilities(self, target_id=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                if target_id:
                    cursor.execute(
                        "SELECT * FROM vulnerabilities WHERE target_id = ? ORDER BY found_at DESC",
                        (target_id,),
                    )
                else:
                    cursor.execute("SELECT * FROM vulnerabilities ORDER BY found_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_vulnerabilities 失败: {e}")
            return []

    def get_scan_history(self, limit=50):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM scan_history ORDER BY started_at DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_scan_history 失败: {e}")
            return []

    def save_snapshot(self, target_id, label=None):
        """Save a point-in-time snapshot of a target's ports and vulns."""
        try:
            import json
            ports = self.get_ports(target_id)
            vulns = self.get_vulnerabilities(target_id)
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO scan_history (scan_type, target, status, results_json) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        "snapshot",
                        f"target:{target_id}",
                        "done",
                        json.dumps({
                            "target_id": target_id,
                            "label": label or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "ports": ports,
                            "vulns": vulns,
                        }, ensure_ascii=False, default=str),
                    ),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"save_snapshot 失败: {e}")
            return None

    def get_snapshots(self, target_id):
        """Get all snapshots for a target."""
        try:
            import json
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT id, results_json, started_at FROM scan_history "
                    "WHERE scan_type = 'snapshot' AND target = ? ORDER BY started_at DESC",
                    (f"target:{target_id}",),
                )
                results = []
                for row in cursor.fetchall():
                    data = json.loads(row["results_json"]) if row["results_json"] else {}
                    data["snapshot_id"] = row["id"]
                    data["snapshot_time"] = row["started_at"]
                    results.append(data)
                return results
        except Exception as e:
            self.logger.error(f"get_snapshots 失败: {e}")
            return []

    def get_port_service_stats(self):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT COALESCE(service, 'unknown') as service, COUNT(*) as cnt "
                    "FROM ports WHERE state = 'open' GROUP BY service ORDER BY cnt DESC LIMIT 10"
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_port_service_stats 失败: {e}")
            return []

    def get_vuln_timeline(self, limit=30):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT DATE(found_at) as day, COUNT(*) as cnt "
                    "FROM vulnerabilities GROUP BY DATE(found_at) ORDER BY day DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_vuln_timeline 失败: {e}")
            return []

    def get_stats(self):
        stats = {"targets": 0, "open_ports": 0, "vulnerabilities": 0,
                 "exploits": 0, "scans": 0, "vuln_by_severity": {}}
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) as cnt FROM targets")
                row = cursor.fetchone()
                stats["targets"] = row["cnt"] if row else 0

                cursor.execute("SELECT COUNT(*) as cnt FROM ports WHERE state = 'open'")
                row = cursor.fetchone()
                stats["open_ports"] = row["cnt"] if row else 0

                cursor.execute("SELECT COUNT(*) as cnt FROM vulnerabilities")
                row = cursor.fetchone()
                stats["vulnerabilities"] = row["cnt"] if row else 0

                cursor.execute("SELECT COUNT(*) as cnt FROM exploits")
                row = cursor.fetchone()
                stats["exploits"] = row["cnt"] if row else 0

                cursor.execute("SELECT COUNT(*) as cnt FROM scan_history")
                row = cursor.fetchone()
                stats["scans"] = row["cnt"] if row else 0

                cursor.execute(
                    "SELECT severity, COUNT(*) as cnt FROM vulnerabilities GROUP BY severity"
                )
                stats["vuln_by_severity"] = {row["severity"]: row["cnt"] for row in cursor.fetchall()}
        except Exception as e:
            self.logger.error(f"get_stats 失败: {e}")
        return stats

    def add_honeypot_capture(self, service, source_ip, source_port=None, data=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO honeypot_captures (service, source_ip, source_port, data) "
                    "VALUES (?, ?, ?, ?)",
                    (service, source_ip, source_port, data),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_honeypot_capture 失败: {e}")
            return None

    def get_honeypot_captures(self, limit=100):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT * FROM honeypot_captures ORDER BY captured_at DESC LIMIT ?",
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"get_honeypot_captures 失败: {e}")
            return []

    def delete_target(self, target_id):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM vulnerabilities WHERE target_id = ?", (target_id,))
                cursor.execute("DELETE FROM ports WHERE target_id = ?", (target_id,))
                cursor.execute("DELETE FROM targets WHERE id = ?", (target_id,))
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"delete_target 失败: {e}")

    def clear_honeypot_captures(self):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM honeypot_captures")
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"clear_honeypot_captures 失败: {e}")

    def add_intel_query(self, source, query, results_json):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO intel_queries (source, query, results_json) VALUES (?, ?, ?)",
                    (source, query, results_json),
                )
                self.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"add_intel_query 失败: {e}")
            return None

    def get_intel_cache(self, source, query, max_age_hours=24):
        try:
            import json
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT results_json FROM intel_queries "
                    "WHERE source = ? AND query = ? "
                    "AND datetime(cached_at, '+' || ? || ' hours') > datetime('now') "
                    "ORDER BY cached_at DESC LIMIT 1",
                    (source, query, max_age_hours),
                )
                row = cursor.fetchone()
                if row and row["results_json"]:
                    return json.loads(row["results_json"])
                return None
        except Exception as e:
            self.logger.error(f"get_intel_cache 失败: {e}")
            return None

    def clear_intel_cache(self, source=None):
        try:
            with self._lock:
                cursor = self.conn.cursor()
                if source:
                    cursor.execute("DELETE FROM intel_queries WHERE source = ?", (source,))
                else:
                    cursor.execute("DELETE FROM intel_queries")
                self.conn.commit()
        except Exception as e:
            self.logger.error(f"clear_intel_cache 失败: {e}")

    def close(self):
        try:
            with self._lock:
                if self.conn:
                    self.conn.commit()
                    self.conn.close()
                    self.conn = None
        except Exception as e:
            self.logger.error(f"关闭数据库失败: {e}")
