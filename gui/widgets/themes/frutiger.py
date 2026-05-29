from .engine import ThemeBase


class FrutigerAeroTheme(ThemeBase):
    name = "frutiger"
    display_name = "Frutiger Aero"
    description = "2000s 天蓝渐变 + 光泽气泡 + 磨砂玻璃，Wii/Vista 壁纸风"
    font_family = "Segoe UI"
    font_size = 9

    @property
    def window_bg(self): return "qlineargradient(x1:0,y1:0,x2:0.3,y2:1, stop:0 #5ac8fa, stop:0.3 #4ab8e8, stop:0.6 #88d4f0, stop:1 #c0e8f8)"
    @property
    def panel_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(255,255,255,0.92), stop:0.5 rgba(240,248,255,0.88), stop:1 rgba(220,240,255,0.85))"
    @property
    def sidebar_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #1a8acc, stop:0.15 #2196d8, stop:0.5 #1a7abb, stop:0.85 #0d5a9a, stop:1 #094a80)"
    @property
    def sidebar_fg(self): return "#e8f4ff"
    @property
    def sidebar_active(self): return "#ffffff"
    @property
    def accent(self): return "#0090d0"
    @property
    def text_primary(self): return "#1a3a5a"
    @property
    def text_secondary(self): return "#3a6a8a"
    @property
    def border_color(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #90c8e8, stop:1 #60a0d0)"
    @property
    def input_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:1 #e8f0f8)"
    @property
    def input_border(self): return "#80b8e0"
    @property
    def button_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:0.08 #e8f4ff, stop:0.5 #a8d4f0, stop:1 #60a8d8)"
    @property
    def button_hover(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:0.08 #f0f8ff, stop:0.5 #b8e0f8, stop:1 #70b8e8)"
    @property
    def button_pressed(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5098c8, stop:0.5 #4088b8, stop:1 #60a0d0)"
    @property
    def table_header_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e0f0ff, stop:0.5 #c8e4f8, stop:1 #b0d4f0)"
    @property
    def table_alt_row(self): return "rgba(220,240,255,0.5)"
    @property
    def selection_bg(self): return "#0090d0"
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "rgba(200,230,250,0.5)"
    @property
    def scrollbar_handle(self): return "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #80c0e8, stop:0.3 #a0d8f8, stop:0.32 #b0e0ff, stop:0.7 #90c8f0, stop:1 #70b0e0)"
    @property
    def terminal_bg(self): return "#0a1a2a"
    @property
    def terminal_fg(self): return "#80d0ff"
    @property
    def tooltip_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8f4ff, stop:1 #c0e0f8)"
    @property
    def tooltip_fg(self): return "#1a4a70"
    @property
    def danger(self): return "#e04040"
    @property
    def success(self): return "#30a050"
    @property
    def warning(self): return "#f0a020"

    def generate_qss(self) -> str:
        return f"""
QMainWindow, QWidget {{
    background: qlineargradient(x1:0,y1:0,x2:0.3,y2:1,
        stop:0 #5ac8fa, stop:0.3 #4ab8e8, stop:0.6 #88d4f0, stop:1 #c0e8f8);
    color: #1a3a5a;
    font-family: "{self.font_family}";
    font-size: {self.font_size}pt;
}}

/* === Frutiger Sidebar - Glossy Blue Pill Bar === */
QFrame#sidebar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1a8acc, stop:0.08 #30a8e8, stop:0.1 #30a8e8, stop:0.12 #2196d8,
        stop:0.5 #1a7abb, stop:0.85 #0d5a9a, stop:1 #094a80);
    border-right: 1px solid #0d6ab0;
}}

QPushButton#nav_btn {{
    background: transparent;
    color: #d0eaff;
    border: none;
    border-left: 3px solid transparent;
    padding: 9px 16px;
    text-align: left;
    font-size: 10pt;
}}

QPushButton#nav_btn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(255,255,255,0.2), stop:0.5 rgba(255,255,255,0.08), stop:1 transparent);
    border-left: 3px solid rgba(255,255,255,0.5);
    color: #ffffff;
}}

QPushButton#nav_btn:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(255,255,255,0.3), stop:0.3 rgba(255,255,255,0.15), stop:1 transparent);
    border-left: 3px solid #ffffff;
    color: #ffffff;
    font-weight: bold;
}}

/* === Frutiger Panels - Frosted Glass === */
QFrame#panel, QGroupBox {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(255,255,255,0.92), stop:0.03 rgba(248,252,255,0.90),
        stop:0.5 rgba(240,248,255,0.88), stop:1 rgba(220,240,255,0.85));
    border: 1px solid #90c8e8;
    border-top-color: #b0e0ff;
    border-radius: 10px;
    padding: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #0070b0;
    font-weight: bold;
}}

QLabel {{
    color: #1a3a5a;
    background: transparent;
}}

QLabel#subtitle {{
    color: #5a8aaa;
    font-size: 8pt;
}}

QLabel#title {{
    font-size: 16pt;
    font-weight: bold;
    color: #0060a0;
}}

/* === Frutiger Buttons - Glossy Bubble Pill === */
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:0.08 #f0f8ff, stop:0.1 #ffffff66,
        stop:0.5 #a8d4f0, stop:1 #60a8d8);
    color: #0a3050;
    border: 1px solid #70b8e0;
    border-top-color: #c0e8ff;
    border-radius: 8px;
    padding: 6px 18px;
    min-height: 28px;
    font-weight: 500;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:0.08 #f8fbff, stop:0.1 #ffffff88,
        stop:0.5 #b8e0f8, stop:1 #70b8e8);
    border-color: #80c8f0;
    border-top-color: #d0f0ff;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #5098c8, stop:0.5 #4088b8, stop:1 #60a0d0);
    border-color: #4080b0;
    border-top-color: #5098c8;
    color: #ffffff;
}}

QPushButton:disabled {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e0e8f0, stop:1 #c0d0e0);
    color: #5a6a7a;
    border-color: #b0c0d0;
}}

QPushButton#primary {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #60c8ff, stop:0.08 #ffffff55, stop:0.1 #40b0f0,
        stop:0.5 #2090d0, stop:1 #1070b0);
    color: #ffffff;
    border: 1px solid #1070b0;
    border-top-color: #80d8ff;
    font-weight: bold;
    border-radius: 10px;
}}

QPushButton#primary:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #80d8ff, stop:0.08 #ffffff77, stop:0.1 #50c0ff,
        stop:0.5 #30a0e0, stop:1 #2080c0);
    border-top-color: #a0e8ff;
}}

QPushButton#primary:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1070b0, stop:0.5 #2080c0, stop:1 #30a0e0);
    border-top-color: #1060a0;
}}

QPushButton#danger {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ff8080, stop:0.08 #ffffff44, stop:0.1 #ff6060,
        stop:0.5 #e04040, stop:1 #c02020);
    color: #ffffff;
    border: 1px solid #c02020;
    border-top-color: #ffa0a0;
    font-weight: bold;
    border-radius: 10px;
}}

QPushButton#danger:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ff9090, stop:0.08 #ffffff55, stop:0.1 #ff7070,
        stop:0.5 #f05050, stop:1 #d03030);
}}

/* === Frutiger Inputs - Soft Inset === */
QLineEdit, QSpinBox, QComboBox {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f0f8ff, stop:0.5 #ffffff, stop:1 #e8f0f8);
    border: 1px solid #80b8e0;
    border-top-color: #6098c0;
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 28px;
    color: #1a3a5a;
    selection-background-color: #0090d0;
    selection-color: #ffffff;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: #0090d0;
    border-top-color: #40b8f0;
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #0070b0;
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 1px solid #80b8e0;
    border-radius: 6px;
    selection-background-color: #0090d0;
    selection-color: #ffffff;
    outline: none;
}}

/* === Frutiger Table === */
QTableWidget {{
    background-color: rgba(255,255,255,0.9);
    alternate-background-color: rgba(220,240,255,0.5);
    border: 1px solid #90c8e8;
    border-radius: 8px;
    gridline-color: #c0e0f0;
    selection-background-color: #0090d0;
    selection-color: #ffffff;
    outline: none;
}}

QTableWidget::item {{
    padding: 4px 8px;
    border: none;
}}

QHeaderView::section {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e0f0ff, stop:0.5 #c8e4f8, stop:1 #b0d4f0);
    color: #0060a0;
    border: none;
    border-bottom: 2px solid #90c8e8;
    border-right: 1px solid #c0e0f0;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 8pt;
}}

/* === Frutiger Terminal === */
QTextEdit#terminal {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0a1a2a, stop:1 #061018);
    color: #70c8ff;
    border: 1px solid #3080b0;
    border-radius: 8px;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(0,144,208,0.3);
}}

QTextBrowser#terminal {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0a1a2a, stop:1 #061018);
    color: #70c8ff;
    border: 1px solid #3080b0;
    border-radius: 8px;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(0,144,208,0.3);
}}

/* === Frutiger Progress Bar === */
QProgressBar {{
    background-color: #e0f0ff;
    border: 1px solid #80b8e0;
    border-radius: 8px;
    text-align: center;
    min-height: 20px;
    font-size: 8pt;
    color: #0060a0;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0090d0, stop:0.4 #40b8f0, stop:0.42 #80d8ff,
        stop:0.6 #80d8ff, stop:0.62 #40b8f0, stop:1 #0090d0);
    border-radius: 7px;
    margin: 1px;
}}

/* === Frutiger Tabs === */
QTabWidget::pane {{
    border: 1px solid #90c8e8;
    border-top-color: #b0e0ff;
    border-radius: 8px;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 rgba(255,255,255,0.92), stop:1 rgba(230,245,255,0.88));
    top: -1px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #d0e8f8, stop:0.5 #b0d4f0, stop:1 #90c0e0);
    border: 1px solid #80b8e0;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 6px 16px;
    margin-right: 3px;
    color: #2a6090;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:0.08 #f0f8ff, stop:0.1 #ffffff55,
        stop:1 #e0f0ff);
    color: #0060a0;
    font-weight: bold;
    border-bottom: 2px solid #ffffff;
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e0f0ff, stop:1 #c0e0f8);
    color: #0070b0;
}}

/* === Frutiger Scrollbar === */
QScrollBar:vertical {{
    background-color: rgba(200,230,250,0.4);
    width: 12px;
    border: 1px solid #b0d8f0;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #80c0e8, stop:0.3 #a0d8f8, stop:0.32 #c0e8ff,
        stop:0.7 #a0d8f8, stop:1 #80c0e8);
    border-radius: 5px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #60a8d8, stop:0.3 #80c8f0, stop:0.32 #a0e0ff,
        stop:0.7 #80c8f0, stop:1 #60a8d8);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: rgba(200,230,250,0.4);
    height: 12px;
    border: 1px solid #b0d8f0;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #80c0e8, stop:0.3 #a0d8f8, stop:0.32 #c0e8ff,
        stop:0.7 #a0d8f8, stop:1 #80c0e8);
    border-radius: 5px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #60a8d8, stop:0.3 #80c8f0, stop:0.32 #a0e0ff,
        stop:0.7 #80c8f0, stop:1 #60a8d8);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === Frutiger Checkbox === */
QCheckBox {{
    spacing: 6px;
    color: #1a3a5a;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid #80b8e0;
    border-radius: 5px;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:1 #e8f0f8);
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #60c8ff, stop:0.5 #0090d0, stop:1 #0070b0);
    border-color: #0090d0;
}}

/* === Frutiger Tooltip === */
QToolTip {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8f4ff, stop:1 #c0e0f8);
    color: #1a4a70;
    border: 1px solid #80b8e0;
    padding: 8px;
    border-radius: 8px;
    font-size: 8pt;
}}

QSplitter::handle {{
    background-color: #80b8e0;
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QStatusBar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1a8acc, stop:0.5 #1570b0, stop:1 #0d5a9a);
    color: #d0eaff;
    border-top: 1px solid #40a0e0;
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: #d0eaff;
    background: transparent;
}}
""" + self._dashboard_qss()
