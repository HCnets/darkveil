import socket
import re


FINGERPRINTS = {
    "SSH": {
        "pattern": r"SSH-\d+\.\d+",
        "versions": {
            "OpenSSH": r"OpenSSH[_ ](\S+)",
            "libssh": r"libssh[_ ](\S+)",
        },
    },
    "FTP": {
        "pattern": r"^220.*FTP",
        "versions": {
            "vsftpd": r"vsftpd (\S+)",
            "ProFTPD": r"ProFTPD (\S+)",
            "FileZilla": r"FileZilla Server (\S+)",
        },
    },
    "SMTP": {
        "pattern": r"^220.*SMTP",
        "versions": {
            "Postfix": r"Postfix",
            "Sendmail": r"Sendmail (\S+)",
        },
    },
    "HTTP": {
        "headers": {
            "Server": "server",
            "X-Powered-By": "powered_by",
        },
    },
    "MySQL": {
        "pattern": r"mysql|MariaDB",
    },
    "Redis": {
        "pattern": r"redis_version:",
    },
}


class ServiceDetector:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def detect(self, ip, port, banner=""):
        result = {
            "port": port,
            "service": "unknown",
            "version": "",
            "details": {},
        }

        if banner:
            result.update(self._analyze_banner(banner, port))

        if port in (80, 443, 8080, 8443, 8888):
            http_info = self._detect_http(ip, port)
            if http_info:
                result["service"] = "HTTP"
                result["details"].update(http_info)
                if http_info.get("server"):
                    result["version"] = http_info["server"]

        return result

    def detect_batch(self, ip, ports_with_banners):
        results = []
        for port_info in ports_with_banners:
            port = port_info["port"]
            banner = port_info.get("banner", "")
            result = self.detect(ip, port, banner)
            results.append(result)
        return results

    def _analyze_banner(self, banner, port):
        for svc_name, fp in FINGERPRINTS.items():
            if "pattern" in fp and re.search(fp["pattern"], banner, re.IGNORECASE):
                version = ""
                if "versions" in fp:
                    for vname, vpat in fp["versions"].items():
                        m = re.search(vpat, banner, re.IGNORECASE)
                        if m:
                            version = f"{vname} {m.group(1)}" if m.lastindex else vname
                            break
                return {"service": svc_name, "version": version}
        return {}

    def _detect_http(self, ip, port):
        try:
            import requests
            scheme = "https" if port in (443, 8443) else "http"
            url = f"{scheme}://{ip}:{port}/"
            resp = requests.get(url, timeout=5, verify=False, allow_redirects=False)
            info = {
                "status_code": resp.status_code,
                "server": resp.headers.get("Server", ""),
                "powered_by": resp.headers.get("X-Powered-By", ""),
                "content_type": resp.headers.get("Content-Type", ""),
            }
            title_match = re.search(r"<title>(.*?)</title>", resp.text[:5000], re.IGNORECASE)
            if title_match:
                info["title"] = title_match.group(1).strip()[:100]
            return info
        except Exception:
            return None


def register(engine):
    detector = ServiceDetector(engine.config, engine.logger)
    engine.register_module("service_detector", detector)
