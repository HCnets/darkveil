from datetime import datetime


class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def generate_markdown(self):
        lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats = self.db.get_stats()
        targets = self.db.get_targets()
        vulns = self.db.get_vulnerabilities()

        lines.append("# DarkVeil 安全评估报告")
        lines.append(f"\n生成时间: {now}\n")

        # 概览
        lines.append("## 1. 评估概览\n")
        lines.append(f"| 指标 | 数值 |")
        lines.append(f"|------|------|")
        lines.append(f"| 扫描目标 | {stats.get('targets', 0)} |")
        lines.append(f"| 开放端口 | {stats.get('open_ports', 0)} |")
        lines.append(f"| 漏洞发现 | {stats.get('vulnerabilities', 0)} |")
        lines.append(f"| 利用尝试 | {stats.get('exploits', 0)} |")
        lines.append(f"| 扫描次数 | {stats.get('scans', 0)} |")

        # 漏洞分布
        vuln_by_sev = stats.get("vuln_by_severity", {})
        if vuln_by_sev:
            lines.append("\n### 漏洞严重程度分布\n")
            sev_icons = {"CRITICAL": "!!!", "HIGH": "!!", "MEDIUM": "!", "LOW": "."}
            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                cnt = vuln_by_sev.get(sev, 0)
                if cnt > 0:
                    lines.append(f"- **{sev}**: {cnt}")

        # 目标详情
        if targets:
            lines.append("\n## 2. 目标详情\n")
            for t in targets:
                tid = t.get("id")
                host = t.get("host", "?")
                ip = t.get("ip") or "-"
                first = t.get("first_seen", "-")
                last = t.get("last_seen", "-")

                lines.append(f"### {host} ({ip})\n")
                lines.append(f"- 首次发现: {first}")
                lines.append(f"- 最后活动: {last}")

                ports = self.db.get_ports(tid)
                if ports:
                    lines.append(f"\n**开放端口 ({len(ports)}):**\n")
                    lines.append("| 端口 | 状态 | 服务 | 版本 |")
                    lines.append("|------|------|------|------|")
                    for p in ports:
                        lines.append(f"| {p.get('port')} | {p.get('state')} | {p.get('service') or '-'} | {p.get('version') or '-'} |")

                target_vulns = [v for v in vulns if v.get("target_id") == tid]
                if target_vulns:
                    lines.append(f"\n**漏洞 ({len(target_vulns)}):**\n")
                    lines.append("| 严重程度 | 类型 | 标题 | 描述 |")
                    lines.append("|----------|------|------|------|")
                    for v in target_vulns:
                        lines.append(f"| {v.get('severity')} | {v.get('vuln_type')} | {v.get('title')} | {(v.get('description') or '-')[:60]} |")

                lines.append("")

        # 所有漏洞汇总
        if vulns:
            lines.append("\n## 3. 漏洞汇总\n")
            lines.append("| # | 严重程度 | 类型 | 标题 | 发现时间 |")
            lines.append("|---|----------|------|------|----------|")
            for i, v in enumerate(vulns[:50], 1):
                lines.append(
                    f"| {i} | {v.get('severity')} | {v.get('vuln_type')} | "
                    f"{v.get('title')} | {v.get('found_at', '-')} |"
                )

            critical = [v for v in vulns if v.get("severity") == "CRITICAL"]
            high = [v for v in vulns if v.get("severity") == "HIGH"]
            if critical or high:
                lines.append("\n## 4. 高危漏洞详情\n")
                for v in critical + high:
                    lines.append(f"### [{v.get('severity')}] {v.get('title')}\n")
                    lines.append(f"- 类型: {v.get('vuln_type')}")
                    lines.append(f"- 描述: {v.get('description') or '-'}")
                    if v.get("evidence"):
                        lines.append(f"- 证据: {v.get('evidence')[:200]}")
                    if v.get("recommendation"):
                        lines.append(f"- 建议: {v.get('recommendation')}")
                    lines.append("")

        # 扫描历史
        history = self.db.get_scan_history(20)
        if history:
            lines.append("\n## 5. 扫描历史\n")
            lines.append("| 时间 | 类型 | 目标 | 状态 |")
            lines.append("|------|------|------|------|")
            for h in history:
                lines.append(
                    f"| {h.get('started_at', '-')} | {h.get('scan_type')} | "
                    f"{h.get('target')} | {h.get('status')} |"
                )

        lines.append("\n---\n*报告由 DarkVeil 自动生成*")
        return "\n".join(lines)

    def generate_html(self):
        md = self.generate_markdown()
        html_body = self._md_to_html(md)
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>DarkVeil 安全评估报告</title>
<style>
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; color: #333; line-height: 1.6; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #0078d4; padding-bottom: 10px; }}
h2 {{ color: #0078d4; margin-top: 30px; }}
h3 {{ color: #333; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f5f5f5; font-weight: 600; }}
tr:nth-child(even) {{ background: #f9f9f9; }}
code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 30px 0; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    def _md_to_html(self, md):
        lines = md.split("\n")
        html = []
        in_table = False
        table_header_done = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("## "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("### "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("|") and "|" in stripped[1:]:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if all(set(c) <= set("- :") for c in cells):
                    table_header_done = True
                    continue
                if not in_table:
                    html.append("<table>")
                    in_table = True
                tag = "th" if not table_header_done else "td"
                row = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
                html.append(f"<tr>{row}</tr>")
            elif stripped.startswith("- "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<li>{stripped[2:]}</li>")
            elif stripped.startswith("---"):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append("<hr>")
            elif stripped:
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<p>{stripped}</p>")

        if in_table:
            html.append("</table>")

        return "\n".join(html)
