import importlib
import os
import pkgutil


class Engine:
    def __init__(self, config, db, logger):
        self.config = config
        self.db = db
        self.logger = logger
        self.modules = {}
        self._callbacks = {"scan_progress": [], "scan_complete": [], "log": []}
        self.logger.info("引擎初始化完成")

    def register_module(self, name, module_instance):
        self.modules[name] = module_instance
        self.logger.info(f"模块已注册: {name}")

    def get_module(self, name):
        return self.modules.get(name)

    def on(self, event, callback):
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def emit(self, event, *args, **kwargs):
        for cb in self._callbacks.get(event, []):
            try:
                cb(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"事件回调异常 [{event}]: {e}")

    def auto_discover_modules(self, package_path, package_name):
        if not os.path.exists(package_path):
            return
        for importer, modname, ispkg in pkgutil.iter_modules([package_path]):
            if modname.startswith("_"):
                continue
            try:
                module = importlib.import_module(f"{package_name}.{modname}")
                if hasattr(module, "register"):
                    module.register(self)
            except Exception as e:
                self.logger.error(f"加载模块失败 [{modname}]: {e}")
