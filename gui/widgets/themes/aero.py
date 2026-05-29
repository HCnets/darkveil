from .engine import ThemeBase


class AeroTheme(ThemeBase):
    name = "aero"
    display_name = "Windows 7 Aero"
    description = "Vista/7 Aero 玻璃质感：蓝白半透明面板、浅灰内容区、珍珠光泽按钮"
    font_family = "Segoe UI"
    font_size = 9

    @property
    def window_bg(self): return "#f0f0f0"
    @property
    def panel_bg(self): return "#ffffff"
    @property
    def sidebar_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #203048, stop:0.015 #304868, stop:0.03 #1c2c40, stop:0.5 #15223a, stop:1 #0e1830)"
    @property
    def sidebar_fg(self): return "#b0c8e0"
    @property
    def sidebar_active(self): return "#5cb8ff"
    @property
    def accent(self): return "#4a90d0"
    @property
    def text_primary(self): return "#1a1a1a"
    @property
    def text_secondary(self): return "#666666"
    @property
    def border_color(self): return "#b0b8c0"
    @property
    def input_bg(self): return "#ffffff"
    @property
    def input_border(self): return "#7a98b8"
    @property
    def button_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8f0f8, stop:0.04 #ffffff, stop:0.06 #d8e8f4, stop:0.4 #a8c8e0, stop:0.7 #80b0d0, stop:1 #6098c0)"
    @property
    def button_hover(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f0f8ff, stop:0.04 #ffffff, stop:0.06 #e0f0ff, stop:0.4 #b8d8f0, stop:0.7 #90c0e0, stop:1 #70a8d0)"
    @property
    def button_pressed(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5888b0, stop:0.3 #6898c0, stop:0.7 #78a8d0, stop:1 #88b8e0)"
    @property
    def table_header_bg(self): return "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8f0f8, stop:0.03 #f8fcff, stop:0.06 #d8e8f4, stop:1 #c0d4e8)"
    @property
    def table_alt_row(self): return "#f4f8fc"
    @property
    def selection_bg(self): return "#3399ff"
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "#f0f0f0"
    @property
    def scrollbar_handle(self): return "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #c0d0e0, stop:0.2 #d8e4f0, stop:0.22 #e8f0f8, stop:0.5 #d0dce8, stop:1 #b8c8d8)"
    @property
    def terminal_bg(self): return "#0c1420"
    @property
    def terminal_fg(self): return "#a0c8e8"
    @property
    def tooltip_bg(self): return "#ffffe1"
    @property
    def tooltip_fg(self): return "#000000"
    @property
    def danger(self): return "#c04040"
    @property
    def success(self): return "#40a050"
    @property
    def warning(self): return "#e09020"

    def generate_qss(self) -> str:
        return f"""
QMainWindow, QWidget {{
    background-color: #f0f0f0;
    color: #1a1a1a;
    font-family: "{self.font_family}";
    font-size: {self.font_size}pt;
}}

/* ================================================================
   SIDEBAR — 模拟 Win7 任务栏
   近黑色 + 微弱蓝调玻璃 + 顶部高光条
   ================================================================ */
QFrame#sidebar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1c2c40,
        stop:0.015 #304868,
        stop:0.03 #1c2c40,
        stop:0.5 #15223a,
        stop:1 #0e1830);
    border-right: 1px solid #1a2840;
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: #8aa0b8;
    border: none;
    border-left: 3px solid transparent;
    padding: 9px 16px;
    text-align: left;
    font-size: 10pt;
}}

QPushButton#nav_btn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(80,170,255,0.20), stop:0.4 rgba(80,170,255,0.08), stop:1 transparent);
    border-left: 3px solid rgba(80,170,255,0.6);
    color: #d0e4ff;
}}

QPushButton#nav_btn:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(80,170,255,0.35), stop:0.3 rgba(80,170,255,0.15), stop:1 transparent);
    border-left: 3px solid #5cb8ff;
    color: #ffffff;
    font-weight: bold;
}}

/* ================================================================
   PANELS — 白色内容区 + 浅蓝边框
   Win7 窗口内容区是白色的，不是深蓝色
   ================================================================ */
QFrame#panel, QGroupBox {{
    background-color: #ffffff;
    border: 1px solid #8898a8;
    border-radius: 4px;
    padding: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2a5a88;
    font-weight: bold;
}}

QLabel {{
    color: #1a1a1a;
    background: transparent;
}}

QLabel#subtitle {{
    color: #666666;
    font-size: 8pt;
}}

QLabel#title {{
    font-size: 16pt;
    font-weight: bold;
    color: #1a1a1a;
}}

/* ================================================================
   PEARL BUTTONS — Win7 标志性珍珠光泽
   浅色底 + 顶部极细白高光条 + 蓝色渐变到深蓝底部
   ================================================================ */
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e0ecf8,
        stop:0.04 #f8fcff,
        stop:0.08 #d0e0f0,
        stop:0.4 #a0c4dc,
        stop:0.7 #78a8cc,
        stop:1 #5888b0);
    color: #0a1828;
    border: 1px solid #6888a8;
    border-top: 1px solid #a0c0e0;
    border-radius: 4px;
    padding: 5px 16px;
    min-height: 20px;
    font-weight: 500;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8f4ff,
        stop:0.04 #ffffff,
        stop:0.08 #d8ecff,
        stop:0.4 #b0d4f0,
        stop:0.7 #88b8dc,
        stop:1 #6898c0);
    border: 1px solid #7898b8;
    border-top: 1px solid #b8d4f0;
    color: #000000;
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #4a7898,
        stop:0.3 #5888a8,
        stop:0.7 #6898b8,
        stop:1 #78a8c8);
    border: 1px solid #3a6888;
    border-top: 1px solid #4a7898;
    color: #ffffff;
    padding-top: 6px;
}}

QPushButton:disabled {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8e8e8, stop:0.04 #f0f0f0, stop:1 #d0d0d0);
    color: #888888;
    border: 1px solid #b0b0b0;
    border-top: 1px solid #d0d0d0;
}}

QPushButton#primary {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #b8dcff,
        stop:0.04 #e0f0ff,
        stop:0.08 #90c8f0,
        stop:0.4 #4aa0e0,
        stop:0.7 #2880c8,
        stop:1 #1060a8);
    color: #ffffff;
    border: 1px solid #1060a8;
    border-top: 1px solid #90c8f0;
    font-weight: bold;
    border-radius: 5px;
}}

QPushButton#primary:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #c8e8ff,
        stop:0.04 #f0f8ff,
        stop:0.08 #a0d8ff,
        stop:0.4 #5ab0f0,
        stop:0.7 #3890d8,
        stop:1 #2070b8);
    border-top: 1px solid #a0d8ff;
}}

QPushButton#primary:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #1060a8, stop:0.3 #2070b8, stop:0.7 #3080c8, stop:1 #4090d8);
    border-top: 1px solid #0850a0;
    color: #d0e8ff;
}}

QPushButton#danger {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f8c0c0,
        stop:0.04 #ffe8e8,
        stop:0.08 #f0a0a0,
        stop:0.4 #d86060,
        stop:0.7 #c04040,
        stop:1 #a02020);
    color: #ffffff;
    border: 1px solid #a02020;
    border-top: 1px solid #f0a0a0;
    font-weight: bold;
    border-radius: 5px;
}}

QPushButton#danger:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffd0d0,
        stop:0.04 #fff0f0,
        stop:0.08 #f8b0b0,
        stop:0.4 #e87070,
        stop:0.7 #d05050,
        stop:1 #b03030);
    border-top: 1px solid #f8b0b0;
}}

/* ================================================================
   INPUTS — 白底 + 蓝色边框 + 蓝光聚焦
   ================================================================ */
QLineEdit, QSpinBox, QComboBox {{
    background-color: #ffffff;
    border: 1px solid #7a98b8;
    border-radius: 3px;
    padding: 5px 8px;
    min-height: 20px;
    color: #1a1a1a;
    selection-background-color: #3399ff;
    selection-color: #ffffff;
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid #4a90d0;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #4a6880;
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    border: 1px solid #8898a8;
    selection-background-color: #3399ff;
    selection-color: #ffffff;
    outline: none;
}}

/* ================================================================
   TABLE — 白底 + 浅蓝玻璃表头
   ================================================================ */
QTableWidget {{
    background-color: #ffffff;
    alternate-background-color: #f4f8fc;
    border: 1px solid #b0b8c0;
    border-radius: 4px;
    gridline-color: #e0e4e8;
    selection-background-color: #3399ff;
    selection-color: #ffffff;
    outline: none;
}}

QTableWidget::item {{
    padding: 4px 8px;
    border: none;
}}

QHeaderView::section {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8f0f8,
        stop:0.03 #f8fcff,
        stop:0.06 #d8e8f4,
        stop:1 #c0d4e8);
    color: #2a4a68;
    border: none;
    border-bottom: 1px solid #a0b0c0;
    border-right: 1px solid #d0d8e0;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 8pt;
}}

/* ================================================================
   TERMINAL — 保持深色（cmd.exe 风格）
   ================================================================ */
QTextEdit#terminal {{
    background-color: #0c1420;
    color: #a0c8e8;
    border: 1px solid #8898a8;
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(51,153,255,0.3);
}}

QTextBrowser#terminal {{
    background-color: #0c1420;
    color: #a0c8e8;
    border: 1px solid #8898a8;
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(51,153,255,0.3);
}}

/* ================================================================
   PROGRESS BAR
   ================================================================ */
QProgressBar {{
    background-color: #e8e8e8;
    border: 1px solid #b0b8c0;
    border-radius: 4px;
    text-align: center;
    min-height: 18px;
    font-size: 8pt;
    color: #333333;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #2a80d0, stop:0.3 #4aa0f0, stop:0.32 #80c8ff,
        stop:0.5 #4aa0f0, stop:0.52 #80c8ff, stop:1 #4aa0f0);
    border-radius: 3px;
}}

/* ================================================================
   TABS
   ================================================================ */
QTabWidget::pane {{
    border: 1px solid #8898a8;
    border-radius: 4px;
    background-color: #ffffff;
    top: -1px;
}}

QTabBar::tab {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e0e8f0, stop:0.04 #f0f4f8, stop:0.06 #d0dce8, stop:1 #c0ccd8);
    border: 1px solid #8898a8;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 16px;
    margin-right: 2px;
    color: #4a6880;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #4a90d0,
        stop:0.02 #6ab0e8,
        stop:0.04 #3a80c0,
        stop:0.15 #2a6aa0,
        stop:1 #1a5080);
    color: #ffffff;
    font-weight: bold;
    border-top: 1px solid #6ab0e8;
    border-color: #1a5080;
}}

QTabBar::tab:hover:!selected {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8f0f8, stop:0.04 #f8fcff, stop:1 #d8e4f0);
    color: #2a5a88;
}}

/* ================================================================
   SCROLLBAR — 玻璃光泽
   ================================================================ */
QScrollBar:vertical {{
    background-color: #f0f0f0;
    width: 14px;
    border: 1px solid #c0c8d0;
    border-radius: 7px;
}}

QScrollBar::handle:vertical {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #b0c0d0,
        stop:0.15 #c8d8e8,
        stop:0.18 #e0ecf8,
        stop:0.5 #c0d0e0,
        stop:0.85 #a0b0c0);
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #90a8c0,
        stop:0.15 #b0c8e0,
        stop:0.18 #d0e4f8,
        stop:0.5 #a8c0d8,
        stop:0.85 #8098b0);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: #f0f0f0;
    height: 14px;
    border: 1px solid #c0c8d0;
    border-radius: 7px;
}}

QScrollBar::handle:horizontal {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #b0c0d0,
        stop:0.15 #c8d8e8,
        stop:0.18 #e0ecf8,
        stop:0.5 #c0d0e0,
        stop:0.85 #a0b0c0);
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #90a8c0,
        stop:0.15 #b0c8e0,
        stop:0.18 #d0e4f8,
        stop:0.5 #a8c0d8,
        stop:0.85 #8098b0);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ================================================================
   CHECKBOX
   ================================================================ */
QCheckBox {{
    spacing: 6px;
    color: #1a1a1a;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #7a98b8;
    border-radius: 3px;
    background-color: #ffffff;
}}

QCheckBox::indicator:checked {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #60b8ff, stop:0.3 #3a9cff, stop:1 #1a70d0);
    border-color: #3a9cff;
}}

/* ================================================================
   TOOLTIP
   ================================================================ */
QToolTip {{
    background-color: #ffffe1;
    color: #000000;
    border: 1px solid #000000;
    padding: 6px;
    border-radius: 4px;
    font-size: 8pt;
}}

QSplitter::handle {{
    background-color: #c0c8d0;
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QStatusBar {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #182838, stop:0.015 #243848, stop:1 #0e1828);
    color: #80a0c0;
    border-top: 1px solid #2a4058;
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: #80a0c0;
    background: transparent;
}}
""" + self._dashboard_qss()
