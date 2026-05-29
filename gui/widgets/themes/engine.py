from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont


class ThemeBase:
    """主题基类 — 所有主题必须继承并实现 generate_qss()"""

    name = "unnamed"
    display_name = "Unnamed Theme"
    description = ""
    font_family = "Segoe UI"
    font_size = 9

    # --- 颜色属性（子类覆盖） ---
    @property
    def window_bg(self): return "#f0f0f0"

    @property
    def panel_bg(self): return "#ffffff"

    @property
    def sidebar_bg(self): return "#2b2b2b"

    @property
    def sidebar_fg(self): return "#e0e0e0"

    @property
    def sidebar_active(self): return "#0078d4"

    @property
    def accent(self): return "#0078d4"

    @property
    def text_primary(self): return "#1a1a1a"

    @property
    def text_secondary(self): return "#666666"

    @property
    def border_color(self): return "#d0d0d0"

    @property
    def input_bg(self): return "#ffffff"

    @property
    def input_border(self): return "#c0c0c0"

    @property
    def button_bg(self): return "#e1e1e1"

    @property
    def button_hover(self): return "#d0d0d0"

    @property
    def button_pressed(self): return "#c0c0c0"

    @property
    def table_header_bg(self): return "#f5f5f5"

    @property
    def table_alt_row(self): return "#f9f9f9"

    @property
    def selection_bg(self): return "#0078d4"

    @property
    def selection_fg(self): return "#ffffff"

    @property
    def scrollbar_bg(self): return "#f0f0f0"

    @property
    def scrollbar_handle(self): return "#c0c0c0"

    @property
    def terminal_bg(self): return "#1e1e1e"

    @property
    def terminal_fg(self): return "#cccccc"

    @property
    def tooltip_bg(self): return "#2b2b2b"

    @property
    def tooltip_fg(self): return "#ffffff"

    @property
    def danger(self): return "#d83b01"

    @property
    def success(self): return "#107c10"

    @property
    def warning(self): return "#ffb900"

    def generate_qss(self) -> str:
        """返回完整 QSS 样式表，子类必须实现"""
        raise NotImplementedError

    def _dashboard_qss(self) -> str:
        """Dashboard 和终端组件的通用 QSS，子类在 generate_qss() 中拼接"""
        return f"""
QLabel#stat_value {{
    font-size: 28px;
    font-weight: 700;
    font-family: "Consolas", "Cascadia Mono", monospace;
    background: transparent;
}}

QLabel#stat_label {{
    font-size: 11px;
    color: {self.text_secondary};
    background: transparent;
}}

QFrame#activity_item {{
    background: transparent;
    border: none;
    border-bottom: 1px solid {self.border_color};
}}

QLabel#activity_time {{
    color: {self.text_secondary};
    font-size: 10px;
    font-family: "Consolas", "Cascadia Mono", monospace;
    background: transparent;
}}

QLabel#activity_action {{
    color: {self.accent};
    font-size: 11px;
    background: transparent;
}}

QLabel#activity_target {{
    color: {self.text_primary};
    font-size: 11px;
    background: transparent;
}}

QLabel#panel_header {{
    color: {self.text_primary};
    font-weight: 600;
    padding: 10px 12px;
    border-bottom: 1px solid {self.border_color};
    background: transparent;
}}

QWidget#panel_body, QLabel#panel_body {{
    color: {self.text_secondary};
    padding: 12px;
    background: transparent;
}}

QTextEdit#terminal {{
    background-color: {self.terminal_bg};
    color: {self.terminal_fg};
    border: none;
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: #264f78;
}}

/* === Shared interaction states (all themes) === */
QPushButton:focus {{
    outline: 2px solid {self.accent};
    outline-offset: 2px;
}}

QCheckBox:focus::indicator {{
    border: 2px solid {self.accent};
}}

QTabBar::tab:focus {{
    outline: 2px solid {self.accent};
    outline-offset: -2px;
}}

QCheckBox:hover {{
    color: {self.accent};
}}

QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
    background-color: {self.scrollbar_bg};
    color: {self.text_secondary};
    border-color: {self.border_color};
}}

QCheckBox:disabled {{
    color: {self.text_secondary};
}}
"""

    def apply_palette(self, app: QApplication):
        """应用 QPalette（部分控件不支持 QSS）"""
        pal = app.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(self.window_bg))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(self.text_primary))
        pal.setColor(QPalette.ColorRole.Base, QColor(self.input_bg))
        pal.setColor(QPalette.ColorRole.Text, QColor(self.text_primary))
        pal.setColor(QPalette.ColorRole.Button, QColor(self.button_bg))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(self.text_primary))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(self.selection_bg))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(self.selection_fg))
        pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(self.tooltip_bg))
        pal.setColor(QPalette.ColorRole.ToolTipText, QColor(self.tooltip_fg))
        app.setPalette(pal)

        font = QFont(self.font_family, self.font_size)
        app.setFont(font)


class ThemeEngine:
    """主题引擎 — 注册、切换、应用主题"""

    def __init__(self):
        self._themes: dict[str, ThemeBase] = {}
        self._current: ThemeBase | None = None

    def register(self, theme: ThemeBase):
        self._themes[theme.name] = theme

    def register_all(self, themes: list):
        for t in themes:
            if isinstance(t, type):
                t = t()
            self.register(t)

    def get(self, name: str) -> ThemeBase | None:
        return self._themes.get(name)

    def list_themes(self) -> list[dict]:
        return [
            {"name": t.name, "display_name": t.display_name, "description": t.description}
            for t in self._themes.values()
        ]

    @property
    def current(self) -> ThemeBase | None:
        return self._current

    def apply(self, name: str, app: QApplication) -> bool:
        theme = self._themes.get(name)
        if not theme:
            return False
        self._current = theme
        app.setStyleSheet(theme.generate_qss())
        theme.apply_palette(app)
        return True
