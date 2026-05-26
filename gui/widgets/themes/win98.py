from .engine import ThemeBase


class Win98Theme(ThemeBase):
    name = "win98"
    display_name = "Windows 98"
    description = "经典灰色像素风，复古 3D 边框"
    font_family = "MS Sans Serif"
    font_size = 8

    @property
    def window_bg(self): return "#c0c0c0"
    @property
    def panel_bg(self): return "#ffffff"
    @property
    def sidebar_bg(self): return "#000080"
    @property
    def sidebar_fg(self): return "#ffffff"
    @property
    def sidebar_active(self): return "#ffff00"
    @property
    def accent(self): return "#000080"
    @property
    def text_primary(self): return "#000000"
    @property
    def text_secondary(self): return "#404040"
    @property
    def border_color(self): return "#808080"
    @property
    def input_bg(self): return "#ffffff"
    @property
    def input_border(self): return "#808080"
    @property
    def button_bg(self): return "#c0c0c0"
    @property
    def button_hover(self): return "#b0b0b0"
    @property
    def button_pressed(self): return "#a0a0a0"
    @property
    def table_header_bg(self): return "#c0c0c0"
    @property
    def table_alt_row(self): return "#f0f0f0"
    @property
    def selection_bg(self): return "#000080"
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "#c0c0c0"
    @property
    def scrollbar_handle(self): return "#a0a0a0"
    @property
    def terminal_bg(self): return "#000000"
    @property
    def terminal_fg(self): return "#00ff00"
    @property
    def tooltip_bg(self): return "#ffffe1"
    @property
    def tooltip_fg(self): return "#000000"

    def generate_qss(self) -> str:
        return f"""
QMainWindow, QWidget {{
    background-color: #c0c0c0;
    color: #000000;
    font-family: "{self.font_family}";
    font-size: {self.font_size}pt;
}}

QFrame#sidebar {{
    background-color: #000080;
    border: none;
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: #ffffff;
    border: none;
    padding: 7px 12px;
    text-align: left;
    font-size: 9pt;
}}

QPushButton#nav_btn:hover {{
    background-color: rgba(255,255,255,0.1);
}}

QPushButton#nav_btn:checked {{
    background-color: #0000c0;
    color: #ffff00;
    font-weight: bold;
    border: 1px dashed #ffff00;
}}

QPushButton {{
    background-color: #c0c0c0;
    color: #000000;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 3px 10px;
    min-height: 18px;
    font-size: 8pt;
}}

QPushButton:hover {{
    background-color: #b4b4b4;
}}

QPushButton:pressed {{
    border-style: inset;
    border-color: #404040;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    padding: 4px 9px 2px 11px;
}}

QPushButton:disabled {{
    color: #808080;
    border-color: #c0c0c0;
}}

QPushButton#primary {{
    background-color: #000080;
    color: #ffffff;
    border: 2px outset #4040c0;
}}

QPushButton#primary:hover {{
    background-color: #0000a0;
}}

QPushButton#primary:pressed {{
    border-style: inset;
    border-color: #000040;
}}

QPushButton#danger {{
    background-color: #800000;
    color: #ffffff;
    border: 2px outset #c04040;
}}

QPushButton#danger:pressed {{
    border-style: inset;
    border-color: #400000;
}}

QFrame#panel, QGroupBox {{
    background-color: #ffffff;
    border: 2px groove #808080;
    padding: 4px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 6px;
    padding: 0 3px;
    color: #000000;
    font-weight: bold;
}}

QLabel {{
    color: #000000;
    background: transparent;
}}

QLabel#subtitle {{
    color: #404040;
    font-size: 8pt;
}}

QLabel#title {{
    font-size: 12pt;
    font-weight: bold;
    color: #000000;
}}

QLineEdit, QSpinBox {{
    background-color: #ffffff;
    border: 2px inset #808080;
    padding: 2px 4px;
    min-height: 18px;
    font-size: 8pt;
    color: #000000;
}}

QLineEdit:focus, QSpinBox:focus {{
    border-color: #000080;
}}

QComboBox {{
    background-color: #c0c0c0;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 2px 4px;
    min-height: 18px;
    font-size: 8pt;
    color: #000000;
}}

QComboBox::drop-down {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    width: 18px;
    background-color: #c0c0c0;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 3px solid #000000;
    margin-right: 4px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 2px inset #808080;
    selection-background-color: #000080;
    selection-color: #ffffff;
}}

QTableWidget {{
    background-color: #ffffff;
    alternate-background-color: #f0f0f0;
    border: 2px inset #808080;
    gridline-color: #c0c0c0;
    selection-background-color: #000080;
    selection-color: #ffffff;
    font-size: 8pt;
}}

QTableWidget::item {{
    padding: 1px 4px;
}}

QHeaderView::section {{
    background-color: #c0c0c0;
    color: #000000;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    padding: 2px 6px;
    font-weight: bold;
    font-size: 8pt;
}}

QScrollBar:vertical {{
    background-color: #c0c0c0;
    width: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:vertical {{
    background-color: #c0c0c0;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #b0b0b0;
}}

QScrollBar::add-line:vertical {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #c0c0c0;
    height: 16px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:vertical {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #c0c0c0;
    height: 16px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}}

QScrollBar:horizontal {{
    background-color: #c0c0c0;
    height: 16px;
    border: 1px solid #808080;
}}

QScrollBar::handle:horizontal {{
    background-color: #c0c0c0;
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #b0b0b0;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: 2px outset #ffffff;
    border-right-color: #404040;
    border-bottom-color: #404040;
    background-color: #c0c0c0;
    width: 16px;
}}

QTabWidget::pane {{
    border: 2px groove #808080;
    background-color: #ffffff;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #c0c0c0;
    border: 2px outset #ffffff;
    border-bottom: none;
    padding: 3px 8px;
    margin-right: 1px;
    font-size: 8pt;
    color: #404040;
}}

QTabBar::tab:selected {{
    background-color: #ffffff;
    color: #000000;
    font-weight: bold;
    border-bottom: 1px solid #ffffff;
}}

QProgressBar {{
    background-color: #c0c0c0;
    border: 2px inset #808080;
    text-align: center;
    min-height: 14px;
    font-size: 8pt;
}}

QProgressBar::chunk {{
    background-color: #000080;
}}

QTextBrowser#terminal {{
    background-color: #000000;
    color: #00ff00;
    border: 2px inset #808080;
    font-family: "Fixedsys", "Courier New", monospace;
    font-size: 10pt;
    padding: 4px;
}}

QCheckBox {{
    spacing: 4px;
    color: #000000;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 13px;
    height: 13px;
    border: 2px inset #808080;
    background-color: #ffffff;
}}

QCheckBox::indicator:checked {{
    background-color: #000080;
    border-color: #000040;
}}

QToolTip {{
    background-color: #ffffe1;
    color: #000000;
    border: 1px solid #000000;
    padding: 2px;
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
    background-color: #c0c0c0;
    color: #000000;
    border-top: 2px groove #808080;
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: #000000;
    background: transparent;
}}
""" + self._dashboard_qss()
