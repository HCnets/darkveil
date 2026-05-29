import json
import urllib.request
import urllib.parse


class NVDClient:
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def __init__(self, config, db=None, logger=None):
        self.config = config
        self.db = db
        self.logger = logger
        self._api_key = config.get("intel.nvd_api_key", "") if config else ""

    def _do_request(self, params):
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "DarkVeil/2.0")
        if self._api_key:
            req.add_header("apiKey", self._api_key)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _parse_cve(self, item):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "")
        desc_data = cve.get("descriptions", [])
        desc = ""
        for d in desc_data:
            if d.get("lang") == "en":
                desc = d.get("value", "")
                break

        severity = "MEDIUM"
        cvss_score = 0.0
        metrics = cve.get("metrics", {})
        for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            metric_list = metrics.get(metric_key, [])
            if metric_list:
                cvss_data = metric_list[0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore", 0.0)
                severity = cvss_data.get("baseSeverity", "MEDIUM").upper()
                break

        published = cve.get("published", "")[:10]
        return {
            "cve_id": cve_id,
            "severity": severity,
            "cvss_score": cvss_score,
            "description": desc[:200],
            "published": published,
        }

    def query(self, keyword, max_results=20):
        if self.db:
            cache = self.db.get_intel_cache("nvd", keyword)
            if cache:
                return cache

        try:
            params = {"keywordSearch": keyword, "resultsPerPage": max_results}
            data = self._do_request(params)
            vulns = []
            for item in data.get("vulnerabilities", []):
                vulns.append(self._parse_cve(item))

            if self.db and vulns:
                self.db.add_intel_query("nvd", keyword, json.dumps(vulns, ensure_ascii=False))
            return vulns
        except Exception as e:
            if self.logger:
                self.logger.error(f"NVD 查询失败: {e}")
            return []

    def query_by_cve_id(self, cve_id):
        if self.db:
            cache = self.db.get_intel_cache("nvd", cve_id)
            if cache:
                return cache

        try:
            params = {"cveId": cve_id}
            data = self._do_request(params)
            vulns = []
            for item in data.get("vulnerabilities", []):
                vulns.append(self._parse_cve(item))

            if self.db and vulns:
                self.db.add_intel_query("nvd", cve_id, json.dumps(vulns, ensure_ascii=False))
            return vulns
        except Exception as e:
            if self.logger:
                self.logger.error(f"NVD CVE 查询失败: {e}")
            return []

    def query_by_cpe(self, cpe_string, max_results=20):
        if self.db:
            cache = self.db.get_intel_cache("nvd_cpe", cpe_string)
            if cache:
                return cache

        try:
            params = {"cpeName": cpe_string, "resultsPerPage": max_results}
            data = self._do_request(params)
            vulns = []
            for item in data.get("vulnerabilities", []):
                vulns.append(self._parse_cve(item))

            if self.db and vulns:
                self.db.add_intel_query("nvd_cpe", cpe_string, json.dumps(vulns, ensure_ascii=False))
            return vulns
        except Exception as e:
            if self.logger:
                self.logger.error(f"NVD CPE 查询失败: {e}")
            return []
