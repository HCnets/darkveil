import json
import base64
from modules.http_utils import get_session


class FofaClient:
    BASE_URL = "https://fofa.info/api/v1/search/all"

    def __init__(self, config, db=None, logger=None):
        self.config = config
        self.db = db
        self.logger = logger
        self._api_key = config.get("intel.fofa_api_key", "") if config else ""
        self._email = config.get("intel.fofa_email", "") if config else ""
        self._session = None

    def _get_session(self):
        if self._session is None:
            self._session = get_session(self.config)
        return self._session

    def search(self, query, fields="ip,port,host,title,server", size=100):
        if not self._api_key or not self._email:
            return {"error": "Fofa API key 或 email 未配置"}

        cache_key = f"search:{query}:{size}"
        if self.db:
            cache = self.db.get_intel_cache("fofa", cache_key)
            if cache:
                return cache

        try:
            qbase64 = base64.b64encode(query.encode("utf-8")).decode("utf-8")
            params = {
                "email": self._email,
                "key": self._api_key,
                "qbase64": qbase64,
                "fields": fields,
                "size": size,
            }
            resp = self._get_session().get(self.BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if data.get("error"):
                return {"error": data.get("errmsg", "Unknown error")}

            results = []
            field_names = fields.split(",")
            for row in data.get("results", []):
                item = {}
                for i, name in enumerate(field_names):
                    item[name] = row[i] if i < len(row) else ""
                results.append(item)

            if self.db and results:
                self.db.add_intel_query("fofa", cache_key, json.dumps(results, ensure_ascii=False))
            return {"total": data.get("size", 0), "results": results}
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fofa 查询失败: {e}")
            return {"error": str(e)}

    def host_info(self, ip):
        return self.search(f'ip="{ip}"', fields="ip,port,host,title,server,protocol", size=200)
