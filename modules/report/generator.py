from datetime import datetime
from html import escape as html_escape
from modules.report.compliance import (
    generate_owasp_section, generate_cis_section, generate_risk_matrix,
)


class ReportGenerator:
    def __init__(self, db):
        self.db = db

    def _calculate_risk_score(self, stats, vulns):
        score = 0
        vuln_by_sev = stats.get("vuln_by_severity", {})
        score += vuln_by_sev.get("CRITICAL", 0) * 10
        score += vuln_by_sev.get("HIGH", 0) * 5
        score += vuln_by_sev.get("MEDIUM", 0) * 2
        score += vuln_by_sev.get("LOW", 0) * 1
        return min(score, 100)

    def _get_risk_level(self, score):
        if score >= 50:
            return "高危"
        elif score >= 20:
            return "中危"
        elif score > 0:
            return "低危"
        return "安全"

    def generate_markdown(self, sections=None, company_name=""):
        if sections is None:
            sections = {"summary": True, "targets": True, "vulns": True, "high_risk": True,
                        "history": True, "owasp": False, "cis": False, "risk_matrix": False}

        lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats = self.db.get_stats()
        targets = self.db.get_targets()
        vulns = self.db.get_vulnerabilities()

        if company_name:
            lines.append(f"# {company_name} - 安全评估报告")
        else:
            lines.append("# DarkVeil 安全评估报告")
        lines.append(f"\n生成时间: {now}\n")

        # 执行摘要
        if sections.get("summary"):
            risk_score = self._calculate_risk_score(stats, vulns)
            risk_level = self._get_risk_level(risk_score)
            vuln_by_sev = stats.get("vuln_by_severity", {})

            lines.append("## 执行摘要\n")
            lines.append(f"**风险评分: {risk_score}/100 ({risk_level})**\n")
            lines.append(f"| 指标 | 数值 |")
            lines.append(f"|------|------|")
            lines.append(f"| 扫描目标 | {stats.get('targets', 0)} |")
            lines.append(f"| 开放端口 | {stats.get('open_ports', 0)} |")
            lines.append(f"| 漏洞发现 | {stats.get('vulnerabilities', 0)} |")
            lines.append(f"| 利用尝试 | {stats.get('exploits', 0)} |")
            lines.append(f"| 扫描次数 | {stats.get('scans', 0)} |")

            if vuln_by_sev:
                lines.append("\n### 漏洞严重程度分布\n")
                for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    cnt = vuln_by_sev.get(sev, 0)
                    if cnt > 0:
                        lines.append(f"- **{sev}**: {cnt}")

            # Top 3 findings
            critical_high = [v for v in vulns if v.get("severity") in ("CRITICAL", "HIGH")]
            if critical_high:
                lines.append("\n### Top 3 关键发现\n")
                for i, v in enumerate(critical_high[:3], 1):
                    lines.append(f"{i}. **[{v.get('severity')}] {v.get('title')}** - {v.get('description', '')[:80]}")

            # Recommendations
            lines.append("\n### 建议\n")
            if vuln_by_sev.get("CRITICAL", 0) > 0:
                lines.append("- 立即修复所有 CRITICAL 级别漏洞")
            if vuln_by_sev.get("HIGH", 0) > 0:
                lines.append("- 尽快处理 HIGH 级别漏洞")
            if stats.get("open_ports", 0) > 10:
                lines.append("- 审查开放端口，关闭不必要的服务")
            if not vulns:
                lines.append("- 当前未发现已知漏洞，建议定期复查")
            lines.append("")

        # 目标详情
        if sections.get("targets") and targets:
            lines.append("\n## 目标详情\n")
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

                if sections.get("vulns"):
                    target_vulns = [v for v in vulns if v.get("target_id") == tid]
                    if target_vulns:
                        lines.append(f"\n**漏洞 ({len(target_vulns)}):**\n")
                        lines.append("| 严重程度 | 类型 | 标题 | 描述 |")
                        lines.append("|----------|------|------|------|")
                        for v in target_vulns:
                            lines.append(f"| {v.get('severity')} | {v.get('vuln_type')} | {v.get('title')} | {(v.get('description') or '-')[:60]} |")

                lines.append("")

        # 漏洞汇总
        if sections.get("vulns") and vulns:
            lines.append("\n## 漏洞汇总\n")
            lines.append("| # | 严重程度 | 类型 | 标题 | 发现时间 |")
            lines.append("|---|----------|------|------|----------|")
            for i, v in enumerate(vulns[:50], 1):
                lines.append(
                    f"| {i} | {v.get('severity')} | {v.get('vuln_type')} | "
                    f"{v.get('title')} | {v.get('found_at', '-')} |"
                )

        # 高危漏洞详情
        if sections.get("high_risk") and vulns:
            critical = [v for v in vulns if v.get("severity") == "CRITICAL"]
            high = [v for v in vulns if v.get("severity") == "HIGH"]
            if critical or high:
                lines.append("\n## 高危漏洞详情\n")
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
        if sections.get("history"):
            history = self.db.get_scan_history(20)
            if history:
                lines.append("\n## 扫描历史\n")
                lines.append("| 时间 | 类型 | 目标 | 状态 |")
                lines.append("|------|------|------|------|")
                for h in history:
                    lines.append(
                        f"| {h.get('started_at', '-')} | {h.get('scan_type')} | "
                        f"{h.get('target')} | {h.get('status')} |"
                    )

        # OWASP Top 10 合规
        if sections.get("owasp") and vulns:
            owasp_md = generate_owasp_section(vulns)
            if owasp_md:
                lines.append(owasp_md)

        # CIS Benchmark 合规
        if sections.get("cis") and vulns:
            cis_md = generate_cis_section(vulns)
            if cis_md:
                lines.append(cis_md)

        # 风险矩阵
        if sections.get("risk_matrix") and vulns:
            matrix_md = generate_risk_matrix(vulns)
            if matrix_md:
                lines.append(matrix_md)

        lines.append("\n---\n*报告由 DarkVeil 自动生成*")
        return "\n".join(lines)

    def generate_html(self, sections=None, company_name=""):
        md = self.generate_markdown(sections=sections, company_name=company_name)
        html_body = self._md_to_html(md)
        report_title = f"{company_name} - 安全评估报告" if company_name else "DarkVeil 安全评估报告"
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{html_escape(report_title)}</title>
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
                html.append(f"<h1>{html_escape(stripped[2:])}</h1>")
            elif stripped.startswith("## "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<h2>{html_escape(stripped[3:])}</h2>")
            elif stripped.startswith("### "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<h3>{html_escape(stripped[4:])}</h3>")
            elif stripped.startswith("|") and "|" in stripped[1:]:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if all(set(c) <= set("- :") for c in cells):
                    table_header_done = True
                    continue
                if not in_table:
                    html.append("<table>")
                    in_table = True
                tag = "th" if not table_header_done else "td"
                row = "".join(f"<{tag}>{html_escape(c)}</{tag}>" for c in cells)
                html.append(f"<tr>{row}</tr>")
            elif stripped.startswith("- "):
                if in_table:
                    html.append("</table>")
                    in_table = False
                    table_header_done = False
                html.append(f"<li>{html_escape(stripped[2:])}</li>")
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
                html.append(f"<p>{html_escape(stripped)}</p>")

        if in_table:
            html.append("</table>")

        return "\n".join(html)
