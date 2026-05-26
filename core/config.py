import os
import json


class Config:
    DEFAULTS = {
        "app_name": "DarkVeil",
        "version": "0.1.0",
        "db_path": "darkveil.db",
        "log_level": "INFO",
        "log_file": "darkveil.log",
        "scan": {
            "max_threads": 100,
            "timeout": 2.0,
            "default_ports": [21, 22, 23, 25, 53, 80, 110, 135, 139, 143,
                              443, 445, 993, 995, 1433, 1521, 3306, 3389,
                              5432, 5900, 6379, 8080, 8443, 8888, 9090, 27017],
            "web_timeout": 10,
        },
        "proxy": {
            "enabled": False,
            "http": "",
            "https": "",
            "socks5": "",
        },
        "exploit": {
            "payloads_dir": "modules/exploit/payloads",
            "modules_dir": "modules/exploit/modules",
        },
        "ui": {
            "theme": "aero",
            "language": "zh-CN",
            "window_width": 1400,
            "window_height": 900,
        },
    }

    def __init__(self, config_file="darkveil.json"):
        self.config_file = config_file
        self.data = self._deep_copy(self.DEFAULTS)
        self.load()

    def _deep_copy(self, d):
        if isinstance(d, dict):
            return {k: self._deep_copy(v) for k, v in d.items()}
        if isinstance(d, list):
            return list(d)
        return d

    def load(self):
        if not os.path.exists(self.config_file):
            return
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            if isinstance(user_cfg, dict):
                self._deep_merge(self.data, user_cfg)
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"[WARN] 配置文件加载失败: {e}")

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"[WARN] 配置文件保存失败: {e}")

    def get(self, key, default=None):
        keys = key.split(".")
        val = self.data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key, value):
        keys = key.split(".")
        d = self.data
        for k in keys[:-1]:
            if not isinstance(d, dict):
                return
            d = d.setdefault(k, {})
        if isinstance(d, dict):
            d[keys[-1]] = value
            self.save()

    def _deep_merge(self, base, override):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self._deep_merge(base[k], v)
            elif isinstance(v, dict) and k in base and not isinstance(base[k], dict):
                pass
            else:
                base[k] = v
