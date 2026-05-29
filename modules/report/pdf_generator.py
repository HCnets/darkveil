import os
from datetime import datetime

from fpdf import FPDF


# Default font paths for Chinese support
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
    "C:/Windows/Fonts/simsun.ttc",     # SimSun
    "C:/Windows/Fonts/simhei.ttf",     # SimHei
    "C:/Windows/Fonts/msyhbd.ttc",     # YaHei Bold
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _find_cjk_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            return p
    return None


class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self._font_loaded = False
        font_path = _find_cjk_font()
        if font_path:
            try:
                self.add_font("CJK", "", font_path, uni=True)
                self._font_loaded = True
            except Exception:
                pass

    def _set_font(self, style="", size=10):
        if self._font_loaded:
            self.set_font("CJK", style, size)
        else:
            self.set_font("Helvetica", style, size)

    def header(self):
        self._set_font("B", 14)
        self.cell(0, 10, "DarkVeil Security Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self._set_font("", 9)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 6, ts, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self._set_font("", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self._set_font("B", 13)
        self.set_text_color(0, 120, 212)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def sub_title(self, title):
        self._set_font("B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self._set_font("", 10)
        self.multi_cell(0, 6, str(text or "-"))
        self.ln(2)

    def kv_line(self, key, value):
        self._set_font("B", 10)
        self.cell(45, 7, str(key) + ":")
        self._set_font("", 10)
        self.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")

    def add_table(self, headers, rows, col_widths=None):
        if not rows:
            return
        if col_widths is None:
            w = (self.w - 20) / len(headers)
            col_widths = [w] * len(headers)

        # Header
        self._set_font("B", 9)
        self.set_fill_color(240, 240, 240)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, str(h), border=1, fill=True)
        self.ln()

        # Rows
        self._set_font("", 9)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(249, 249, 249)
            for i, cell in enumerate(row):
                text = str(cell or "-")[:40]
                self.cell(col_widths[i], 6, text, border=1, fill=fill)
            self.ln()
            fill = not fill
        self.ln(3)

    def severity_text(self, severity, text):
        colors = {
            "CRITICAL": (198, 40, 40),
            "HIGH": (230, 81, 0),
            "MEDIUM": (249, 168, 37),
            "LOW": (102, 102, 102),
        }
        r, g, b = colors.get(severity, (0, 0, 0))
        self._set_font("B", 10)
        self.set_text_color(r, g, b)
        self.cell(25, 7, f"[{severity}]")
        self.set_text_color(0, 0, 0)
        self._set_font("", 10)
        self.cell(0, 7, str(text), new_x="LMARGIN", new_y="NEXT")


def generate_pdf(db, output_path, company_name="", logo_path="", sections=None):
    """Generate a PDF report from database."""
    if sections is None:
        sections = {"summary": True, "targets": True, "vulns": True, "high_risk": True,
                    "history": True, "owasp": False, "cis": False, "risk_matrix": False}

    pdf = PDFReport()
    pdf.alias_nb_pages()

    # Cover page
    pdf.add_page()
    pdf.ln(60)
    pdf._set_font("B", 28)
    pdf.set_text_color(0, 120, 212)
    cover_title = f"{company_name} - 安全评估报告" if company_name else "DarkVeil 安全评估报告"
    pdf.cell(0, 15, cover_title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=(pdf.w - 60) / 2, w=60)
            pdf.ln(10)
        except Exception:
            pass

    pdf._set_font("", 12)
    ts = datetime.now().strftime("%Y-%m-%d")
    pdf.cell(0, 8, f"报告日期: {ts}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, "分类: 机密", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, "由 DarkVeil 自动生成", new_x="LMARGIN", new_y="NEXT", align="C")

    # TOC page
    pdf.add_page()
    pdf.section_title("目录")
    toc_items = [
        ("1", "评估概览"),
        ("2", "目标详情"),
        ("3", "漏洞汇总"),
        ("4", "高危漏洞详情"),
        ("5", "扫描历史"),
    ]
    if sections.get("owasp"):
        toc_items.append(("6", "OWASP Top 10 2021 合规映射"))
    if sections.get("cis"):
        toc_items.append(("7", "CIS Benchmark 合规映射"))
    if sections.get("risk_matrix"):
        toc_items.append(("8", "风险矩阵"))

    for num, title in toc_items:
        pdf._set_font("", 11)
        pdf.cell(0, 8, f"  {num}. {title}", new_x="LMARGIN", new_y="NEXT")

    stats = db.get_stats()
    targets = db.get_targets()
    vulns = db.get_vulnerabilities()

    # Overview
    pdf.section_title("1. Assessment Overview")
    pdf.kv_line("Targets", stats.get("targets", 0))
    pdf.kv_line("Open Ports", stats.get("open_ports", 0))
    pdf.kv_line("Vulnerabilities", stats.get("vulnerabilities", 0))
    pdf.kv_line("Exploit Attempts", stats.get("exploits", 0))
    pdf.kv_line("Total Scans", stats.get("scans", 0))
    pdf.ln(5)

    # Vuln severity distribution
    vuln_by_sev = stats.get("vuln_by_severity", {})
    if vuln_by_sev:
        pdf.sub_title("Vulnerability Severity Distribution")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            cnt = vuln_by_sev.get(sev, 0)
            if cnt > 0:
                pdf.severity_text(sev, f"{cnt}")
        pdf.ln(5)

    # Target details
    if targets:
        pdf.section_title("2. Target Details")
        for t in targets:
            tid = t.get("id")
            host = t.get("host", "?")
            ip = t.get("ip") or "-"
            pdf.sub_title(f"{host} ({ip})")
            pdf.kv_line("First Seen", t.get("first_seen", "-"))
            pdf.kv_line("Last Seen", t.get("last_seen", "-"))

            ports = db.get_ports(tid)
            if ports:
                pdf.ln(3)
                pdf.body_text(f"Open Ports ({len(ports)}):")
                rows = [[str(p["port"]), p.get("state", ""),
                         p.get("service") or "-", p.get("version") or "-"]
                        for p in ports]
                pdf.add_table(["Port", "State", "Service", "Version"], rows,
                              [25, 25, 50, 80])

            target_vulns = [v for v in vulns if v.get("target_id") == tid]
            if target_vulns:
                pdf.body_text(f"Vulnerabilities ({len(target_vulns)}):")
                for v in target_vulns:
                    pdf.severity_text(
                        v.get("severity", ""),
                        f"{v.get('vuln_type', '')} - {v.get('title', '')}"
                    )
                    if v.get("description"):
                        pdf._set_font("", 9)
                        pdf.multi_cell(0, 5, f"  {v['description'][:150]}")
                pdf.ln(3)

    # All vulnerabilities
    if vulns:
        pdf.add_page()
        pdf.section_title("3. Vulnerability Summary")
        rows = []
        for i, v in enumerate(vulns[:50], 1):
            rows.append([
                str(i), v.get("severity", ""), v.get("vuln_type", ""),
                (v.get("title") or "")[:35], (v.get("found_at") or "-")[:16]
            ])
        pdf.add_table(["#", "Severity", "Type", "Title", "Found"], rows,
                      [10, 25, 30, 65, 40])

        # High severity details
        critical_high = [v for v in vulns if v.get("severity") in ("CRITICAL", "HIGH")]
        if critical_high:
            pdf.section_title("4. Critical/High Vulnerability Details")
            for v in critical_high:
                pdf.severity_text(v.get("severity", ""), v.get("title", ""))
                pdf.kv_line("Type", v.get("vuln_type", "-"))
                pdf.body_text(f"Description: {v.get('description', '-')}")
                if v.get("evidence"):
                    pdf._set_font("", 9)
                    pdf.multi_cell(0, 5, f"Evidence: {v['evidence'][:200]}")
                if v.get("recommendation"):
                    pdf.kv_line("Recommendation", v.get("recommendation"))
                pdf.ln(3)

    # Scan history
    history = db.get_scan_history(20)
    if history:
        pdf.add_page()
        pdf.section_title("5. Scan History")
        rows = []
        for h in history:
            rows.append([
                (h.get("started_at") or "-")[:16],
                h.get("scan_type", ""),
                h.get("target", ""),
                h.get("status", ""),
            ])
        pdf.add_table(["Time", "Type", "Target", "Status"], rows,
                      [40, 25, 60, 30])

    # OWASP Top 10
    if sections.get("owasp") and vulns:
        from modules.report.compliance import get_owasp_category
        from collections import defaultdict
        grouped = defaultdict(list)
        for v in vulns:
            code, name = get_owasp_category(v.get("vuln_type", ""))
            grouped[(code, name)].append(v)
        if grouped:
            pdf.add_page()
            pdf.section_title("OWASP Top 10 2021 合规映射")
            for (code, name) in sorted(grouped.keys()):
                items = grouped[(code, name)]
                pdf.sub_title(f"{code} - {name} ({len(items)} 项)")
                rows = []
                for v in items[:15]:
                    rows.append([
                        v.get("severity", ""), (v.get("title") or "")[:40],
                        str(v.get("target_id", "")),
                    ])
                pdf.add_table(["严重程度", "标题", "目标"], rows, [30, 80, 40])

    # CIS Benchmark
    if sections.get("cis") and vulns:
        from modules.report.compliance import get_cis_controls
        from collections import defaultdict
        grouped = defaultdict(list)
        for v in vulns:
            controls = get_cis_controls(v.get("vuln_type", ""))
            for ctrl in controls:
                grouped[ctrl].append(v)
        if grouped:
            pdf.add_page()
            pdf.section_title("CIS Benchmark 合规映射")
            for ctrl in sorted(grouped.keys()):
                items = grouped[ctrl]
                pdf.sub_title(f"{ctrl} ({len(items)} 项)")
                rows = []
                for v in items[:15]:
                    rows.append([
                        v.get("severity", ""), v.get("vuln_type", ""),
                        (v.get("title") or "")[:35],
                    ])
                pdf.add_table(["严重程度", "类型", "标题"], rows, [30, 35, 80])

    # Risk matrix
    if sections.get("risk_matrix") and vulns:
        pdf.add_page()
        pdf.section_title("风险矩阵")
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        likelihoods = ["Certain", "Likely", "Possible", "Unlikely"]
        sev_likeliness = {"CRITICAL": "Certain", "HIGH": "Likely", "MEDIUM": "Possible", "LOW": "Unlikely"}
        matrix = {s: {l: 0 for l in likelihoods} for s in severities}
        for v in vulns:
            sev = v.get("severity", "MEDIUM")
            lk = sev_likeliness.get(sev, "Possible")
            if sev in matrix:
                matrix[sev][lk] += 1

        rows = []
        for sev in severities:
            row = [sev]
            for l in likelihoods:
                cnt = matrix[sev][l]
                row.append(str(cnt) if cnt > 0 else "-")
            rows.append(row)
        pdf.add_table(
            ["严重程度 \\ 可能性", "Certain", "Likely", "Possible", "Unlikely"],
            rows, [35, 30, 30, 30, 30],
        )

    pdf.output(output_path)
    return output_path
