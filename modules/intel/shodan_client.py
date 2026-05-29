import json
from modules.http_utils import get_session

try:
    import shodan as shodan_lib
    _HAS_SHODAN = True
except ImportError:
    _HAS_SHODAN = False


class ShodanClient:
    BASE_URL = "https://api.shodan.io"

    def __init__(self, config, db=None, logger=None):
        self.config = config
        self.db = db
        self.logger = logger
        self._api_key = config.get("intel.shodan_api_key", "") if config else ""
        self._session = None

    def _get_session(self):
        if self._session is None:
            self._session = get_session(self.config)
        return self._session

    def _api_get(self, path, params=None):
        if not self._api_key:
            raise ValueError("Shodan API key 未配置")
        if params is None:
            params = {}
        params["key"] = self._api_key
        url = f"{self.BASE_URL}{path}"
        resp = self._get_session().get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def host_lookup(self, ip):
        cache_key = f"host:{ip}"
        if self.db:
            cache = self.db.get_intel_cache("shodan", cache_key)
            if cache:
                return cache

        try:
            if _HAS_SHODAN:
                api = shodan_lib.Shodan(self._api_key)
                data = api.host(ip)
            else:
                data = self._api_get(f"/shodan/host/{ip}")

            result = {
                "ip": data.get("ip_str", ip),
                "os": data.get("os") or "Unknown",
                "org": data.get("org", ""),
                "ports": data.get("ports", []),
                "vulns": data.get("vulns", []),
                "hostnames": data.get("hostnames", []),
                "country": data.get("country_name", ""),
                "city": data.get("city", ""),
                "banners": [],
            }
            for svc in data.get("data", [])[:20]:
                result["banners"].append({
                    "port": svc.get("port"),
                    "transport": svc.get("transport", "tcp"),
                    "product": svc.get("product", ""),
                    "version": svc.get("version", ""),
                    "banner": (svc.get("data", "") or "")[:100],
                })

            if self.db:
                self.db.add_intel_query("shodan", cache_key, json.dumps(result, ensure_ascii=False))
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Shodan host 查询失败: {e}")
            return {"error": str(e)}

    def search(self, query, limit=100):
        cache_key = f"search:{query}:{limit}"
        if self.db:
            cache = self.db.get_intel_cache("shodan", cache_key)
            if cache:
                return cache

        try:
            if _HAS_SHODAN:
                api = shodan_lib.Shodan(self._api_key)
                data = api.search(query, limit=limit)
            else:
                data = self._api_get("/shodan/host/search", {"query": query, "limit": limit})

            results = []
            for match in data.get("matches", [])[:limit]:
                results.append({
                    "ip": match.get("ip_str", ""),
                    "port": match.get("port"),
                    "org": match.get("org", ""),
                    "product": match.get("product", ""),
                    "version": match.get("version", ""),
                    "banner": (match.get("data", "") or "")[:100],
                    "country": match.get("location", {}).get("country_name", ""),
                })

            if self.db and results:
                self.db.add_intel_query("shodan", cache_key, json.dumps(results, ensure_ascii=False))
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Shodan search 失败: {e}")
            return []

    def vulns_for_host(self, ip):
        try:
            data = self.host_lookup(ip)
            return data.get("vulns", [])
        except Exception:
            return []
