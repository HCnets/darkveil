from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QEvent
from PyQt6.QtGui import QTextCursor, QFont, QKeySequence, QShortcut


def _escape_html(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class LogBridge(QObject):
    log_signal = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()


class TerminalInput(QLineEdit):
    """QLineEdit with command history and tab completion."""

    _COMMANDS = [
        "help", "clear", "stats", "targets", "exploit list",
        "scan", "web",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._history_index = -1
        self._pending_text = ""

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key.Key_Up:
            if not self._history:
                return
            if self._history_index == -1:
                self._pending_text = self.text()
            if self._history_index < len(self._history) - 1:
                self._history_index += 1
                self.setText(self._history[self._history_index])
            return

        if key == Qt.Key.Key_Down:
            if self._history_index <= 0:
                self._history_index = -1
                self.setText(self._pending_text)
                return
            self._history_index -= 1
            self.setText(self._history[self._history_index])
            return

        if key == Qt.Key.Key_Tab:
            self._tab_complete()
            return

        # Reset history navigation on any other key
        self._history_index = -1
        super().keyPressEvent(event)

    def add_history(self, cmd):
        if cmd and (not self._history or self._history[0] != cmd):
            self._history.insert(0, cmd)
        self._history_index = -1
        self._pending_text = ""

    def _tab_complete(self):
        text = self.text().strip()
        if not text:
            return
        matches = [c for c in self._COMMANDS if c.startswith(text)]
        if len(matches) == 1:
            self.setText(matches[0] + " ")
        elif len(matches) > 1:
            # Find common prefix
            prefix = matches[0]
            for m in matches[1:]:
                while not m.startswith(prefix):
                    prefix = prefix[:-1]
            if len(prefix) > len(text):
                self.setText(prefix)


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

        self.input = TerminalInput()
        self.input.setPlaceholderText("输入命令... (↑↓ 历史, Tab 补全, help 帮助)")
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

        # Ctrl+K to clear terminal
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self.clear)

    def _on_command(self):
        cmd = self.input.text().strip()
        if cmd:
            self.input.add_history(cmd)
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
