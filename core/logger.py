import logging
from datetime import datetime


class Logger:
    def __init__(self, config):
        self.logger = logging.getLogger("DarkVeil")
        self.logger.setLevel(getattr(logging, config.get("log_level", "INFO")))

        fmt = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console = logging.StreamHandler()
        console.setFormatter(fmt)
        self.logger.addHandler(console)

        log_file = config.get("log_file", "darkveil.log")
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)
        except Exception:
            pass

        self._callbacks = []

    def on_message(self, callback):
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        try:
            self._callbacks.remove(callback)
        except ValueError:
            pass

    def _emit(self, level, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        for cb in self._callbacks[:]:
            try:
                cb(timestamp, level, msg)
            except Exception as e:
                self.logger.debug(f"回调异常: {e}")

    def info(self, msg):
        self.logger.info(msg)
        self._emit("INFO", msg)

    def warning(self, msg):
        self.logger.warning(msg)
        self._emit("WARN", msg)

    def error(self, msg):
        self.logger.error(msg)
        self._emit("ERROR", msg)

    def success(self, msg):
        self.logger.info(f"[+] {msg}")
        self._emit("SUCCESS", msg)

    def debug(self, msg):
        self.logger.debug(msg)
        self._emit("DEBUG", msg)
