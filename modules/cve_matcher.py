import re
import json
import urllib.request
import urllib.error
import ssl


# Local CVE database: service -> [(version_pattern, cve_id, severity, description)]
LOCAL_CVE_DB = {
    "openssh": [
        (r"^[0-7]\.", "CVE-2018-15473", "MEDIUM", "OpenSSH 用户名枚举漏洞"),
        (r"^7\.[0-4]", "CVE-2016-10009", "HIGH", "OpenSSH ssh-agent 任意库加载"),
        (r"^7\.[0-5]", "CVE-2017-15906", "MEDIUM", "OpenSSH sftp 文件名信息泄露"),
        (r"^8\.[0-2]", "CVE-2019-6109", "MEDIUM", "OpenSSH SCP 命令注入"),
        (r"^8\.[0-5]", "CVE-2020-14145", "MEDIUM", "OpenSSH Observable Discrepancy"),
        (r"^8\.[0-9]", "CVE-2021-28041", "MEDIUM", "OpenSSH 双重释放漏洞"),
        (r"^9\.[0-5]", "CVE-2023-38408", "MEDIUM", "OpenSSH PKCS#11 远程代码执行"),
    ],
    "apache": [
        (r"2\.4\.[0-9]($|\D)", "CVE-2017-9798", "MEDIUM", "Apache HTTP Server Optionsbleed"),
        (r"2\.4\.([0-9]|[0-3]\d|4[0-6])($|\D)", "CVE-2021-44790", "CRITICAL", "Apache mod_lua 缓冲区溢出"),
        (r"2\.4\.([0-9]|[0-3]\d|4[0-8])($|\D)", "CVE-2021-41773", "CRITICAL", "Apache 路径遍历和 RCE"),
        (r"2\.4\.([0-9]|[0-3]\d|4[0-8])($|\D)", "CVE-2021-42013", "CRITICAL", "Apache 路径遍历绕过"),
        (r"2\.4\.([0-9]|[0-3]\d|5[0-1])($|\D)", "CVE-2022-22720", "CRITICAL", "Apache HTTP 请求走私"),
    ],
    "nginx": [
        (r"0\.", "CVE-2013-2028", "HIGH", "Nginx 栈缓冲区溢出"),
        (r"1\.([0-9]|1[0-9]|2[0-1])\.", "CVE-2021-23017", "HIGH", "Nginx DNS 解析器越界写入"),
        (r"1\.([0-9]|1[0-9]|2[0-4])\.", "CVE-2022-41741", "HIGH", "Nginx mp4 模块内存损坏"),
    ],
    "mysql": [
        (r"5\.[0-6]\.", "CVE-2012-5611", "HIGH", "MySQL 用户名枚举"),
        (r"5\.[0-7]\.", "CVE-2016-6662", "CRITICAL", "MySQL 远程代码执行"),
        (r"8\.0\.", "CVE-2020-2574", "HIGH", "MySQL 认证绕过"),
        (r"8\.0\.([0-9]|1[0-9]|2[0-8])($|\D)", "CVE-2021-2471", "HIGH", "MySQL 权限提升"),
    ],
    "microsoft iis": [
        (r"[7-9]\.", "CVE-2017-7269", "CRITICAL", "IIS WebDAV 缓冲区溢出"),
        (r"7\.5", "CVE-2010-2730", "HIGH", "IIS ASP.NET 源码泄露"),
    ],
    "proftpd": [
        (r"1\.[0-2]\.", "CVE-2010-4221", "HIGH", "ProFTPD telnet IAC 缓冲区溢出"),
        (r"1\.3\.[0-4]", "CVE-2015-3306", "HIGH", "ProFTPD mod_copy 任意文件复制"),
        (r"1\.3\.[0-5]", "CVE-2019-12815", "HIGH", "ProFTPD 任意文件复制"),
    ],
    "vsftpd": [
        (r"2\.3\.4", "CVE-2011-2523", "CRITICAL", "vsftpd 2.3.4 后门命令执行"),
    ],
    "postfix": [
        (r"[0-2]\.", "CVE-2014-0140", "MEDIUM", "Postfix SMTP 认证绕过"),
    ],
    "redis": [
        (r"[0-5]\.", "CVE-2015-8080", "CRITICAL", "Redis 未授权访问"),
        (r"[0-6]\.", "CVE-2022-0543", "CRITICAL", "Redis Lua 沙箱逃逸"),
    ],
    "tomcat": [
        (r"[6-9]\.", "CVE-2017-12617", "HIGH", "Apache Tomcat PUT 方法任意文件上传"),
        (r"8\.5\.([0-9]|[0-4]\d|5[0-6])($|\D)", "CVE-2020-1938", "CRITICAL", "Tomcat AJP 文件读取/包含 (Ghostcat)"),
        (r"9\.0\.([0-9]|[0-3]\d|4[0-5])($|\D)", "CVE-2020-1938", "CRITICAL", "Tomcat AJP 文件读取/包含 (Ghostcat)"),
        (r"10\.0\.", "CVE-2023-24998", "HIGH", "Tomcat DoS 攻击"),
    ],
    "samba": [
        (r"[0-3]\.", "CVE-2017-7494", "CRITICAL", "Samba 远程代码执行 (SambaCry)"),
        (r"3\.[0-6]\.", "CVE-2015-0240", "CRITICAL", "Samba 远程代码执行"),
        (r"4\.[0-9]\.", "CVE-2021-44142", "CRITICAL", "Samba out-of-bounds 读取"),
    ],
    "php": [
        (r"[0-6]\.", "CVE-2019-11043", "CRITICAL", "PHP-FPM 远程代码执行"),
        (r"7\.[0-3]\.", "CVE-2018-17082", "HIGH", "PHP XSS 漏洞"),
        (r"8\.0\.", "CVE-2021-21703", "HIGH", "PHP 本地权限提升"),
    ],
    "openssl": [
        (r"1\.0\.[0-1][a-z]?", "CVE-2014-0160", "CRITICAL", "OpenSSL Heartbleed 信息泄露"),
        (r"1\.0\.1[a-f]?", "CVE-2014-0160", "CRITICAL", "OpenSSL Heartbleed 信息泄露"),
        (r"1\.0\.[0-1]", "CVE-2014-0224", "HIGH", "OpenSSL CCS 注入"),
        (r"1\.0\.[0-2]", "CVE-2016-6304", "HIGH", "OpenSSL 内存耗尽 DoS"),
    ],
    "lighttpd": [
        (r"1\.4\.[0-9]($|\D)", "CVE-2014-2323", "HIGH", "Lighttpd 路径遍历"),
    ],
    "exim": [
        (r"[0-4]\.", "CVE-2019-10149", "CRITICAL", "Exim 远程命令执行 (Return of the Wizard)"),
        (r"4\.([0-8]\d|9[0-1])($|\D)", "CVE-2019-15846", "CRITICAL", "Exim 远程代码执行"),
    ],
    "bind": [
        (r"9\.([0-9]\.|1[0-1]\.)", "CVE-2015-5477", "HIGH", "BIND TKEY 查询 DoS"),
        (r"9\.1[0-7]\.", "CVE-2020-8617", "HIGH", "BIND 缓冲区溢出"),
    ],
    "dovecot": [
        (r"2\.[0-2]\.", "CVE-2019-10691", "HIGH", "Dovecot DoS"),
    ],
    "elasticsearch": [
        (r"[0-6]\.", "CVE-2015-1427", "CRITICAL", "Elasticsearch Groovy 沙箱绕过 RCE"),
        (r"[0-6]\.", "CVE-2014-3120", "CRITICAL", "Elasticsearch 动态脚本 RCE"),
    ],
    "mariadb": [
        (r"5\.5\.", "CVE-2012-5611", "HIGH", "MariaDB 用户名枚举"),
        (r"10\.[0-3]\.", "CVE-2016-6662", "CRITICAL", "MariaDB 远程代码执行"),
    ],
    "memcached": [
        (r"1\.[0-5]\.", "CVE-2016-8704", "CRITICAL", "Memcached 反射型 DDoS"),
    ],
}


class CVEMatcher:
    def __init__(self, db=None, logger=None):
        self.db = db
        self.logger = logger

    def match_local(self, service, version):
        """Match service+version against local CVE database."""
        if not service or not version:
            return []

        service_lower = service.lower().strip()
        results = []

        for svc_key, cve_list in LOCAL_CVE_DB.items():
            if svc_key in service_lower or service_lower in svc_key:
                for pattern, cve_id, severity, desc in cve_list:
                    try:
                        if re.search(pattern, version):
                            results.append({
                                "cve_id": cve_id,
                                "severity": severity,
                                "service": service,
                                "version": version,
                                "description": desc,
                                "source": "local",
                            })
                    except re.error:
                        continue

        return results

    def match_services(self, services):
        """Match a list of service dicts (from DB or scanner) against CVE database."""
        all_results = []
        for svc in services:
            service = svc.get("service", "")
            version = svc.get("version", "")
            port = svc.get("port", "")
            matches = self.match_local(service, version)
            for m in matches:
                m["port"] = port
            all_results.extend(matches)
        return all_results

    def query_nvd(self, keyword, max_results=10):
        """Query NIST NVD API for CVEs matching a keyword."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            url = (
                f"https://services.nvd.nist.gov/rest/json/cves/2.0"
                f"?keywordSearch={urllib.request.quote(keyword)}"
                f"&resultsPerPage={max_results}"
            )
            req = urllib.request.Request(url, headers={
                "User-Agent": "DarkVeil/1.0",
                "Accept": "application/json",
            })
            resp = urllib.request.urlopen(req, timeout=15, context=ctx)
            data = json.loads(resp.read().decode("utf-8"))

            results = []
            for vuln in data.get("vulnerabilities", []):
                cve = vuln.get("cve", {})
                cve_id = cve.get("id", "")
                desc_list = cve.get("descriptions", [])
                desc = ""
                for d in desc_list:
                    if d.get("lang") == "en":
                        desc = d.get("value", "")
                        break

                severity = "MEDIUM"
                metrics = cve.get("metrics", {})
                for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    if key in metrics and metrics[key]:
                        cvss = metrics[key][0].get("cvssData", {})
                        score = cvss.get("baseScore", 0)
                        if score >= 9.0:
                            severity = "CRITICAL"
                        elif score >= 7.0:
                            severity = "HIGH"
                        elif score >= 4.0:
                            severity = "MEDIUM"
                        else:
                            severity = "LOW"
                        break

                results.append({
                    "cve_id": cve_id,
                    "severity": severity,
                    "description": desc[:200],
                    "source": "nvd",
                })
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"NVD 查询失败: {e}")
            return []

    def scan_targets(self, targets):
        """Scan all targets' ports and match CVEs. Returns findings grouped by target."""
        if not self.db:
            return []

        from modules.report.compliance import get_owasp_category

        all_findings = []
        for target in targets:
            tid = target.get("id")
            host = target.get("host", "")
            ports = self.db.get_ports(tid)

            services_with_version = [
                p for p in ports
                if p.get("service") and p.get("version") and p.get("state") == "open"
            ]

            matches = self.match_services(services_with_version)
            for m in matches:
                m["target"] = host
                m["target_id"] = tid

            all_findings.extend(matches)

            # Save to DB as vulnerabilities with OWASP category
            for m in matches:
                owasp_code, _ = get_owasp_category("cve")
                self.db.add_vulnerability(
                    tid, "cve", m["severity"],
                    f"{m['cve_id']} ({m['service']} {m['version']})",
                    m["description"],
                    port_id=None,
                    owasp_category=owasp_code,
                )

        return all_findings
