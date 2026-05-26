import socket
import concurrent.futures
import threading

COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
    1433: "MSSQL", 1521: "Oracle", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Proxy",
    8443: "HTTPS-Alt", 8888: "HTTP-Alt", 9090: "Web-Console",
    27017: "MongoDB",
}

MAX_PORTS = 5000


class PortScanner:
    def __init__(self, config, db, logger):
        self.config = config
        self.db = db
        self.logger = logger
        self._running = False
        self._results = []
        self._lock = threading.Lock()

    def scan(self, target, ports=None, callback=None):
        if ports is None:
            ports = self.config.get("scan.default_ports", list(COMMON_SERVICES.keys()))
        elif isinstance(ports, str):
            ports = self._parse_ports(ports)

        if len(ports) > MAX_PORTS:
            self.logger.warning(f"端口数量 {len(ports)} 超过上限 {MAX_PORTS}，已截断")
            ports = ports[:MAX_PORTS]

        timeout = self.config.get("scan.timeout", 2.0)
        max_threads = min(self.config.get("scan.max_threads", 100), 200)
        self._running = True
        self._results = []

        try:
            ip = socket.gethostbyname(target)
        except (socket.gaierror, OSError) as e:
            self.logger.error(f"无法解析主机: {target} ({e})")
            return []

        self.logger.info(f"开始端口扫描: {target} ({ip}) - {len(ports)} 个端口")

        total = len(ports)
        done = 0

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_port = {}
                for port in ports:
                    if not self._running:
                        break
                    future = executor.submit(self._scan_port, ip, port, timeout)
                    future_to_port[future] = port

                for future in concurrent.futures.as_completed(future_to_port):
                    if not self._running:
                        break
                    port = future_to_port[future]
                    try:
                        result = future.result(timeout=timeout + 3)
                        if result:
                            svc = COMMON_SERVICES.get(port, "unknown")
                            result["service"] = svc
                            with self._lock:
                                self._results.append(result)
                            self.logger.success(f"  {port}/tcp OPEN - {svc}")
                    except Exception:
                        pass
                    done += 1
                    if callback:
                        try:
                            callback(done, total, port)
                        except Exception:
                            pass
        except Exception as e:
            self.logger.error(f"扫描异常: {e}")

        with self._lock:
            self._results.sort(key=lambda x: x["port"])
            results_copy = list(self._results)

        self.logger.success(f"端口扫描完成: {len(results_copy)} 个开放端口")
        return results_copy

    def save_results(self, target, results):
        if not results:
            return
        try:
            target_id = self.db.get_or_create_target(target)
            if target_id is None:
                return
            for r in results:
                self.db.add_port(
                    target_id, r.get("port", 0), "open",
                    r.get("service", "unknown"), r.get("banner", ""),
                )
            self.db.log_scan("port_scan", target, "completed", results)
        except Exception as e:
            self.logger.error(f"保存扫描结果失败: {e}")

    def stop(self):
        self._running = False

    def _scan_port(self, ip, port, timeout):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                banner = ""
                try:
                    banner = self._grab_banner(sock, port)
                except Exception:
                    pass
                return {"port": port, "state": "open", "banner": banner}
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
        except Exception:
            pass
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
        return None

    def _grab_banner(self, sock, port):
        try:
            sock.settimeout(1.5)
            if port in (80, 8080, 8443, 8888, 443):
                sock.sendall(b"HEAD / HTTP/1.0\r\nHost: test\r\n\r\n")
            data = sock.recv(512)
            return data.decode("utf-8", errors="replace").strip()[:150]
        except Exception:
            return ""

    def _parse_ports(self, port_str):
        ports = []
        for part in port_str.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                try:
                    start, end = part.split("-", 1)
                    s, e = int(start), int(end)
                    if 1 <= s <= 65535 and 1 <= e <= 65535 and s <= e:
                        ports.extend(range(s, min(e, s + MAX_PORTS) + 1))
                except ValueError:
                    pass
            elif part.isdigit():
                p = int(part)
                if 1 <= p <= 65535:
                    ports.append(p)
        return ports[:MAX_PORTS]


def register(engine):
    scanner = PortScanner(engine.config, engine.db, engine.logger)
    engine.register_module("port_scanner", scanner)
