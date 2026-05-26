import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox


def main():
    db = None
    try:
        from core.config import Config
        from core.logger import Logger
        from core.db import Database
        from core.engine import Engine
        from gui.main_window import MainWindow

        config = Config()
        logger = Logger(config)
        db = Database(config, logger)
        engine = Engine(config, db, logger)

        from gui.widgets.themes import ThemeEngine, ALL_THEMES
        theme_engine = ThemeEngine()
        theme_engine.register_all(ALL_THEMES)

        app = QApplication(sys.argv)
        app.setApplicationName("DarkVeil")
        app.setStyle("Fusion")

        saved_theme = config.get("ui.theme", "modern")
        if not theme_engine.apply(saved_theme, app):
            theme_engine.apply("modern", app)

        window = MainWindow(engine, config, logger, theme_engine)
        window.show()

        exit_code = app.exec()
        db.close()
        sys.exit(exit_code)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        print(f"[FATAL] {error_msg}", file=sys.stderr)
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "DarkVeil 启动失败", error_msg)
        except Exception:
            pass
        if db:
            try:
                db.close()
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
