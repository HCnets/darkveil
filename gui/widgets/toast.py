from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint


class ToastNotification(QWidget):
    _instances = []

    def __init__(self, message, parent=None, duration=5000, level="info"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(360)

        ToastNotification._instances.append(self)
        self._cleanup_old()

        bg = "#2d2d2d" if level == "info" else ("#4a1a1a" if level == "error" else "#1a3a1a")
        border = "#555" if level == "info" else ("#c62828" if level == "error" else "#2e7d32")
        self.setStyleSheet(f"""
            QWidget {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            QLabel {{
                color: #eee;
                font-size: 12px;
                padding: 2px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        icon_text = {"info": "[i]", "error": "[!]", "success": "[+]"}.get(level, "[i]")
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"color: {border}; font-weight: bold; font-size: 13px;")
        layout.addWidget(icon)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label, 1)

        self.adjustSize()
        self.setFixedHeight(max(self.sizeHint().height(), 36))

        # Position at bottom-right of parent
        if parent:
            px = parent.width() - self.width() - 20
            py = parent.height() - self.height() - 20
            self._target_pos = QPoint(px, py)
            self.move(px, parent.height())
        else:
            self._target_pos = QPoint(100, 100)
            self.move(100, 200)

        # Slide-in animation
        self._anim = QPropertyAnimation(self, b"pos")
        self._anim.setDuration(250)
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(self._target_pos)
        self._anim.start()

        # Fade-out timer
        self._fade_timer = QTimer(self)
        self._fade_timer.setSingleShot(True)
        self._fade_timer.timeout.connect(self._fade_out)
        self._fade_timer.start(duration)

        self.show()

    def _fade_out(self):
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(400)
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(self._remove)
        self._fade_anim.start()

    def _remove(self):
        if self in ToastNotification._instances:
            ToastNotification._instances.remove(self)
        self.deleteLater()

    def _cleanup_old(self):
        # Keep max 3 toasts visible
        while len(ToastNotification._instances) > 3:
            old = ToastNotification._instances.pop(0)
            try:
                old.deleteLater()
            except Exception:
                pass


def show_toast(parent, message, level="info", duration=5000):
    """Show a toast notification. level: info/success/error"""
    return ToastNotification(message, parent=parent, duration=duration, level=level)
