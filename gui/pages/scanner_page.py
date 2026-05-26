from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QProgressBar, QTabWidget,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from gui.widgets.result_table import ResultTable


class ScanWorker(QThread):
    progress = pyqtSignal(int, int, object)
    finished = pyqtSignal(str, object)
    error = pyqtSignal(str)

    def __init__(self, scanner_type, scanner, target, options):
        super().__init__()
        self.scanner_type = scanner_type
        self.scanner = scanner
        self.target = target
        self.options = options
        self.cancelled = False

    def _safe_emit(self, signal, *args):
        if self.cancelled:
            return
        try:
            signal.emit(*args)
        except Exception:
            pass

    def run(self):
        try:
            def on_progress(done, total, info):
                if self.cancelled:
                    return
                try:
                    self.progress.emit(done, total, info)
                except Exception:
                    pass

            if self.scanner_type == "port":
                result = self.scanner.scan(
                    self.target,
                    ports=self.options.get("ports"),
                    callback=on_progress,
                )
                self._safe_emit(self.finished, "port", result or [])

            elif self.scanner_type == "web":
                result = self.scanner.scan(
                    self.target,
                    callback=on_progress,
                )
                self._safe_emit(self.finished, "web", result or [])

            elif self.scanner_type == "full":
                port_result = self.scanner["port"].scan(
                    self.target,
                    ports=self.options.get("ports"),
                    callback=on_progress,
                )
                self._safe_emit(self.finished, "port_partial", port_result or [])

                if not self.cancelled:
                    web_result = self.scanner["web"].scan(
                        self.target,
                        callback=on_progress,
                    )
                    self._safe_emit(self.finished, "web_partial", web_result or [])

                self._safe_emit(self.finished, "full_done", [])

        except Exception as e:
            self._safe_emit(self.error, str(e))


class ScannerPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.worker = None
        self._scan_target = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("漏洞扫描")
        title.setObjectName("title")
        layout.addWidget(title)

        target_frame = QFrame()
        target_frame.setObjectName("panel")
        target_layout = QHBoxLayout(target_frame)
        target_layout.setSpacing(8)

        target_layout.addWidget(QLabel("目标:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("输入 IP 或域名")
        target_layout.addWidget(self.target_input)

        self.scan_type = QComboBox()
        self.scan_type.addItems(["端口扫描", "Web 漏洞扫描", "全面扫描"])
        self.scan_type.setFixedWidth(130)
        target_layout.addWidget(self.scan_type)

        self.btn_scan = QPushButton("开始扫描")
        self.btn_scan.setObjectName("primary")
        self.btn_scan.clicked.connect(self._start_scan)
        target_layout.addWidget(self.btn_scan)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setObjectName("danger")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_scan)
        target_layout.addWidget(self.btn_stop)

        self.btn_import = QPushButton("导入 Nmap XML")
        self.btn_import.clicked.connect(self._import_nmap)
        target_layout.addWidget(self.btn_import)

        layout.addWidget(target_frame)

        options_frame = QFrame()
        options_frame.setObjectName("panel")
        options_layout = QHBoxLayout(options_frame)
        options_layout.setSpacing(8)

        options_layout.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("默认常见端口")
        self.port_input.setFixedWidth(180)
        options_layout.addWidget(self.port_input)

        options_layout.addWidget(QLabel("线程:"))
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 300)
        self.thread_spin.setValue(100)
        self.thread_spin.setFixedWidth(70)
        options_layout.addWidget(self.thread_spin)

        options_layout.addStretch()
        layout.addWidget(options_frame)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.tabs = QTabWidget()

        self.port_table = ResultTable(["端口", "状态", "服务", "Banner"])
        self.port_table.set_column_widths([80, 80, 120, 500])
        self.tabs.addTab(self.port_table, "端口")

        self.vuln_table = ResultTable(["类型", "严重程度", "标题", "描述", "证据"])
        self.vuln_table.set_column_widths([90, 90, 180, 250, 250])
        self.tabs.addTab(self.vuln_table, "漏洞")

        layout.addWidget(self.tabs)

        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

    def _cleanup_worker(self):
        if not self.worker:
            return
        self.worker.cancelled = True
        self.engine.get_module("port_scanner").stop()
        self.engine.get_module("web_scanner").stop()
        try:
            self.worker.progress.disconnect()
            self.worker.finished.disconnect()
            self.worker.error.disconnect()
        except Exception:
            pass
        if self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(2000)
        self.worker = None

    def _start_scan(self):
        target = self.target_input.text().strip()
        if not target:
            self.status_label.setText("请输入扫描目标")
            return

        self._cleanup_worker()

        scan_type = self.scan_type.currentIndex()
        self._scan_target = target
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.port_table.clear_data()
        self.vuln_table.clear_data()

        if scan_type == 0:
            scanner = self.engine.get_module("port_scanner")
            self.worker = ScanWorker("port", scanner, target, {
                "ports": self.port_input.text().strip() or None,
            })
        elif scan_type == 1:
            scanner = self.engine.get_module("web_scanner")
            self.worker = ScanWorker("web", scanner, target, {})
        else:
            port_scanner = self.engine.get_module("port_scanner")
            web_scanner = self.engine.get_module("web_scanner")
            self.worker = ScanWorker("full", {"port": port_scanner, "web": web_scanner}, target, {
                "ports": self.port_input.text().strip() or None,
            })

        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
        self.status_label.setText(f"正在扫描: {target}")

    def _stop_scan(self):
        self._cleanup_worker()
        self._reset_ui()
        self.status_label.setText("已停止")

    def _import_nmap(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Nmap XML 文件", "", "XML Files (*.xml);;All Files (*)"
        )
        if not path:
            return

        try:
            from modules.nmap_importer import import_nmap_file
            hosts, ports = import_nmap_file(path, self.engine.db, self.engine.logger)
            self.status_label.setText(f"导入完成: {hosts} 个主机, {ports} 个端口")

            # Show imported data in the port table
            self.port_table.clear_data()
            targets = self.engine.db.get_targets()
            for t in targets[:20]:
                t_ports = self.engine.db.get_ports(t["id"])
                for p in t_ports:
                    self.port_table.add_row([
                        f"{t.get('host', '')}:{p.get('port', '')}",
                        p.get("state", ""),
                        p.get("service") or "-",
                        (p.get("version") or p.get("banner") or "")[:80],
                    ])
            self.tabs.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", str(e))
            self.status_label.setText(f"导入失败: {e}")

    def _reset_ui(self):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setVisible(False)

    def _on_progress(self, done, total, info):
        if not self.worker or self.worker.cancelled:
            return
        try:
            if total > 0:
                self.progress_bar.setValue(int(done / total * 100))
        except Exception:
            pass

    def _on_finished(self, scan_type, results):
        if not self.worker or self.worker.cancelled:
            return
        try:
            if scan_type in ("port", "port_partial"):
                port_scanner = self.engine.get_module("port_scanner")
                port_scanner.save_results(self._scan_target, results)
                for r in results:
                    self.port_table.add_row([
                        r.get("port", ""),
                        r.get("state", ""),
                        r.get("service", ""),
                        (r.get("banner") or "")[:80],
                    ])
                if scan_type == "port":
                    self._reset_ui()
                    self.tabs.setCurrentIndex(0)
                    self.status_label.setText(f"完成: {len(results)} 个开放端口")

            elif scan_type in ("web", "web_partial"):
                web_scanner = self.engine.get_module("web_scanner")
                web_scanner.save_findings(self._scan_target, results)
                sev_colors = {
                    "CRITICAL": "#c62828", "HIGH": "#e65100",
                    "MEDIUM": "#f57f17", "LOW": "#2e7d32",
                }
                for r in results:
                    sev = r.get("severity", "LOW")
                    self.vuln_table.add_row([
                        r.get("type", ""),
                        sev,
                        r.get("title", ""),
                        r.get("description", ""),
                        (r.get("evidence") or "")[:80],
                    ], row_color=sev_colors.get(sev))
                if scan_type == "web":
                    self._reset_ui()
                self.tabs.setCurrentIndex(1)
                self.status_label.setText(f"完成: {len(results)} 个漏洞")

            elif scan_type == "full_done":
                self._reset_ui()
                self.status_label.setText("全面扫描完成")
        except Exception as e:
            self._reset_ui()
            self.status_label.setText(f"处理结果时出错: {e}")

    def _on_error(self, msg):
        if not self.worker or self.worker.cancelled:
            return
        self._reset_ui()
        self.status_label.setText(f"错误: {msg}")
