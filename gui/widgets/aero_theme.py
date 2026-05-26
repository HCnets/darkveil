from PyQt6.QtGui import QColor, QPalette

C = {
    "bg": "#f5f5f5",
    "bg_dark": "#2b2b2b",
    "bg_panel": "#ffffff",
    "bg_input": "#ffffff",
    "bg_sidebar": "#2f2f2f",
    "bg_sidebar_hover": "#3a3a3a",
    "bg_sidebar_active": "#404040",
    "bg_header": "#e8e8e8",
    "bg_table_alt": "#f9f9f9",
    "bg_code": "#1e1e1e",

    "border": "#d0d0d0",
    "border_dark": "#555555",
    "border_focus": "#0078d4",

    "accent": "#0078d4",
    "accent_hover": "#1a8ae8",
    "accent_text": "#ffffff",

    "green": "#2e7d32",
    "yellow": "#f57f17",
    "orange": "#e65100",
    "red": "#c62828",

    "text": "#1a1a1a",
    "text_secondary": "#666666",
    "text_light": "#ffffff",
    "text_muted": "#999999",
    "text_sidebar": "#cccccc",
}


def get_stylesheet():
    return f"""
    QWidget {{
        background: {C['bg']};
        color: {C['text']};
        font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        font-size: 13px;
    }}

    QMainWindow {{
        background: {C['bg']};
    }}

    QFrame#AeroPanel {{
        background: {C['bg_panel']};
        border: 1px solid {C['border']};
        border-radius: 4px;
    }}

    QFrame#AeroPanelGlow {{
        background: {C['bg_sidebar']};
        border: none;
    }}

    QFrame#Sidebar {{
        background: {C['bg_sidebar']};
        border-right: 1px solid {C['border_dark']};
    }}

    QPushButton {{
        background: {C['bg_panel']};
        border: 1px solid {C['border']};
        border-radius: 3px;
        padding: 6px 16px;
        color: {C['text']};
        min-height: 18px;
    }}
    QPushButton:hover {{
        background: {C['bg_header']};
        border: 1px solid {C['accent']};
    }}
    QPushButton:pressed {{
        background: #e0e0e0;
    }}
    QPushButton:disabled {{
        background: {C['bg_header']};
        border: 1px solid {C['border']};
        color: {C['text_muted']};
    }}

    QPushButton#PrimaryBtn {{
        background: {C['accent']};
        border: 1px solid {C['accent']};
        color: {C['accent_text']};
        font-weight: 600;
    }}
    QPushButton#PrimaryBtn:hover {{
        background: {C['accent_hover']};
    }}

    QPushButton#DangerBtn {{
        background: {C['bg_panel']};
        border: 1px solid {C['red']};
        color: {C['red']};
    }}
    QPushButton#DangerBtn:hover {{
        background: #fff5f5;
    }}

    QPushButton#NavBtn {{
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
        border-radius: 0;
        padding: 11px 16px;
        text-align: left;
        font-size: 13px;
        color: {C['text_sidebar']};
    }}
    QPushButton#NavBtn:hover {{
        background: {C['bg_sidebar_hover']};
        border-left: 3px solid {C['text_muted']};
    }}
    QPushButton#NavBtn:checked {{
        background: {C['bg_sidebar_active']};
        border-left: 3px solid {C['accent']};
        color: {C['text_light']};
        font-weight: 600;
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {C['bg_input']};
        border: 1px solid {C['border']};
        border-radius: 3px;
        padding: 6px 10px;
        color: {C['text']};
        selection-background-color: #cce8ff;
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {C['border_focus']};
    }}

    QSpinBox, QComboBox {{
        background: {C['bg_input']};
        border: 1px solid {C['border']};
        border-radius: 3px;
        padding: 5px 8px;
        color: {C['text']};
        min-height: 18px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {C['bg_panel']};
        border: 1px solid {C['border']};
        color: {C['text']};
        selection-background-color: #cce8ff;
    }}

    QTableWidget {{
        background: {C['bg_panel']};
        alternate-background-color: {C['bg_table_alt']};
        border: 1px solid {C['border']};
        border-radius: 3px;
        gridline-color: #e8e8e8;
        selection-background-color: #cce8ff;
    }}
    QTableWidget::item {{
        padding: 5px 8px;
    }}
    QTableWidget::item:selected {{
        background: #cce8ff;
        color: {C['text']};
    }}
    QHeaderView::section {{
        background: {C['bg_header']};
        color: {C['text_secondary']};
        border: none;
        border-bottom: 1px solid {C['border']};
        border-right: 1px solid {C['border']};
        padding: 6px 8px;
        font-weight: 600;
        font-size: 11px;
    }}

    QLabel {{
        background: transparent;
    }}
    QLabel#Title {{
        font-size: 20px;
        font-weight: 700;
    }}
    QLabel#Subtitle {{
        color: {C['text_secondary']};
    }}
    QLabel#GlowLabel {{
        color: {C['accent']};
        font-weight: 600;
    }}
    QLabel#StatValue {{
        font-size: 32px;
        font-weight: 700;
        font-family: "Consolas", monospace;
    }}
    QLabel#StatLabel {{
        font-size: 11px;
        color: {C['text_secondary']};
    }}

    QProgressBar {{
        background: {C['bg_header']};
        border: 1px solid {C['border']};
        border-radius: 3px;
        text-align: center;
        color: {C['text']};
        min-height: 20px;
    }}
    QProgressBar::chunk {{
        background: {C['accent']};
        border-radius: 2px;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
    }}
    QScrollBar::handle:vertical {{
        background: #c0c0c0;
        border-radius: 4px;
        min-height: 25px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #a0a0a0;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
    }}
    QScrollBar::handle:horizontal {{
        background: #c0c0c0;
        border-radius: 4px;
        min-width: 25px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: #a0a0a0;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    QGroupBox {{
        background: {C['bg_panel']};
        border: 1px solid {C['border']};
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 18px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 10px;
        color: {C['accent']};
    }}

    QTabWidget::pane {{
        background: {C['bg_panel']};
        border: 1px solid {C['border']};
        border-radius: 3px;
    }}
    QTabBar::tab {{
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 8px 16px;
        color: {C['text_secondary']};
    }}
    QTabBar::tab:selected {{
        color: {C['accent']};
        border-bottom: 2px solid {C['accent']};
    }}
    QTabBar::tab:hover {{
        color: {C['text']};
    }}

    QToolTip {{
        background: {C['bg_dark']};
        border: 1px solid {C['border_dark']};
        border-radius: 3px;
        padding: 4px 8px;
        color: {C['text_light']};
    }}

    QCheckBox {{
        spacing: 6px;
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {C['border']};
        border-radius: 2px;
        background: {C['bg_input']};
    }}
    QCheckBox::indicator:checked {{
        background: {C['accent']};
        border: 1px solid {C['accent']};
    }}

    QSplitter::handle {{
        background: {C['border']};
    }}
    QSplitter::handle:horizontal {{ width: 1px; }}
    QSplitter::handle:vertical {{ height: 1px; }}
    """


def apply_palette(app):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(C["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(C["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(C["bg_input"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(C["bg_table_alt"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(C["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(C["bg_panel"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(C["text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(C["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
