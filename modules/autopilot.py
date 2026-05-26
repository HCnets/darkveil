import time


SERVICE_EXPLOIT_MAP = {
    "ssh": ["ssh_brute", "ssh_version_enum"],
    "ftp": ["ftp_brute"],
    "mysql": ["mysql_brute"],
    "http": ["sqli_exploiter", "ssrf_detector", "cmdi_detector", "file_upload",
             "cors_checker", "unauth_scanner", "dir_scanner", "api_fuzzer", "cve_checker"],
    "https": ["sqli_exploiter", "ssrf_detector", "cmdi_detector", "cors_checker",
              "unauth_scanner", "dir_scanner", "api_fuzzer", "cve_checker"],
    "rdp": ["rdp_brute"],
    "smb": ["smb_brute"],
    "snmp": ["snmp_brute"],
    "dns": ["dns_zone_transfer"],
}

STAGE_NAMES = [
    "端口扫描",
    "服务识别",
    "Web 漏洞扫描",
    "利用模块匹配",
    "漏洞检测",
    "自动利用",
    "报告生成",
]


class AutoPilot:
    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger
        self._running = False
        self._results = {
            "open_ports": [],
            "services": [],
            "web_vulns": [],
            "matched_modules": [],
            "check_results": [],
            "exploit_results": [],
            "report_path": None,
        }

    def stop(self):
        self._running = False

    def run(self, target, options, callback):
        """Run the full attack chain. callback(stage_idx, message, progress_pct)"""
        self._running = True
        self._results = {k: [] if isinstance(v, list) else None for k, v in self._results.items()}

        port_scanner = self.engine.get_module("port_scanner")
        service_detector = self.engine.get_module("service_detector")
        web_scanner = self.engine.get_module("web_scanner")
        exploit_mgr = self.engine.get_module("exploit_manager")
        db = self.engine.db

        target_ip = target
        total_stages = 7

        # === Stage 1: Port Scan ===
        callback(0, f"[1/{total_stages}] 端口扫描: {target}", 0)
        if not self._running:
            return self._results

        try:
            scan_mode = options.get("scan_mode", "fast")
            if scan_mode == "fast":
                ports = None  # default top ports
            elif scan_mode == "full":
                ports = list(range(1, 65536))
            else:
                port_str = options.get("custom_ports", "80,443,22,21,3306,3389,8080")
                ports = [int(p.strip()) for p in port_str.split(",") if p.strip().isdigit()]

            open_ports = port_scanner.scan(target, ports=ports)
            self._results["open_ports"] = open_ports or []

            if not open_ports:
                callback(0, "未发现开放端口，扫描终止", 100)
                return self._results

            callback(0, f"发现 {len(open_ports)} 个开放端口", 15)
            for p in open_ports:
                callback(0, f"  端口 {p['port']}: {p.get('service', 'unknown')}", -1)

            if db:
                tid = db.get_or_create_target(target)
                for p in open_ports:
                    db.add_port(tid, p["port"], "open", p.get("service"), p.get("version"), p.get("banner"))
        except Exception as e:
            callback(0, f"端口扫描失败: {e}", -1)
            return self._results

        if not self._running:
            return self._results

        # === Stage 2: Service Detection ===
        callback(1, f"[2/{total_stages}] 服务识别", 20)
        try:
            ip = open_ports[0].get("ip", target) if open_ports else target
            services = service_detector.detect_batch(ip, open_ports)
            self._results["services"] = services or []

            for svc in (services or []):
                port = svc.get("port")
                name = svc.get("service", "unknown")
                ver = svc.get("version", "")
                callback(1, f"  {port}: {name} {ver}".strip(), -1)

                # Update DB with enriched service info
                if db and tid:
                    for p in open_ports:
                        if p["port"] == port:
                            db.add_port(tid, port, "open", name, ver, p.get("banner"))
                            break

            callback(1, f"服务识别完成: {len(services or [])} 个服务", 30)
        except Exception as e:
            callback(1, f"服务识别异常: {e}", -1)

        if not self._running:
            return self._results

        # === Stage 3: Web Vulnerability Scan ===
        callback(2, f"[3/{total_stages}] Web 漏洞扫描", 35)
        web_ports = [p for p in (open_ports or []) if p.get("service") in ("http", "https", "http-proxy")]
        # Also check common HTTP ports
        for p in (open_ports or []):
            if p["port"] in (80, 443, 8080, 8443, 8888) and p not in web_ports:
                web_ports.append(p)

        all_web_vulns = []
        for p in web_ports:
            if not self._running:
                break
            port = p["port"]
            scheme = "https" if port == 443 or p.get("service") == "https" else "http"
            url = f"{scheme}://{target}:{port}" if port not in (80, 443) else f"{scheme}://{target}"
            try:
                callback(2, f"  扫描: {url}", -1)
                vulns = web_scanner.scan(url)
                if vulns:
                    all_web_vulns.extend(vulns)
                    for v in vulns:
                        callback(2, f"    [{v.get('severity')}] {v.get('title')}", -1)
            except Exception as e:
                callback(2, f"  Web 扫描失败 {url}: {e}", -1)

        self._results["web_vulns"] = all_web_vulns
        if all_web_vulns and db and tid:
            for v in all_web_vulns:
                db.add_vulnerability(
                    tid, v.get("type", "web"), v.get("severity", "MEDIUM"),
                    v.get("title", ""), v.get("description"), v.get("evidence"),
                    v.get("recommendation"),
                )

        callback(2, f"Web 扫描完成: {len(all_web_vulns)} 个漏洞", 50)

        if not self._running:
            return self._results

        # === Stage 4: Match Exploit Modules ===
        callback(3, f"[4/{total_stages}] 利用模块匹配", 55)
        matched = []
        seen_services = set()
        for svc in (self._results["services"] or []):
            svc_name = (svc.get("service") or "").lower()
            if svc_name in seen_services:
                continue
            seen_services.add(svc_name)

            for key, modules in SERVICE_EXPLOIT_MAP.items():
                if key in svc_name or svc_name in key:
                    for mod_name in modules:
                        if mod_name not in [m["name"] for m in matched]:
                            exploit = exploit_mgr.get_exploit(mod_name) if exploit_mgr else None
                            if exploit:
                                matched.append({
                                    "name": mod_name,
                                    "service": svc_name,
                                    "port": svc.get("port"),
                                    "severity": getattr(exploit, "severity", "MEDIUM"),
                                })
                                callback(3, f"  匹配: {mod_name} -> {svc_name}:{svc.get('port')}", -1)

        # Also match web vulns to exploit modules
        if all_web_vulns:
            for mod_name in ["sqli_exploiter", "ssrf_detector", "cmdi_detector", "cors_checker"]:
                if mod_name not in [m["name"] for m in matched]:
                    exploit = exploit_mgr.get_exploit(mod_name) if exploit_mgr else None
                    if exploit:
                        http_port = web_ports[0]["port"] if web_ports else 80
                        matched.append({
                            "name": mod_name,
                            "service": "http",
                            "port": http_port,
                            "severity": getattr(exploit, "severity", "MEDIUM"),
                        })

        self._results["matched_modules"] = matched
        callback(3, f"匹配完成: {len(matched)} 个利用模块", 60)

        if not self._running:
            return self._results

        # === Stage 5: Vulnerability Check (non-destructive) ===
        callback(4, f"[5/{total_stages}] 漏洞检测（非破坏性）", 65)
        check_results = []
        for mod_info in matched:
            if not self._running:
                break
            mod_name = mod_info["name"]
            port = mod_info["port"]
            try:
                callback(4, f"  检测: {mod_name} -> {target}:{port}", -1)
                result = exploit_mgr.check(mod_name, target, port)
                status = result if isinstance(result, str) else "error"
                check_results.append({"module": mod_name, "port": port, "status": status})
                output = ""
                exploit_obj = exploit_mgr.get_exploit(mod_name)
                if exploit_obj and hasattr(exploit_obj, "get_output"):
                    try:
                        output = exploit_obj.get_output()
                    except Exception:
                        pass
                callback(4, f"    结果: {status}", -1)
                if output:
                    for line in output.split("\n")[:5]:
                        if line.strip():
                            callback(4, f"      {line.strip()}", -1)
            except Exception as e:
                check_results.append({"module": mod_name, "port": port, "status": "error"})
                callback(4, f"    错误: {e}", -1)

        self._results["check_results"] = check_results
        vulnerable_count = sum(1 for r in check_results if r["status"] == "vulnerable" or r["status"] == "success")
        callback(4, f"漏洞检测完成: {vulnerable_count}/{len(check_results)} 发现漏洞", 75)

        if not self._running:
            return self._results

        # === Stage 6: Auto Exploit (optional) ===
        auto_exploit = options.get("auto_exploit", False)
        if auto_exploit:
            callback(5, f"[6/{total_stages}] 自动利用", 80)
            exploit_results = []
            for cr in check_results:
                if not self._running:
                    break
                if cr["status"] not in ("vulnerable", "success"):
                    continue
                mod_name = cr["module"]
                port = cr["port"]
                try:
                    callback(5, f"  执行: {mod_name} -> {target}:{port}", -1)
                    result = exploit_mgr.execute(mod_name, target, port)
                    exploit_results.append({"module": mod_name, "port": port, "result": result})

                    exploit_obj = exploit_mgr.get_exploit(mod_name)
                    if exploit_obj and hasattr(exploit_obj, "get_output"):
                        try:
                            output = exploit_obj.get_output()
                            for line in output.split("\n")[:10]:
                                if line.strip():
                                    callback(5, f"    {line.strip()}", -1)
                        except Exception:
                            pass
                except Exception as e:
                    exploit_results.append({"module": mod_name, "port": port, "result": "error"})
                    callback(5, f"    错误: {e}", -1)

            self._results["exploit_results"] = exploit_results
            callback(5, f"利用完成: {len(exploit_results)} 个模块执行", 90)
        else:
            callback(5, f"[6/{total_stages}] 自动利用（已跳过）", 90)

        if not self._running:
            return self._results

        # === Stage 7: Generate Report ===
        callback(6, f"[7/{total_stages}] 生成报告", 95)
        try:
            from modules.report.generator import ReportGenerator
            gen = ReportGenerator(db)
            md = gen.generate_markdown()
            html = gen.generate_html()

            report_path = f"autopilot_report_{target.replace(':', '_').replace('/', '_')}.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(md)
            self._results["report_path"] = report_path

            html_path = report_path.replace(".md", ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)

            callback(6, f"报告已生成: {report_path}", 100)
        except Exception as e:
            callback(6, f"报告生成失败: {e}", -1)

        return self._results
