OWASP_2021_MAP = {
    "weak_auth": ("A07:2021", "Identification and Authentication Failures"),
    "sqli": ("A03:2021", "Injection"),
    "ssrf": ("A10:2021", "Server-Side Request Forgery"),
    "command_injection": ("A03:2021", "Injection"),
    "file_upload": ("A04:2021", "Insecure Design"),
    "unauthorized_access": ("A01:2021", "Broken Access Control"),
    "privesc": ("A01:2021", "Broken Access Control"),
    "info_disclosure": ("A01:2021", "Broken Access Control"),
    "misconfiguration": ("A05:2021", "Security Misconfiguration"),
    "cve": ("A06:2021", "Vulnerable and Outdated Components"),
    "recon": ("A05:2021", "Security Misconfiguration"),
    "fuzzing": ("A03:2021", "Injection"),
    "payload": ("A03:2021", "Injection"),
    "web": ("A05:2021", "Security Misconfiguration"),
    "persistence": ("A01:2021", "Broken Access Control"),
}

CIS_CONTROLS_MAP = {
    "weak_auth": ["CIS 5.2", "CIS 5.3"],
    "sqli": ["CIS 16.1"],
    "ssrf": ["CIS 16.1"],
    "command_injection": ["CIS 16.1"],
    "misconfiguration": ["CIS 4.1", "CIS 4.2"],
    "privesc": ["CIS 5.4", "CIS 6.8"],
    "info_disclosure": ["CIS 3.3"],
    "cve": ["CIS 7.1", "CIS 7.2"],
    "unauthorized_access": ["CIS 5.1", "CIS 6.1"],
    "persistence": ["CIS 8.2"],
    "file_upload": ["CIS 16.1"],
    "fuzzing": ["CIS 16.1"],
}


def get_owasp_category(vuln_type):
    return OWASP_2021_MAP.get(vuln_type, ("A00:2021", "Uncategorized"))


def get_cis_controls(vuln_type):
    return CIS_CONTROLS_MAP.get(vuln_type, [])


def generate_owasp_section(vulns):
    from collections import defaultdict
    grouped = defaultdict(list)
    for v in vulns:
        vt = v.get("vuln_type", "")
        code, name = get_owasp_category(vt)
        grouped[(code, name)].append(v)

    if not grouped:
        return ""

    lines = ["\n## OWASP Top 10 2021 合规映射\n"]
    for (code, name) in sorted(grouped.keys()):
        items = grouped[(code, name)]
        lines.append(f"### {code} - {name} ({len(items)} 项)\n")
        lines.append("| 严重程度 | 标题 | 目标 |")
        lines.append("|----------|------|------|")
        for v in items:
            lines.append(f"| {v.get('severity', '-')} | {v.get('title', '-')} | {v.get('target_id', '-')} |")
        lines.append("")
    return "\n".join(lines)


def generate_cis_section(vulns):
    from collections import defaultdict
    grouped = defaultdict(list)
    for v in vulns:
        vt = v.get("vuln_type", "")
        controls = get_cis_controls(vt)
        for ctrl in controls:
            grouped[ctrl].append(v)

    if not grouped:
        return ""

    lines = ["\n## CIS Benchmark 合规映射\n"]
    for ctrl in sorted(grouped.keys()):
        items = grouped[ctrl]
        lines.append(f"### {ctrl} ({len(items)} 项)\n")
        lines.append("| 严重程度 | vuln_type | 标题 |")
        lines.append("|----------|-----------|------|")
        for v in items:
            lines.append(f"| {v.get('severity', '-')} | {v.get('vuln_type', '-')} | {v.get('title', '-')} |")
        lines.append("")
    return "\n".join(lines)


def generate_risk_matrix(vulns):
    severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    likelihoods = ["Certain", "Likely", "Possible", "Unlikely"]

    matrix = {s: {l: 0 for l in likelihoods} for s in severities}

    sev_likeliness = {
        "CRITICAL": "Certain",
        "HIGH": "Likely",
        "MEDIUM": "Possible",
        "LOW": "Unlikely",
    }

    for v in vulns:
        sev = v.get("severity", "MEDIUM")
        likelihood = sev_likeliness.get(sev, "Possible")
        if sev in matrix:
            matrix[sev][likelihood] += 1

    lines = ["\n## 风险矩阵\n"]
    lines.append("| 严重程度 \\ 可能性 | Certain | Likely | Possible | Unlikely |")
    lines.append("|-------------------|---------|--------|----------|----------|")
    for sev in severities:
        cells = []
        for l in likelihoods:
            cnt = matrix[sev][l]
            if cnt > 0:
                cells.append(f"**{cnt}**")
            else:
                cells.append("-")
        lines.append(f"| {sev} | {' | '.join(cells)} |")
    lines.append("")
    return "\n".join(lines)
