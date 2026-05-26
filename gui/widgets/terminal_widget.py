from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QFont


def _escape_html(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class LogBridge(QObject):
    log_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()


class TerminalWidget(QWidget):
    command_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bridge = LogBridge()
        self._bridge.log_signal.connect(self._write_log_safe)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(5000)
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background: #1e1e1e;
                border: 1px solid #d0d0d0;
                border-radius: 0;
                padding: 8px;
                color: #cccccc;
            }
        """)
        layout.addWidget(self.output)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        prompt = QLabel(" >")
        prompt.setFixedWidth(24)
        prompt.setStyleSheet("""
            QLabel {
                background: #2b2b2b;
                border: 1px solid #d0d0d0;
                border-right: none;
                color: #0078d4;
                font-family: Consolas;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 0;
            }
        """)

        self.input = QLineEdit()
        self.input.setPlaceholderText("输入命令... (help 查看帮助)")
        self.input.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1px solid #d0d0d0;
                border-left: none;
                border-radius: 0;
                padding: 6px 10px;
                color: #1a1a1a;
                font-family: Consolas;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
                border-left: none;
            }
        """)
        self.input.returnPressed.connect(self._on_command)

        input_layout.addWidget(prompt)
        input_layout.addWidget(self.input)
        layout.addLayout(input_layout)

    def _on_command(self):
        cmd = self.input.text().strip()
        if cmd:
            self.write(f"> {cmd}", "#0078d4")
            self.input.clear()
            self.command_entered.emit(cmd)

    def write(self, text, color=None):
        safe = _escape_html(text)
        if color:
            self.output.appendHtml(f'<span style="color: {color};">{safe}</span>')
        else:
            self.output.appendPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def write_log(self, timestamp, level, message):
        self._bridge.log_signal.emit(timestamp, level, message)

    def _write_log_safe(self, timestamp, level, message):
        colors = {
            "INFO": "#999999", "WARN": "#f57f17", "ERROR": "#c62828",
            "SUCCESS": "#2e7d32", "DEBUG": "#666666",
        }
        color = colors.get(level, "#999999")
        safe_msg = _escape_html(message)
        self.output.appendHtml(
            f'<span style="color: #666;">[{_escape_html(timestamp)}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{_escape_html(level)}]</span> '
            f'<span style="color: #ccc;">{safe_msg}</span>'
        )
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def clear(self):
        self.output.clear()
