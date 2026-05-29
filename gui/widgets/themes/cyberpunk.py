from .engine import ThemeBase

class CyberpunkTheme(ThemeBase):
    name = "cyberpunk"
    display_name = "Cyberpunk"
    description = "深黑底 + 霓虹青/品红发光边框，赛博朋克黑客风"
    font_family = "Cascadia Mono"
    font_size = 9

    @property
    def window_bg(self): return "#0a0a0f"
    @property
    def panel_bg(self): return "#0f0f1a"
    @property
    def sidebar_bg(self): return "#050510"
    @property
    def sidebar_fg(self): return "#00ffcc"
    @property
    def sidebar_active(self): return "#ff00ff"
    @property
    def accent(self): return "#00ffcc"
    @property
    def text_primary(self): return "#e0e0ff"
    @property
    def text_secondary(self): return "#9898c8"
    @property
    def border_color(self): return "#2a2a5a"
    @property
    def input_bg(self): return "#0a0a18"
    @property
    def input_border(self): return "#00ffcc"
    @property
    def button_bg(self): return "#1a1a2e"
    @property
    def button_hover(self): return "#2a2a4e"
    @property
    def button_pressed(self): return "#0f0f20"
    @property
    def table_header_bg(self): return "#0a0a1a"
    @property
    def table_alt_row(self): return "#0f0f1e"
    @property
    def selection_bg(self): return "#ff00ff"
    @property
    def selection_fg(self): return "#ffffff"
    @property
    def scrollbar_bg(self): return "#0a0a14"
    @property
    def scrollbar_handle(self): return "#00ffcc"
    @property
    def terminal_bg(self): return "#000008"
    @property
    def terminal_fg(self): return "#00ffcc"
    @property
    def tooltip_bg(self): return "#1a0a2e"
    @property
    def tooltip_fg(self): return "#ff00ff"
    @property
    def danger(self): return "#ff0040"
    @property
    def success(self): return "#00ff88"
    @property
    def warning(self): return "#ffee00"

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
    border-right: 1px solid {self.accent};
}}

QPushButton#nav_btn {{
    background-color: transparent;
    color: {self.sidebar_fg};
    border: none;
    border-left: 3px solid transparent;
    padding: 10px 16px;
    text-align: left;
    font-size: 10pt;
}}

QPushButton#nav_btn:hover {{
    background-color: rgba(0, 255, 204, 0.06);
    border-left: 3px solid rgba(0, 255, 204, 0.4);
    color: #ffffff;
}}

QPushButton#nav_btn:checked {{
    background-color: rgba(255, 0, 255, 0.08);
    border-left: 3px solid {self.sidebar_active};
    color: {self.sidebar_active};
    font-weight: bold;
}}

QFrame#panel, QGroupBox {{
    background-color: {self.panel_bg};
    border: 1px solid {self.border_color};
    border-radius: 2px;
    padding: 12px;
}}

QFrame#panel:hover, QGroupBox:hover {{
    border-color: {self.accent};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {self.accent};
    font-weight: bold;
}}

QLabel {{
    color: {self.text_primary};
    background: transparent;
}}

QLabel#subtitle {{
    color: {self.text_secondary};
    font-size: 8pt;
}}

QLabel#title {{
    font-size: 16pt;
    font-weight: bold;
    color: {self.accent};
}}

QPushButton {{
    background-color: {self.button_bg};
    color: {self.accent};
    border: 1px solid {self.border_color};
    border-radius: 2px;
    padding: 6px 16px;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {self.button_hover};
    border-color: {self.accent};
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: {self.button_pressed};
}}

QPushButton:disabled {{
    background-color: #0a0a14;
    color: #303050;
    border-color: #151530;
}}

QPushButton#primary {{
    background-color: transparent;
    color: {self.accent};
    border: 1px solid {self.accent};
    font-weight: bold;
}}

QPushButton#primary:hover {{
    background-color: rgba(0, 255, 204, 0.12);
    color: #ffffff;
    border-color: #ffffff;
}}

QPushButton#primary:pressed {{
    background-color: rgba(0, 255, 204, 0.2);
}}

QPushButton#danger {{
    background-color: transparent;
    color: {self.danger};
    border: 1px solid {self.danger};
    font-weight: bold;
}}

QPushButton#danger:hover {{
    background-color: rgba(255, 0, 64, 0.12);
    color: #ffffff;
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: {self.input_bg};
    border: 1px solid {self.border_color};
    border-radius: 2px;
    padding: 5px 8px;
    min-height: 28px;
    color: {self.text_primary};
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {self.accent};
    border-width: 1px;
}}

QComboBox::drop-down {{
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {self.input_bg};
    border: 1px solid {self.accent};
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    outline: none;
}}

QTableWidget {{
    background-color: {self.panel_bg};
    alternate-background-color: {self.table_alt_row};
    border: 1px solid {self.border_color};
    border-radius: 2px;
    gridline-color: #1a1a30;
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    outline: none;
}}

QTableWidget::item {{
    padding: 4px 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: rgba(255, 0, 255, 0.2);
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: {self.table_header_bg};
    color: {self.accent};
    border: none;
    border-bottom: 1px solid {self.border_color};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 8pt;
}}

QTextBrowser#terminal {{
    background-color: {self.terminal_bg};
    color: {self.terminal_fg};
    border: 1px solid {self.border_color};
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(0, 255, 204, 0.25);
}}

QTextEdit#terminal {{
    background-color: {self.terminal_bg};
    color: {self.terminal_fg};
    border: none;
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: rgba(0, 255, 204, 0.25);
}}

QProgressBar {{
    background-color: #0a0a18;
    border: 1px solid {self.border_color};
    border-radius: 2px;
    text-align: center;
    min-height: 18px;
    font-size: 8pt;
    color: {self.text_primary};
}}

QProgressBar::chunk {{
    background-color: {self.accent};
    border-radius: 1px;
}}

QTabWidget::pane {{
    border: 1px solid {self.border_color};
    border-radius: 2px;
    background-color: {self.panel_bg};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {self.window_bg};
    border: 1px solid {self.border_color};
    border-bottom: none;
    border-top-left-radius: 2px;
    border-top-right-radius: 2px;
    padding: 6px 16px;
    margin-right: 2px;
    color: {self.text_secondary};
}}

QTabBar::tab:selected {{
    background-color: {self.panel_bg};
    color: {self.accent};
    font-weight: bold;
    border-color: {self.accent};
}}

QTabBar::tab:hover:!selected {{
    background-color: #0f0f20;
    color: {self.text_primary};
}}

QScrollBar:vertical {{
    background-color: {self.scrollbar_bg};
    width: 12px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {self.scrollbar_handle};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #40ffdd;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {self.scrollbar_bg};
    height: 12px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {self.scrollbar_handle};
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #40ffdd;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QCheckBox {{
    spacing: 6px;
    color: {self.text_primary};
    background: transparent;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {self.border_color};
    border-radius: 2px;
    background-color: {self.input_bg};
}}

QCheckBox::indicator:checked {{
    background-color: {self.accent};
    border-color: {self.accent};
}}

QToolTip {{
    background-color: {self.tooltip_bg};
    color: {self.tooltip_fg};
    border: 1px solid {self.sidebar_active};
    padding: 6px;
    border-radius: 2px;
    font-size: 8pt;
}}

QSplitter::handle {{
    background-color: {self.border_color};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

QStatusBar {{
    background-color: {self.sidebar_bg};
    color: {self.sidebar_fg};
    border-top: 1px solid {self.border_color};
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: {self.sidebar_fg};
    background: transparent;
}}
""" + self._dashboard_qss()
