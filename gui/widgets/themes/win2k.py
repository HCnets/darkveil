from .engine import ThemeBase


class Win2000Theme(ThemeBase):
    name = "win2000"
    display_name = "Windows 2000"
    description = "经典灰色立体边框，NT 时代风格"
    font_family = "Tahoma"
    font_size = 8

    @property
    def window_bg(self): return "#d4d0c8"
    @property
    def panel_bg(self): return "#ffffff"
    @property
    def sidebar_bg(self): return "#1f3460"
    @property
    def sidebar_fg(self): return "#d4d0c8"
    @property
    def sidebar_active(self): return "#ffffff"
    @property
    def accent(self): return "#1f3460"
    @property
    def text_primary(self): return "#000000"
    @property
    def text_secondary(self): return "#444444"
    @property
    def border_color(self): return "#808080"
    @property
    def input_bg(self): return "#ffffff"
    @property
    def input_border(self): return "#808080"
    @property
    def button_bg(self): return "#d4d0c8"
    @property
    def button_hover(self): return "#c8c4b8"
    @property
    def button_pressed(self): return "#b8b4a8"
    @property
    def table_header_bg(self): return "#d4d0c8"
    @property
    def table_alt_row(self): return "#f0eeea"
    @property
    def selection_bg(self): return "#1f3460"
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "#d4d0c8"
    @property
    def scrollbar_handle(self): return "#c0bcb0"
    @property
    def terminal_bg(self): return "#000000"
    @property
    def terminal_fg(self): return "#c0c0c0"
    @property
    def tooltip_bg(self): return "#ffffe1"
    @property
    def tooltip_fg(self): return "#000000"

    def generate_qss(self) -> str:
        return f"""
QMainWindow, QWidget {{
    background-color: {self.window_bg};
    color: {self.text_primary};
    font-family: "{self.font_family}";
    font-size: {self.font_size}pt;
}}

QFrame#sidebar {{
    background-color: {self.sidebar_bg};
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
    background-color: rgba(255,255,255,0.08);
    border-left: 3px solid rgba(255,255,255,0.2);
}}

QPushButton#nav_btn:checked {{
    background-color: #2b4a80;
    border-left: 3px solid #c0c0c0;
    color: #ffffff;
    font-weight: bold;
}}

QPushButton {{
    background-color: #d4d0c8;
    color: #000000;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 4px 12px;
    min-height: 18px;
    font-family: "Tahoma";
    font-size: 8pt;
}}

QPushButton:hover {{
    background-color: #c8c4b8;
}}

QPushButton:pressed {{
    border-style: inset;
    border-color: #404040;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    padding: 5px 11px 3px 13px;
}}

QPushButton:disabled {{
    color: #808080;
    border-style: outset;
    border-color: #c0c0c0;
}}

QPushButton#primary {{
    background-color: #1f3460;
    color: #ffffff;
    border: 2px outset #4060a0;
}}

QPushButton#primary:hover {{
    background-color: #2b4a80;
}}

QPushButton#primary:pressed {{
    border-style: inset;
}}

QPushButton#danger {{
    background-color: #8b0000;
    color: #ffffff;
    border: 2px outset #c04040;
}}

QFrame#panel, QGroupBox {{
    background-color: {self.panel_bg};
    border: 2px groove #808080;
    padding: 6px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: {self.text_primary};
    font-weight: bold;
    font-family: "Tahoma";
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

QLineEdit, QSpinBox {{
    background-color: #ffffff;
    border: 2px inset #808080;
    padding: 2px 4px;
    min-height: 18px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: #000000;
}}

QLineEdit:focus, QSpinBox:focus {{
    border-color: #1f3460;
}}

QComboBox {{
    background-color: #d4d0c8;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 2px 4px;
    min-height: 18px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: #000000;
}}

QComboBox::drop-down {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    width: 20px;
    background-color: #d4d0c8;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid #000000;
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 2px inset #808080;
    selection-background-color: #1f3460;
    selection-color: #ffffff;
    font-family: "Tahoma";
}}

QTableWidget {{
    background-color: #ffffff;
    alternate-background-color: #f0eeea;
    border: 2px inset #808080;
    gridline-color: #c0c0c0;
    selection-background-color: #1f3460;
    selection-color: #ffffff;
    font-family: "Tahoma";
    font-size: 8pt;
}}

QTableWidget::item {{
    padding: 2px 4px;
}}

QHeaderView::section {{
    background-color: #d4d0c8;
    color: #000000;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 3px 6px;
    font-weight: bold;
    font-size: 8pt;
    font-family: "Tahoma";
}}

QScrollBar:vertical {{
    background-color: #d4d0c8;
    width: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:vertical {{
    background-color: #c0bcb0;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #b0aca0;
}}

QScrollBar::add-line:vertical {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #d4d0c8;
    height: 16px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:vertical {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #d4d0c8;
    height: 16px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}}

QScrollBar:horizontal {{
    background-color: #d4d0c8;
    height: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:horizontal {{
    background-color: #c0bcb0;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #b0aca0;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #d4d0c8;
    width: 16px;
}}

QTabWidget::pane {{
    border: 2px groove #808080;
    background-color: #ffffff;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #d4d0c8;
    border: 2px outset #ffffff;
    border-bottom: none;
    padding: 4px 10px;
    margin-right: 1px;
    font-family: "Tahoma";
    font-size: 8pt;
    color: #444444;
}}

QTabBar::tab:selected {{
    background-color: #ffffff;
    color: #000000;
    font-weight: bold;
    border-bottom: 1px solid #ffffff;
}}

QProgressBar {{
    background-color: #d4d0c8;
    border: 2px inset #808080;
    border-radius: 0;
    text-align: center;
    min-height: 16px;
    font-size: 8pt;
    font-family: "Tahoma";
}}

QProgressBar::chunk {{
    background-color: #1f3460;
}}

QTextBrowser#terminal {{
    background-color: #000000;
    color: #c0c0c0;
    border: 2px inset #808080;
    font-family: "Lucida Console", "Consolas", monospace;
    font-size: 9pt;
    padding: 4px;
}}

QCheckBox {{
    spacing: 4px;
    color: #000000;
    background: transparent;
    font-family: "Tahoma";
}}

QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 2px inset #808080;
    background-color: #ffffff;
}}

QCheckBox::indicator:checked {{
    background-color: #1f3460;
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
    color: #000000;
    border-top: 2px groove #808080;
    font-family: "Tahoma";
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: #000000;
    background: transparent;
}}
""" + self._dashboard_qss()
