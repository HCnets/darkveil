from .engine import ThemeBase


class ModernTheme(ThemeBase):
    name = "modern"
    display_name = "Modern (Windows 10/11)"
    description = "干净的现代 Windows 工具风格"
    font_family = "Segoe UI"
    font_size = 9

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
    padding: 10px 16px;
    text-align: left;
    font-size: 10pt;
    border-radius: 0;
}}

QPushButton#nav_btn:hover {{
    background-color: rgba(255,255,255,0.08);
    border-left: 3px solid rgba(255,255,255,0.3);
}}

QPushButton#nav_btn:checked {{
    background-color: rgba(255,255,255,0.12);
    border-left: 3px solid {self.sidebar_active};
    color: #ffffff;
    font-weight: bold;
}}

QFrame#panel, QGroupBox {{
    background-color: {self.panel_bg};
    border: 1px solid {self.border_color};
    border-radius: 6px;
    padding: 12px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {self.text_primary};
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
    color: {self.text_primary};
}}

QPushButton {{
    background-color: {self.button_bg};
    color: {self.text_primary};
    border: 1px solid {self.input_border};
    border-radius: 4px;
    padding: 6px 16px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {self.button_hover};
    border-color: {self.accent};
}}

QPushButton:pressed {{
    background-color: {self.button_pressed};
}}

QPushButton:disabled {{
    background-color: #f0f0f0;
    color: #a0a0a0;
    border-color: #e0e0e0;
}}

QPushButton#primary {{
    background-color: {self.accent};
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton#primary:hover {{
    background-color: #1a6fc4;
}}

QPushButton#primary:pressed {{
    background-color: #005a9e;
}}

QPushButton#danger {{
    background-color: {self.danger};
    color: white;
    border: none;
    font-weight: bold;
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: {self.input_bg};
    border: 1px solid {self.input_border};
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 20px;
    color: {self.text_primary};
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {self.accent};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {self.text_secondary};
    margin-right: 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {self.input_bg};
    border: 1px solid {self.border_color};
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    outline: none;
}}

QTableWidget {{
    background-color: {self.panel_bg};
    alternate-background-color: {self.table_alt_row};
    border: 1px solid {self.border_color};
    border-radius: 4px;
    gridline-color: #eeeeee;
    selection-background-color: {self.selection_bg};
    selection-color: {self.selection_fg};
    outline: none;
}}

QTableWidget::item {{
    padding: 4px 8px;
    border: none;
}}

QHeaderView::section {{
    background-color: {self.table_header_bg};
    color: {self.text_primary};
    border: none;
    border-bottom: 1px solid {self.border_color};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 8pt;
}}

QTextBrowser#terminal {{
    background-color: {self.terminal_bg};
    color: {self.terminal_fg};
    border: none;
    border-radius: 0;
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: #264f78;
}}

QProgressBar {{
    background-color: #e8e8e8;
    border: 1px solid {self.border_color};
    border-radius: 4px;
    text-align: center;
    min-height: 18px;
    font-size: 8pt;
}}

QProgressBar::chunk {{
    background-color: {self.accent};
    border-radius: 3px;
}}

QTabWidget::pane {{
    border: 1px solid {self.border_color};
    border-radius: 4px;
    background-color: {self.panel_bg};
    top: -1px;
}}

QTabBar::tab {{
    background-color: #e8e8e8;
    border: 1px solid {self.border_color};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 16px;
    margin-right: 2px;
    color: {self.text_secondary};
}}

QTabBar::tab:selected {{
    background-color: {self.panel_bg};
    color: {self.text_primary};
    font-weight: bold;
}}

QTabBar::tab:hover:!selected {{
    background-color: #f0f0f0;
}}

QScrollBar:vertical {{
    background-color: {self.scrollbar_bg};
    width: 10px;
    border: none;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {self.scrollbar_handle};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #a0a0a0;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {self.scrollbar_bg};
    height: 10px;
    border: none;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {self.scrollbar_handle};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #a0a0a0;
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
    border: 1px solid {self.input_border};
    border-radius: 3px;
    background-color: {self.input_bg};
}}

QCheckBox::indicator:checked {{
    background-color: {self.accent};
    border-color: {self.accent};
}}

QToolTip {{
    background-color: {self.tooltip_bg};
    color: {self.tooltip_fg};
    border: none;
    padding: 6px;
    border-radius: 4px;
    font-size: 8pt;
}}

QSplitter::handle {{
    background-color: {self.border_color};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QStatusBar {{
    background-color: {self.sidebar_bg};
    color: {self.sidebar_fg};
    border: none;
    font-size: 8pt;
}}

QStatusBar QLabel {{
    color: {self.sidebar_fg};
    background: transparent;
}}
""" + self._dashboard_qss()
