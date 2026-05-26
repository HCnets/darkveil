from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QProgressBar,
    QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from modules.autopilot import AutoPilot, STAGE_NAMES


class AutoPilotWorker(QThread):
    stage_signal = pyqtSignal(int, str, int)  # stage_idx, message, progress_pct
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, autopilot, target, options):
        super().__init__()
        self.autopilot = autopilot
        self.target = target
        self.options = options

    def run(self):
        try:
            results = self.autopilot.run(self.target, self.options, self._on_callback)
            self.finished_signal.emit(results)
        except Exception as e:
            self.error_signal.emit(str(e))

    def _on_callback(self, stage_idx, message, progress_pct):
        self.stage_signal.emit(stage_idx, message, progress_pct)


class AutoPilotPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.worker = None
        self.autopilot = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("渗透向导")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("自动化攻击链：扫描 → 识别 → 漏洞检测 → 利用")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Config panel
        config_frame = QFrame()
        config_frame.setObjectName("panel")
        config_layout = QVBoxLayout(config_frame)
        config_layout.setSpacing(10)

        # Row 1: target + port
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("目标:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("输入 IP 或域名")
        row1.addWidget(self.target_input, 2)

        row1.addWidget(QLabel("端口:"))
        self.port_input = QLineEdit("80,443,22,21,3306,3389,8080")
        self.port_input.setPlaceholderText("自定义端口")
        self.port_input.setFixedWidth(220)
        row1.addWidget(self.port_input, 1)
        config_layout.addLayout(row1)

        # Row 2: mode + options
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("扫描模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.setFixedWidth(160)
        self.mode_combo.addItem("快速扫描", "fast")
        self.mode_combo.addItem("全端口扫描", "full")
        self.mode_combo.addItem("自定义端口", "custom")
        row2.addWidget(self.mode_combo)

        self.auto_exploit_check = QCheckBox("自动利用（确认漏洞后自动执行）")
        self.auto_exploit_check.setChecked(False)
        row2.addWidget(self.auto_exploit_check)

        row2.addStretch()

        self.btn_start = QPushButton("开始攻击")
        self.btn_start.setObjectName("danger")
        self.btn_start.setFixedWidth(120)
        self.btn_start.clicked.connect(self._start)
        row2.addWidget(self.btn_start)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setFixedWidth(80)
        self.btn_stop.clicked.connect(self._stop)
        row2.addWidget(self.btn_stop)

        config_layout.addLayout(row2)
        layout.addWidget(config_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Stage indicators
        stage_frame = QFrame()
        stage_layout = QHBoxLayout(stage_frame)
        stage_layout.setContentsMargins(0, 0, 0, 0)
        stage_layout.setSpacing(4)
        self.stage_labels = []
        for i, name in enumerate(STAGE_NAMES):
            lbl = QLabel(f"{i+1}. {name}")
            lbl.setObjectName("subtitle")
            lbl.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            stage_layout.addWidget(lbl)
            self.stage_labels.append(lbl)
        layout.addWidget(stage_frame)

        # Log output
        log_group = QGroupBox("执行日志")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setObjectName("terminal")
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

        # Result summary
        self.result_label = QLabel("")
        self.result_label.setObjectName("subtitle")
        layout.addWidget(self.result_label)

    def _start(self):
        target = self.target_input.text().strip()
        if not target:
            self.result_label.setText("请输入目标")
            return

        self.autopilot = AutoPilot(self.engine, self.engine.logger)

        mode = self.mode_combo.currentData()
        options = {
            "scan_mode": mode,
            "custom_ports": self.port_input.text().strip(),
            "auto_exploit": self.auto_exploit_check.isChecked(),
        }

        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.result_label.setText("")
        self._reset_stage_labels()

        self.worker = AutoPilotWorker(self.autopilot, target, options)
        self.worker.stage_signal.connect(self._on_stage)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

    def _stop(self):
        if self.autopilot:
            self.autopilot.stop()
        self.log_text.append("\n[!] 用户中止攻击链")

    def _on_stage(self, stage_idx, message, progress_pct):
        self.log_text.append(message)

        if progress_pct >= 0:
            self.progress_bar.setValue(progress_pct)
            # Highlight current stage
            for i, lbl in enumerate(self.stage_labels):
                if i == stage_idx:
                    lbl.setStyleSheet(
                        "padding: 4px 8px; font-size: 11px; "
                        "font-weight: bold; color: #0078d4;"
                    )
                elif i < stage_idx:
                    lbl.setStyleSheet(
                        "padding: 4px 8px; font-size: 11px; "
                        "color: #2e7d32;"
                    )

    def _on_finished(self, results):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)

        # Mark all stages complete
        for lbl in self.stage_labels:
            lbl.setStyleSheet(
                "padding: 4px 8px; font-size: 11px; color: #2e7d32;"
            )

        # Summary
        ports = len(results.get("open_ports", []))
        vulns = len(results.get("web_vulns", []))
        checks = results.get("check_results", [])
        vuln_count = sum(1 for c in checks if c.get("status") in ("vulnerable", "success"))
        exploits = len(results.get("exploit_results", []))
        report = results.get("report_path", "")

        summary = f"扫描完成 | 端口: {ports} | Web漏洞: {vulns} | 可利用: {vuln_count}"
        if exploits:
            summary += f" | 已利用: {exploits}"
        if report:
            summary += f" | 报告: {report}"

        self.result_label.setText(summary)
        self.log_text.append(f"\n{'='*50}")
        self.log_text.append(summary)

    def _on_error(self, text):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.result_label.setText(f"错误: {text}")
        self.log_text.append(f"\n[错误] {text}")

    def _reset_stage_labels(self):
        for lbl in self.stage_labels:
            lbl.setStyleSheet("padding: 4px 8px; font-size: 11px;")
