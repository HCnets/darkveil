import socket
import struct
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTextEdit, QGroupBox, QSplitter,
    QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class CaptureWorker(QThread):
    packet_captured = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, interface_ip, ports, protocol, parse_mode=False):
        super().__init__()
        self.interface_ip = interface_ip
        self.ports = ports
        self.protocol = protocol
        self.parse_mode = parse_mode
        self._running = False
        self._socks = []

    def run(self):
        self._running = True
        try:
            if self.protocol in ("TCP", "ALL"):
                self._capture_tcp()
            elif self.protocol == "UDP":
                self._capture_udp()
            else:
                self._capture_raw()
        except Exception as e:
            if self._running:
                self.error.emit(str(e))
        finally:
            self.finished.emit()

    def _capture_tcp(self):
        import select
        listeners = []
        for port in self.ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(0.5)
                sock.bind((self.interface_ip, port))
                sock.listen(5)
                listeners.append(sock)
                self.packet_captured.emit(
                    f"[{self._ts()}] TCP 监听启动: {self.interface_ip}:{port}"
                )
            except Exception as e:
                self.packet_captured.emit(
                    f"[{self._ts()}] 绑定端口 {port} 失败: {e}"
                )

        if not listeners:
            return

        self._socks = listeners

        while self._running:
            try:
                readable, _, _ = select.select(listeners, [], [], 0.5)
                for sock in readable:
                    conn, addr = sock.accept()
                    ts = self._ts()
                    self.packet_captured.emit(
                        f"[{ts}] TCP 连接: {addr[0]}:{addr[1]} -> {self.interface_ip}:{sock.getsockname()[1]}"
                    )
                    threading.Thread(
                        target=self._handle_tcp_conn, args=(conn, ts), daemon=True
                    ).start()
            except OSError:
                break

        for sock in listeners:
            try:
                sock.close()
            except Exception:
                pass

    def _handle_tcp_conn(self, conn, ts):
        try:
            conn.settimeout(2)
            data = conn.recv(4096)
            if data:
                hex_data = data[:64].hex(" ")
                self.packet_captured.emit(
                    f"[{ts}]   数据 ({len(data)} bytes): {hex_data}"
                )
                if self.parse_mode:
                    parsed = self._parse_protocol(data)
                    if parsed:
                        self.packet_captured.emit(f"[{ts}]   {parsed}")
        except socket.timeout:
            pass
        except Exception:
            pass
        finally:
            conn.close()

    def _parse_protocol(self, data):
        try:
            # HTTP request
            if data[:4] in (b"GET ", b"POST", b"PUT ", b"DELE", b"HEAD", b"OPTI", b"PATC"):
                lines = data.decode("utf-8", errors="replace").split("\r\n")
                req_line = lines[0] if lines else ""
                host = ""
                for line in lines[1:]:
                    if line.lower().startswith("host:"):
                        host = line.split(":", 1)[1].strip()
                        break
                return f"[HTTP 请求] {req_line} | Host: {host}"

            # HTTP response
            if data[:5] == b"HTTP/":
                lines = data.decode("utf-8", errors="replace").split("\r\n")
                status_line = lines[0] if lines else ""
                return f"[HTTP 响应] {status_line}"

            # SSH handshake
            if data.startswith(b"SSH-"):
                banner = data.decode("utf-8", errors="replace").strip()
                return f"[SSH 握手] {banner}"

            # DNS query (port 53)
            if len(data) >= 12 and data[2:4] == b"\x01\x00":
                try:
                    qname_parts = []
                    idx = 12
                    while idx < len(data):
                        length = data[idx]
                        if length == 0:
                            break
                        idx += 1
                        qname_parts.append(data[idx:idx+length].decode("utf-8", errors="replace"))
                        idx += length
                    qname = ".".join(qname_parts)
                    if qname:
                        return f"[DNS 查询] {qname}"
                except Exception:
                    pass

            return None
        except Exception:
            return None

    def _capture_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        self._socks = [sock]

        for port in self.ports:
            try:
                sock.bind((self.interface_ip, port))
                self.packet_captured.emit(
                    f"[{self._ts()}] UDP 监听启动: {self.interface_ip}:{port}"
                )
            except Exception as e:
                self.packet_captured.emit(
                    f"[{self._ts()}] 绑定端口 {port} 失败: {e}"
                )

        while self._running:
            try:
                data, addr = sock.recvfrom(4096)
                ts = self._ts()
                hex_data = data[:64].hex(" ")
                self.packet_captured.emit(
                    f"[{ts}] UDP 数据: {addr[0]}:{addr[1]} ({len(data)} bytes) {hex_data}"
                )
            except socket.timeout:
                continue
            except OSError:
                break

    def _capture_raw(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            sock.bind((self.interface_ip, 0))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.settimeout(0.5)
            self._socks = [sock]
            self.packet_captured.emit(
                f"[{self._ts()}] 原始套接字监听启动: {self.interface_ip}"
            )

            while self._running:
                try:
                    data, addr = sock.recvfrom(65535)
                    ts = self._ts()
                    if len(data) >= 20:
                        proto = data[9]
                        proto_name = {6: "TCP", 17: "UDP", 1: "ICMP"}.get(proto, str(proto))
                        src = f"{data[12]}.{data[13]}.{data[14]}.{data[15]}"
                        dst = f"{data[16]}.{data[17]}.{data[18]}.{data[19]}"
                        self.packet_captured.emit(
                            f"[{ts}] {proto_name}: {src} -> {dst} ({len(data)} bytes)"
                        )
                except socket.timeout:
                    continue
        except PermissionError:
            self.error.emit("原始套接字需要管理员权限")
        except Exception as e:
            self.error.emit(f"原始套接字错误: {e}")

    def stop(self):
        self._running = False
        for sock in self._socks:
            try:
                sock.close()
            except Exception:
                pass
        self._socks.clear()

    def _ts(self):
        return datetime.now().strftime("%H:%M:%S")


class MonitorPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.worker = None
        self._packet_count = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("流量监控")
        title.setObjectName("title")
        layout.addWidget(title)

        # 控制栏
        ctrl_frame = QFrame()
        ctrl_frame.setObjectName("panel")
        ctrl_layout = QHBoxLayout(ctrl_frame)

        ctrl_layout.addWidget(QLabel("监听地址:"))
        self.addr_input = QLineEdit("0.0.0.0")
        self.addr_input.setFixedWidth(140)
        ctrl_layout.addWidget(self.addr_input)

        ctrl_layout.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit("8080")
        self.port_input.setPlaceholderText("逗号分隔，如 80,443")
        self.port_input.setFixedWidth(160)
        ctrl_layout.addWidget(self.port_input)

        ctrl_layout.addWidget(QLabel("协议:"))
        self.btn_tcp = QPushButton("TCP")
        self.btn_tcp.setCheckable(True)
        self.btn_tcp.setChecked(True)
        self.btn_tcp.clicked.connect(lambda: self._set_proto("TCP"))
        ctrl_layout.addWidget(self.btn_tcp)

        self.btn_udp = QPushButton("UDP")
        self.btn_udp.setCheckable(True)
        self.btn_udp.clicked.connect(lambda: self._set_proto("UDP"))
        ctrl_layout.addWidget(self.btn_udp)

        self.btn_all = QPushButton("ALL")
        self.btn_all.setCheckable(True)
        self.btn_all.clicked.connect(lambda: self._set_proto("ALL"))
        ctrl_layout.addWidget(self.btn_all)

        self.parse_check = QCheckBox("解析模式")
        self.parse_check.setToolTip("自动识别 HTTP/SSH/DNS 协议并解析")
        ctrl_layout.addWidget(self.parse_check)

        self.btn_start = QPushButton("开始捕获")
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self._toggle_capture)
        ctrl_layout.addWidget(self.btn_start)

        ctrl_layout.addStretch()
        self.stats_label = QLabel("数据包: 0")
        self.stats_label.setObjectName("subtitle")
        ctrl_layout.addWidget(self.stats_label)

        layout.addWidget(ctrl_frame)

        # 输出区
        output_group = QGroupBox("捕获输出")
        output_layout = QVBoxLayout(output_group)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setObjectName("terminal")
        output_layout.addWidget(self.output_text)

        btn_row = QHBoxLayout()
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self.output_text.clear)
        btn_row.addWidget(self.btn_clear)
        btn_row.addStretch()
        btn_row.addWidget(QLabel("提示: 原始套接字模式需要管理员权限"))
        output_layout.addLayout(btn_row)

        layout.addWidget(output_group)

    def _set_proto(self, proto):
        for btn in (self.btn_tcp, self.btn_udp, self.btn_all):
            btn.setChecked(False)
        {"TCP": self.btn_tcp, "UDP": self.btn_udp, "ALL": self.btn_all}[proto].setChecked(True)

    def _get_proto(self):
        if self.btn_udp.isChecked():
            return "UDP"
        if self.btn_all.isChecked():
            return "ALL"
        return "TCP"

    def _toggle_capture(self):
        if self.worker and self.worker.isRunning():
            self._stop_capture()
        else:
            self._start_capture()

    def _start_capture(self):
        addr = self.addr_input.text().strip() or "0.0.0.0"
        port_text = self.port_input.text().strip()

        ports = []
        for p in port_text.split(","):
            p = p.strip()
            if p.isdigit() and 0 < int(p) <= 65535:
                ports.append(int(p))
        if not ports:
            ports = [8080]

        proto = self._get_proto()
        self._packet_count = 0
        self.output_text.clear()
        self.output_text.append(f"开始捕获 {addr} 端口 {ports} 协议 {proto}\n")

        self.worker = CaptureWorker(addr, ports, proto, self.parse_check.isChecked())
        self.worker.packet_captured.connect(self._on_packet)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

        self.btn_start.setText("停止捕获")
        self.btn_start.setObjectName("danger")
        self.btn_start.style().unpolish(self.btn_start)
        self.btn_start.style().polish(self.btn_start)

    def _stop_capture(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait(3000)
            self.worker = None
        self._reset_btn()

    def _on_packet(self, text):
        self._packet_count += 1
        self.output_text.append(text)
        self.stats_label.setText(f"数据包: {self._packet_count}")

    def _on_error(self, text):
        self.output_text.append(f"[错误] {text}")

    def _on_finished(self):
        self.output_text.append("\n捕获已停止")
        self._reset_btn()

    def _reset_btn(self):
        self.btn_start.setText("开始捕获")
        self.btn_start.setObjectName("primary")
        self.btn_start.style().unpolish(self.btn_start)
        self.btn_start.style().polish(self.btn_start)
