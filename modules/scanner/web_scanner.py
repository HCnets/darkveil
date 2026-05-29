import re
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from requests import RequestException
from modules.http_utils import get_session


SQLI_PAYLOADS = [
    {"payload": "'", "type": "error", "desc": "单引号注入"},
    {"payload": "' OR '1'='1", "type": "boolean", "desc": "布尔注入"},
    {"payload": "1' AND '1'='1", "type": "boolean", "desc": "布尔 AND 注入"},
    {"payload": "' OR 1=1--", "type": "error", "desc": "UNION 注入"},
    {"payload": "1; WAITFOR DELAY '0:0:5'--", "type": "time", "desc": "时间盲注 (MSSQL)"},
    {"payload": "' OR SLEEP(5)--", "type": "time", "desc": "时间盲注 (MySQL)"},
]

SQLI_ERROR_PATTERNS = [
    r"sql syntax.*?near",
    r"mysql_fetch",
    r"ORA-\d{5}",
    r"PostgreSQL.*?ERROR",
    r"SQLite.*?error",
    r"Unclosed quotation mark",
    r"Microsoft OLE DB Provider",
    r"Syntax error.*?in query expression",
    r"Warning.*?mysql_",
    r"valid MySQL result",
    r"MySqlClient\.",
    r"com\.mysql\.jdbc",
    r"org\.postgresql\.util\.PSQLException",
]

XSS_PAYLOADS = [
    {"payload": '<script>alert("DV-XSS")</script>', "type": "reflected"},
    {"payload": '"><img src=x onerror=alert("DV-XSS")>', "type": "reflected"},
    {"payload": "javascript:alert('DV-XSS')", "type": "reflected"},
    {"payload": "'-alert('DV-XSS')-'", "type": "reflected"},
]

SENSITIVE_PATHS = [
    ".git/config", ".git/HEAD", ".env", ".env.bak", ".env.local",
    "robots.txt", "sitemap.xml", "crossdomain.xml", "clientaccesspolicy.xml",
    "wp-config.php.bak", "config.php.bak", "web.config",
    ".htaccess", ".htpasswd", "server-status", "server-info",
    "phpinfo.php", "info.php", "test.php", "debug.php",
    "admin/", "administrator/", "wp-admin/", "phpmyadmin/",
    ".DS_Store", "Thumbs.db", "backup.zip", "backup.sql",
    "db.sql", "dump.sql", "database.sql",
]


class WebScanner:
    def __init__(self, config, db, logger):
        self.config = config
        self.db = db
        self.logger = logger
        self.timeout = config.get("scan.web_timeout", 10)
        self._running = False
        self._session = get_session(config)

    def scan(self, target_url, callback=None):
        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url

        self._running = True
        findings = []

        self.logger.info(f"开始 Web 扫描: {target_url}")

        steps = [
            ("敏感文件探测", lambda: self._scan_sensitive(target_url)),
            ("SQL 注入检测", lambda: self._scan_sqli(target_url)),
            ("XSS 检测", lambda: self._scan_xss(target_url)),
            ("HTTP 头安全检查", lambda: self._scan_headers(target_url)),
        ]

        total_steps = len(steps)
        for i, (step_name, step_fn) in enumerate(steps):
            if not self._running:
                break
            self.logger.info(f"  [{i+1}/{total_steps}] {step_name}")
            try:
                results = step_fn()
                for finding in results:
                    findings.append(finding)
                    self.logger.warning(f"    发现: {finding['title']} [{finding['severity']}]")
            except Exception as e:
                self.logger.error(f"    {step_name} 异常: {e}")
            if callback:
                callback(i + 1, total_steps, step_name)

        self.logger.success(f"Web 扫描完成: {len(findings)} 个发现")
        return findings

    def save_findings(self, target_url, findings):
        target_id = self.db.get_or_create_target(target_url)
        for finding in findings:
            self.db.add_vulnerability(
                target_id=target_id,
                vuln_type=finding["type"],
                severity=finding["severity"],
                title=finding["title"],
                description=finding.get("description", ""),
                evidence=finding.get("evidence", ""),
                recommendation=finding.get("recommendation", ""),
            )
        self.db.log_scan("web_scan", target_url, "completed", findings)

    def stop(self):
        self._running = False

    def _scan_sensitive(self, base_url):
        findings = []
        for path in SENSITIVE_PATHS:
            if not self._running:
                break
            url = urljoin(base_url, path)
            try:
                resp = self._session.get(url, timeout=self.timeout, allow_redirects=False)
                if resp.status_code == 200 and len(resp.text) > 10:
                    severity = "HIGH" if path in (".env", ".git/config", "wp-config.php.bak", ".htpasswd") else "MEDIUM"
                    findings.append({
                        "type": "sensitive_file",
                        "severity": severity,
                        "title": f"敏感文件暴露: {path}",
                        "description": f"发现可公开访问的敏感文件 {url}",
                        "evidence": f"HTTP {resp.status_code}, 大小 {len(resp.text)} bytes",
                        "recommendation": f"通过 Web 服务器配置禁止访问 {path}",
                    })
            except RequestException:
                pass
        return findings

    def _scan_sqli(self, base_url):
        findings = []
        try:
            resp = self._session.get(base_url, timeout=self.timeout)
        except RequestException:
            return findings

        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)

        if not params:
            links = re.findall(r'href=["\']([^"\']*\?[^"\']*)["\']', resp.text[:20000])
            for link in links[:5]:
                full_url = urljoin(base_url, link)
                findings.extend(self._test_sqli_url(full_url))
        else:
            findings.extend(self._test_sqli_url(base_url))

        return findings

    def _test_sqli_url(self, url):
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if not params:
            return findings

        for param_name in params:
            for sqli in SQLI_PAYLOADS:
                if not self._running:
                    break
                test_params = dict(params)
                test_params[param_name] = sqli["payload"]
                test_url = urlunparse(parsed._replace(query=urlencode(test_params, doseq=True)))

                try:
                    if sqli["type"] == "time":
                        start = time.time()
                        self._session.get(test_url, timeout=self.timeout + 5)
                        elapsed = time.time() - start
                        if elapsed >= 4.5:
                            findings.append({
                                "type": "sqli",
                                "severity": "CRITICAL",
                                "title": f"SQL 注入 (时间盲注): 参数 {param_name}",
                                "description": f"参数 {param_name} 存在时间盲注漏洞",
                                "evidence": f"Payload: {sqli['payload']}, 响应时间: {elapsed:.1f}s",
                                "recommendation": "使用参数化查询，禁止拼接 SQL",
                            })
                    else:
                        resp = self._session.get(test_url, timeout=self.timeout)
                        for pattern in SQLI_ERROR_PATTERNS:
                            if re.search(pattern, resp.text, re.IGNORECASE):
                                findings.append({
                                    "type": "sqli",
                                    "severity": "CRITICAL",
                                    "title": f"SQL 注入 (报错型): 参数 {param_name}",
                                    "description": f"参数 {param_name} 触发数据库错误信息",
                                    "evidence": f"Payload: {sqli['payload']}, 匹配: {pattern}",
                                    "recommendation": "使用参数化查询，禁止拼接 SQL",
                                })
                                break
                except RequestException:
                    pass
        return findings

    def _scan_xss(self, base_url):
        findings = []
        try:
            resp = self._session.get(base_url, timeout=self.timeout)
        except RequestException:
            return findings

        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)

        if not params:
            links = re.findall(r'href=["\']([^"\']*\?[^"\']*)["\']', resp.text[:20000])
            for link in links[:3]:
                full_url = urljoin(base_url, link)
                findings.extend(self._test_xss_url(full_url))
        else:
            findings.extend(self._test_xss_url(base_url))

        return findings

    def _test_xss_url(self, url):
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if not params:
            return findings

        for param_name in params:
            for xss in XSS_PAYLOADS:
                if not self._running:
                    break
                test_params = dict(params)
                test_params[param_name] = xss["payload"]
                test_url = urlunparse(parsed._replace(query=urlencode(test_params, doseq=True)))

                try:
                    resp = self._session.get(test_url, timeout=self.timeout)
                    if xss["payload"] in resp.text:
                        findings.append({
                            "type": "xss",
                            "severity": "HIGH",
                            "title": f"反射型 XSS: 参数 {param_name}",
                            "description": f"参数 {param_name} 存在反射型 XSS 漏洞",
                            "evidence": f"Payload: {xss['payload']}",
                            "recommendation": "对输出进行 HTML 编码，设置 CSP 头",
                        })
                except RequestException:
                    pass
        return findings

    def _scan_headers(self, base_url):
        findings = []
        try:
            resp = self._session.get(base_url, timeout=self.timeout)
        except RequestException:
            return findings

        headers = resp.headers

        security_headers = {
            "X-Frame-Options": ("MEDIUM", "缺少 X-Frame-Options 头，存在点击劫持风险"),
            "X-Content-Type-Options": ("LOW", "缺少 X-Content-Type-Options 头"),
            "X-XSS-Protection": ("LOW", "缺少 X-XSS-Protection 头"),
            "Strict-Transport-Security": ("MEDIUM", "缺少 HSTS 头"),
            "Content-Security-Policy": ("MEDIUM", "缺少 CSP 头"),
        }

        for header, (severity, desc) in security_headers.items():
            if header.lower() not in {k.lower() for k in headers}:
                findings.append({
                    "type": "header_missing",
                    "severity": severity,
                    "title": f"缺少安全头: {header}",
                    "description": desc,
                    "recommendation": f"在 Web 服务器配置中添加 {header} 响应头",
                })

        server = headers.get("Server", "")
        if server:
            findings.append({
                "type": "info_disclosure",
                "severity": "LOW",
                "title": f"服务器信息泄露: {server}",
                "description": "Server 头暴露了服务器软件版本",
                "evidence": f"Server: {server}",
                "recommendation": "移除或伪装 Server 响应头",
            })

        powered = headers.get("X-Powered-By", "")
        if powered:
            findings.append({
                "type": "info_disclosure",
                "severity": "LOW",
                "title": f"技术栈信息泄露: {powered}",
                "description": "X-Powered-By 头暴露了后端技术栈",
                "evidence": f"X-Powered-By: {powered}",
                "recommendation": "移除 X-Powered-By 响应头",
            })

        return findings


def register(engine):
    scanner = WebScanner(engine.config, engine.db, engine.logger)
    engine.register_module("web_scanner", scanner)
