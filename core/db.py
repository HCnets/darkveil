import sqlite3
import json
import threading
from datetime import datetime


class Database:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self._lock = threading.Lock()
        db_path = config.get("db_path", "darkveil.db")
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._init_tables()
            logger.info(f"数据库已连接: {db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def _init_tables(self):
        with self._lock:
            cursor = self.conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host TEXT NOT NULL,
                    ip TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );
                CREATE TABLE IF NOT EXISTS ports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    port INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    service TEXT,
                    version TEXT,
                    banner TEXT,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (target_id) REFERENCES targets(id)
                );
                CREATE TABLE IF NOT EXISTS vulnerabilities (
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
                );
                CREATE TABLE IF NOT EXISTS exploits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vuln_id INTEGER,
                    module_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vuln_id) REFERENCES vulnerabilities(id)
                );
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    status TEXT NOT NULL,
                    results_json TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    finished_at TIMESTAMP
                );
            """)
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
                          description=None, evidence=None, recommendation=None, port_id=None):
        if target_id is None:
            return None
        try:
            with self._lock:
                cursor = self.conn.cursor()
                cursor.execute(
                    "INSERT INTO vulnerabilities (target_id, port_id, vuln_type, severity, "
                    "title, description, evidence, recommendation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (target_id, port_id, vuln_type, severity, title, description, evidence, recommendation),
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

    def close(self):
        try:
            with self._lock:
                if self.conn:
                    self.conn.commit()
                    self.conn.close()
                    self.conn = None
        except Exception as e:
            self.logger.error(f"关闭数据库失败: {e}")
