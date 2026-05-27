import socket
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTextEdit, QGroupBox, QCheckBox,
    QTabWidget
)
from gui.widgets.result_table import ResultTable
from PyQt6.QtCore import Qt, QThread, pyqtSignal


FAKE_SSH_BANNER = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"
FAKE_HTTP_RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Server: Apache/2.4.52 (Ubuntu)\r\n"
    b"Content-Type: text/html\r\n"
    b"Connection: close\r\n\r\n"
    b"<html><head><title>Login</title></head>"
    b"<body><h1>Admin Panel</h1>"
    b'<form method="post"><input name="user"><input name="pass" type="password">'
    b'<button type="submit">Login</button></form></body></html>'
)


class HoneypotWorker(QThread):
    log_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    capture_signal = pyqtSignal(dict)

    def __init__(self, service_type, port):
        super().__init__()
        self.service_type = service_type
        self.port = port
        self._running = False
        self._server_sock = None
        self._attack_count = 0

    def run(self):
        self._running = True
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1.0)
            sock.bind(("0.0.0.0", self.port))
            sock.listen(10)
            self._server_sock = sock
            self.log_signal.emit(
                f"[{self._ts()}] {self.service_type} 蜜罐启动在端口 {self.port}"
            )

            while self._running:
                try:
                    conn, addr = sock.accept()
                    self._attack_count += 1
                    self.log_signal.emit(
                        f"[{self._ts()}] #{self._attack_count} 连接来自 {addr[0]}:{addr[1]}"
                    )
                    t = threading.Thread(
                        target=self._handle, args=(conn, addr), daemon=True
                    )
                    t.start()
                except socket.timeout:
                    continue
                except OSError:
                    break
        except PermissionError:
            self.error_signal.emit(f"端口 {self.port} 需要管理员权限")
        except OSError as e:
            self.error_signal.emit(f"绑定失败: {e}")
        finally:
            if self._server_sock:
                try:
                    self._server_sock.close()
                except Exception:
                    pass

    def _handle(self, conn, addr):
        try:
            conn.settimeout(10)
            ts = self._ts()

            if self.service_type == "SSH":
                conn.send(FAKE_SSH_BANNER)
                data = conn.recv(1024)
                if data:
                    self.log_signal.emit(
                        f"[{ts}]   SSH 数据 ({len(data)} bytes): {data[:100]}"
                    )
                    self.capture_signal.emit({
                        "service": "SSH", "source_ip": addr[0],
                        "source_port": addr[1], "data": data[:500].decode("utf-8", errors="replace"),
                    })

            elif self.service_type == "HTTP":
                data = conn.recv(4096)
                if data:
                    lines = data.decode("utf-8", errors="replace").split("\n")
                    req_line = lines[0] if lines else ""
                    self.log_signal.emit(f"[{ts}]   HTTP 请求: {req_line.strip()}")

                    body = ""
                    body_start = data.find(b"\r\n\r\n")
                    if body_start >= 0:
                        body = data[body_start + 4:]
                        if body:
                            self.log_signal.emit(
                                f"[{ts}]   POST 数据: {body.decode('utf-8', errors='replace')[:200]}"
                            )
                    conn.send(FAKE_HTTP_RESPONSE)
                    self.capture_signal.emit({
                        "service": "HTTP", "source_ip": addr[0],
                        "source_port": addr[1],
                        "data": f"{req_line.strip()}\n{body.decode('utf-8', errors='replace')[:300]}",
                    })

            elif self.service_type == "TELNET":
                conn.send(b"login: ")
                user = conn.recv(1024)
                user_str = user.decode("utf-8", errors="replace").strip() if user else ""
                if user:
                    self.log_signal.emit(f"[{ts}]   用户名: {user_str}")
                conn.send(b"Password: ")
                pwd = conn.recv(1024)
                pwd_str = pwd.decode("utf-8", errors="replace").strip() if pwd else ""
                if pwd:
                    self.log_signal.emit(f"[{ts}]   密码: {pwd_str}")
                conn.send(b"Login incorrect\r\n")
                self.capture_signal.emit({
                    "service": "TELNET", "source_ip": addr[0],
                    "source_port": addr[1],
                    "data": f"user={user_str} pass={pwd_str}",
                })

        except socket.timeout:
            pass
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def stop(self):
        self._running = False
        if self._server_sock:
            try:
                self._server_sock.close()
            except Exception:
                pass

    def _ts(self):
        return datetime.now().strftime("%H:%M:%S")


class HoneypotPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._workers = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("蜜罐系统")
        title.setObjectName("title")
        layout.addWidget(title)

        # 服务配置
        svc_frame = QFrame()
        svc_frame.setObjectName("panel")
        svc_layout = QHBoxLayout(svc_frame)

        self.ssh_check = QCheckBox("SSH 蜜罐")
        self.ssh_port = QLineEdit("2222")
        self.ssh_port.setFixedWidth(60)

        self.http_check = QCheckBox("HTTP 蜜罐")
        self.http_port = QLineEdit("8880")
        self.http_port.setFixedWidth(60)

        self.telnet_check = QCheckBox("Telnet 蜜罐")
        self.telnet_port = QLineEdit("2323")
        self.telnet_port.setFixedWidth(60)

        for check, port_input in [
            (self.ssh_check, self.ssh_port),
            (self.http_check, self.http_port),
            (self.telnet_check, self.telnet_port),
        ]:
            svc_layout.addWidget(check)
            svc_layout.addWidget(QLabel("端口:"))
            svc_layout.addWidget(port_input)
            svc_layout.addSpacing(20)

        svc_layout.addStretch()

        self.btn_start = QPushButton("启动蜜罐")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._toggle)
        svc_layout.addWidget(self.btn_start)

        layout.addWidget(svc_frame)

        # Tab widget for logs and history
        self.tabs = QTabWidget()

        # 日志输出 tab
        log_group = QGroupBox("捕获日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("terminal")
        log_layout.addWidget(self.log_text)

        btn_row = QHBoxLayout()
        self.btn_clear = QPushButton("清空日志")
        self.btn_clear.clicked.connect(self.log_text.clear)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        self.status_label = QLabel("蜜罐未启动")
        self.status_label.setObjectName("subtitle")
        btn_row.addWidget(self.status_label)
        log_layout.addLayout(btn_row)

        self.tabs.addTab(log_group, "实时日志")

        # 捕获历史 tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        self.history_table = ResultTable(["时间", "服务", "来源IP", "来源端口", "数据"])
        self.history_table.set_column_widths([140, 60, 130, 80, 350])
        history_layout.addWidget(self.history_table)

        history_btn_row = QHBoxLayout()
        self.btn_refresh_history = QPushButton("刷新历史")
        self.btn_refresh_history.clicked.connect(self._load_history)
        history_btn_row.addWidget(self.btn_refresh_history)
        self.btn_clear_history = QPushButton("清空历史")
        self.btn_clear_history.clicked.connect(self._clear_history)
        history_btn_row.addWidget(self.btn_clear_history)
        history_btn_row.addStretch()
        self.history_count = QLabel("")
        self.history_count.setObjectName("subtitle")
        history_btn_row.addWidget(self.history_count)
        history_layout.addLayout(history_btn_row)

        self.tabs.addTab(history_widget, "捕获历史")

        layout.addWidget(self.tabs)

    def _toggle(self):
        if self._workers:
            self._stop_all()
        else:
            self._start_all()

    def _start_all(self):
        services = []
        if self.ssh_check.isChecked():
            port = self._parse_port(self.ssh_port)
            if port:
                services.append(("SSH", port))
        if self.http_check.isChecked():
            port = self._parse_port(self.http_port)
            if port:
                services.append(("HTTP", port))
        if self.telnet_check.isChecked():
            port = self._parse_port(self.telnet_port)
            if port:
                services.append(("TELNET", port))

        if not services:
            self.log_text.append("请选择至少一个服务")
            return

        self.log_text.clear()
        for svc_type, port in services:
            worker = HoneypotWorker(svc_type, port)
            worker.log_signal.connect(self._on_log)
            worker.error_signal.connect(self._on_error)
            worker.capture_signal.connect(self._on_capture)
            worker.start()
            self._workers[svc_type] = worker

        self.btn_start.setText("停止蜜罐")
        self.btn_start.setObjectName("danger")
        self.btn_start.style().unpolish(self.btn_start)
        self.btn_start.style().polish(self.btn_start)
        self.status_label.setText(f"运行中: {', '.join(s[0] for s in services)}")

        self._set_checks_enabled(False)

    def _stop_all(self):
        for worker in self._workers.values():
            worker.stop()
        for worker in self._workers.values():
            worker.wait(3000)
        self._workers.clear()

        self.btn_start.setText("启动蜜罐")
        self.btn_start.setObjectName("primary")
        self.btn_start.style().unpolish(self.btn_start)
        self.btn_start.style().polish(self.btn_start)
        self.status_label.setText("蜜罐已停止")
        self._set_checks_enabled(True)
        self.log_text.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] 蜜罐已停止")

    def _set_checks_enabled(self, enabled):
        self.ssh_check.setEnabled(enabled)
        self.http_check.setEnabled(enabled)
        self.telnet_check.setEnabled(enabled)
        self.ssh_port.setEnabled(enabled)
        self.http_port.setEnabled(enabled)
        self.telnet_port.setEnabled(enabled)

    def _parse_port(self, line_edit):
        text = line_edit.text().strip()
        if text.isdigit() and 0 < int(text) <= 65535:
            return int(text)
        return None

    def _on_log(self, text):
        self.log_text.append(text)

    def _on_error(self, text):
        self.log_text.append(f"[错误] {text}")

    def _on_capture(self, capture):
        db = self.engine.db
        if db:
            db.add_honeypot_capture(
                service=capture.get("service", ""),
                source_ip=capture.get("source_ip", ""),
                source_port=capture.get("source_port"),
                data=capture.get("data", ""),
            )

    def _load_history(self):
        db = self.engine.db
        if not db:
            return
        self.history_table.clear_data()
        captures = db.get_honeypot_captures(100)
        for c in captures:
            self.history_table.add_row([
                c.get("captured_at", "-"),
                c.get("service", ""),
                c.get("source_ip", ""),
                str(c.get("source_port", "")),
                (c.get("data") or "")[:100],
            ])
        self.history_count.setText(f"{len(captures)} 条记录")

    def _clear_history(self):
        db = self.engine.db
        if not db:
            return
        try:
            with db._lock:
                cursor = db.conn.cursor()
                cursor.execute("DELETE FROM honeypot_captures")
                db.conn.commit()
            self.history_table.clear_data()
            self.history_count.setText("已清空")
        except Exception as e:
            self.history_count.setText(f"清空失败: {e}")
