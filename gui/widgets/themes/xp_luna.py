from .engine import ThemeBase


class _XPLunaBase(ThemeBase):
    """XP Luna 共用基础样式"""
    font_family = "Tahoma"
    font_size = 8

    # 子类覆盖这三组颜色
    _title_start = "#0054e3"
    _title_end = "#4580c4"
    _accent = "#0054e3"
    _start_btn = "#3c8f3c"
    _start_hover = "#4aa04a"
    _panel_border = "#0054e3"
    _sidebar_bg = "#1b3a6b"
    _sidebar_active_bg = "#2b5aab"

    @property
    def window_bg(self): return "#d4d0c8"
    @property
    def panel_bg(self): return "#ffffff"
    @property
    def sidebar_bg(self): return self._sidebar_bg
    @property
    def sidebar_fg(self): return "#d4e1f7"
    @property
    def sidebar_active(self): return "#ffffff"
    @property
    def accent(self): return self._accent
    @property
    def text_primary(self): return "#000000"
    @property
    def text_secondary(self): return "#333333"
    @property
    def border_color(self): return "#808080"
    @property
    def input_bg(self): return "#ffffff"
    @property
    def input_border(self): return "#7f9db9"
    @property
    def button_bg(self): return "#ece9d8"
    @property
    def button_hover(self): return "#e3dfd2"
    @property
    def button_pressed(self): return "#d4d0c8"
    @property
    def table_header_bg(self): return "#ece9d8"
    @property
    def table_alt_row(self): return "#f5f3ee"
    @property
    def selection_bg(self): return self._accent
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "#ece9d8"
    @property
    def scrollbar_handle(self): return "#c8c4b8"
    @property
    def terminal_bg(self): return "#000000"
    @property
    def terminal_fg(self): return "#c0c0c0"
    @property
    def tooltip_bg(self): return "#ffffe1"
    @property
    def tooltip_fg(self): return "#000000"

    def _xp_button(self, btn_id=""):
        ident = f"#{btn_id}" if btn_id else ""
        bg = self._start_btn if btn_id == "primary" else self.button_bg
        hover = self._start_hover if btn_id == "primary" else self.button_hover
        fg = "#ffffff" if btn_id == "primary" else self.text_primary
        return f"""
QPushButton{ident} {{
    background-color: {bg};
    color: {fg};
    border: 1px solid #808080;
    border-radius: 3px;
    padding: 3px 12px;
    min-height: 20px;
    font-family: "Tahoma";
    font-size: 8pt;
}}
QPushButton{ident}:hover {{
    background-color: {hover};
}}
QPushButton{ident}:pressed {{
    background-color: #c0c0c0;
    border-style: inset;
}}
QPushButton{ident}:disabled {{
    background-color: #d4d0c8;
    color: #606060;
}}
"""

    def _sidebar_style(self):
        return f"""
QFrame#sidebar {{
    background-color: {self._sidebar_bg};
    border: none;
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: {self.sidebar_fg};
    border: none;
    border-left: 3px solid transparent;
    padding: 8px 14px;
    text-align: left;
    font-family: "Tahoma";
    font-size: 9pt;
}}

QPushButton#nav_btn:hover {{
    background-color: rgba(255,255,255,0.1);
    border-left: 3px solid rgba(255,255,255,0.3);
}}

QPushButton#nav_btn:checked {{
    background-color: {self._sidebar_active_bg};
    border-left: 3px solid #ffd700;
    color: #ffffff;
    font-weight: bold;
}}
"""

    def _panel_style(self):
        return f"""
QFrame#panel, QGroupBox {{
    background-color: {self.panel_bg};
    border: 2px solid {self._panel_border};
    border-radius: 0;
    padding: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {self.text_primary};
    font-weight: bold;
    font-family: "Tahoma";
}}
"""

    def _table_style(self):
        return f"""
QTableWidget {{
    background-color: {self.panel_bg};
    alternate-background-color: {self.table_alt_row};
    border: 1px solid {self._panel_border};
    gridline-color: #d4d0c8;
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    font-family: "Tahoma";
    font-size: 8pt;
}}

QTableWidget::item {{
    padding: 2px 6px;
    border: none;
}}

QHeaderView::section {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #ece9d8);
    color: {self.text_primary};
    border: 1px solid #808080;
    padding: 4px 6px;
    font-weight: bold;
    font-size: 8pt;
    font-family: "Tahoma";
}}
"""

    def _input_style(self):
        return f"""
QLineEdit, QSpinBox {{
    background-color: {self.input_bg};
    border: 2px inset #7f9db9;
    padding: 2px 4px;
    min-height: 18px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: {self.text_primary};
}}

QLineEdit:focus, QSpinBox:focus {{
    border-color: {self._accent};
}}

QComboBox {{
    background-color: {self.button_bg};
    border: 1px solid #808080;
    padding: 2px 4px;
    min-height: 18px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: {self.text_primary};
}}

QComboBox::drop-down {{
    border: 1px solid #808080;
    width: 20px;
    background-color: {self.button_bg};
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid #000000;
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: {self.input_bg};
    border: 1px solid #808080;
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    font-family: "Tahoma";
}}
"""

    def _scrollbar_style(self):
        return f"""
QScrollBar:vertical {{
    background-color: {self.scrollbar_bg};
    width: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:vertical {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ece9d8, stop:0.5 #ffffff, stop:1 #ece9d8);
    border: 1px solid #808080;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #d4d0c8;
}}

QScrollBar::add-line:vertical {{
    border: 1px solid #808080;
    background-color: {self.button_bg};
    height: 16px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:vertical {{
    border: 1px solid #808080;
    background-color: {self.button_bg};
    height: 16px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}}

QScrollBar:horizontal {{
    background-color: {self.scrollbar_bg};
    height: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:horizontal {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ece9d8, stop:0.5 #ffffff, stop:1 #ece9d8);
    border: 1px solid #808080;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #d4d0c8;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: 1px solid #808080;
    background-color: {self.button_bg};
    width: 16px;
}}
"""

    def _misc_style(self):
        return f"""
QTabWidget::pane {{
    border: 1px solid #808080;
    background-color: {self.panel_bg};
    top: -1px;
}}

QTabBar::tab {{
    background-color: #d4d0c8;
    border: 1px solid #808080;
    border-bottom: none;
    padding: 4px 12px;
    margin-right: 1px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: {self.text_secondary};
}}

QTabBar::tab:selected {{
    background-color: {self.panel_bg};
    color: {self.text_primary};
    font-weight: bold;
}}

QProgressBar {{
    background-color: #d4d0c8;
    border: 1px solid #808080;
    border-radius: 0;
    text-align: center;
    min-height: 16px;
    font-size: 8pt;
    font-family: "Tahoma";
}}

QProgressBar::chunk {{
    background-color: {self._accent};
}}

QTextBrowser#terminal {{
    background-color: {self.terminal_bg};
    color: {self.terminal_fg};
    border: 2px inset #808080;
    font-family: "Lucida Console", "Consolas", monospace;
    font-size: 9pt;
    padding: 4px;
}}

QCheckBox {{
    spacing: 4px;
    color: {self.text_primary};
    background: transparent;
    font-family: "Tahoma";
}}

QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 1px solid #808080;
    background-color: {self.input_bg};
}}

QCheckBox::indicator:checked {{
    background-color: {self._accent};
    border-color: #000080;
}}

QToolTip {{
    background-color: #ffffe1;
    color: #000000;
    border: 1px solid #000000;
    padding: 2px;
    font-family: "Tahoma";
    font-size: 8pt;
}}

QSplitter::handle {{
    background-color: #808080;
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QStatusBar {{
    background-color: #d4d0c8;
    color: {self.text_primary};
    border-top: 1px solid #808080;
    font-family: "Tahoma";
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: {self.text_primary};
    background: transparent;
}}

QLabel {{
    color: {self.text_primary};
    background: transparent;
    font-family: "Tahoma";
}}

QLabel#subtitle {{
    color: {self.text_secondary};
    font-size: 8pt;
}}

QLabel#title {{
    font-size: 13pt;
    font-weight: bold;
    color: {self.text_primary};
}}
"""

    def generate_qss(self) -> str:
        return (
            f"QMainWindow, QWidget {{ background-color: {self.window_bg}; color: {self.text_primary}; "
            f'font-family: "{self.font_family}"; font-size: {self.font_size}pt; }}'
            + self._sidebar_style()
            + self._xp_button()
            + self._xp_button("primary")
            + self._xp_button("danger")
            + self._panel_style()
            + self._table_style()
            + self._input_style()
            + self._scrollbar_style()
            + self._misc_style()
            + self._dashboard_qss()
        )


class XPLunaBlue(_XPLunaBase):
    name = "xp_luna_blue"
    display_name = "Windows XP Luna (Blue)"
    description = "经典蓝色 Luna 主题"
    _title_start = "#0054e3"
    _title_end = "#4580c4"
    _accent = "#0054e3"
    _start_btn = "#3c8f3c"
    _start_hover = "#4aa04a"
    _panel_border = "#0054e3"
    _sidebar_bg = "#1b3a6b"
    _sidebar_active_bg = "#2b5aab"


class XPLunaSilver(_XPLunaBase):
    name = "xp_luna_silver"
    display_name = "Windows XP Luna (Silver)"
    description = "银色 Luna 主题"
    _title_start = "#6b7bc7"
    _title_end = "#a4b4dc"
    _accent = "#5a6aaa"
    _start_btn = "#3c8f3c"
    _start_hover = "#4aa04a"
    _panel_border = "#6b7bc7"
    _sidebar_bg = "#3a4a7a"
    _sidebar_active_bg = "#5a6aaa"


class XPLunaOlive(_XPLunaBase):
    name = "xp_luna_olive"
    display_name = "Windows XP Luna (Olive)"
    description = "橄榄绿 Luna 主题"
    _title_start = "#6b8c3b"
    _title_end = "#a4c46b"
    _accent = "#6b8c3b"
    _start_btn = "#6b8c3b"
    _start_hover = "#7a9c4a"
    _panel_border = "#6b8c3b"
    _sidebar_bg = "#3a5a1b"
    _sidebar_active_bg = "#5a7a3b"
