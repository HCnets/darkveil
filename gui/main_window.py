from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QStackedWidget, QSplitter,
    QComboBox, QGroupBox, QScrollArea, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from gui.widgets.dashboard import DashboardWidget
from gui.widgets.terminal_widget import TerminalWidget
from gui.pages.scanner_page import ScannerPage
from gui.pages.exploit_page import ExploitPage
from gui.pages.report_page import ReportPage
from gui.pages.target_page import TargetPage
from gui.pages.monitor_page import MonitorPage
from gui.pages.honeypot_page import HoneypotPage
from gui.pages.autopilot_page import AutoPilotPage
from gui.pages.tools_page import ToolsPage
from gui.widgets.global_search import GlobalSearchWidget
from modules.scanner.port_scanner import PortScanner
from modules.scanner.service_detector import ServiceDetector
from modules.scanner.web_scanner import WebScanner
from modules.exploit.manager import ExploitManager
import threading


NAV_ITEMS = [
    ("控制中心", "dashboard"),
    ("漏洞扫描", "scanner"),
    ("漏洞利用", "exploit"),
    ("渗透向导", "autopilot"),
    ("目标管理", "target"),
    ("实用工具", "tools"),
    ("流量监控", "monitor"),
    ("蜜罐系统", "honeypot"),
    ("安全报告", "report"),
    ("系统设置", "settings"),
]


class MainWindow(QMainWindow):
    def __init__(self, engine, config, logger, theme_engine=None):
        super().__init__()
        self.engine = engine
        self.config = config
        self.logger = logger
        self.theme_engine = theme_engine

        self.setWindowTitle("DarkVeil")
        self.setMinimumSize(1200, 800)
        self.resize(
            config.get("ui.window_width", 1400),
            config.get("ui.window_height", 900),
        )

        self._init_modules()
        self._setup_ui()
        self._connect_signals()

        self.logger.info("DarkVeil GUI 已启动")

    def _init_modules(self):
        port_scanner = PortScanner(self.config, self.engine.db, self.logger)
        self.engine.register_module("port_scanner", port_scanner)

        service_detector = ServiceDetector(self.config, self.logger)
        self.engine.register_module("service_detector", service_detector)

        web_scanner = WebScanner(self.config, self.engine.db, self.logger)
        self.engine.register_module("web_scanner", web_scanner)

        exploit_mgr = ExploitManager(self.config, self.engine.db, self.logger)
        exploit_mgr.discover()
        self.engine.register_module("exploit_manager", exploit_mgr)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_frame = QFrame()
        logo_frame.setObjectName("sidebar")
        logo_frame.setFixedHeight(56)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_title = QLabel("DarkVeil")
        logo_title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #ffffff; "
            "font-family: Consolas; background: transparent;"
        )
        logo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_title)
        sidebar_layout.addWidget(logo_frame)

        # Global search
        self.global_search = GlobalSearchWidget(self.engine)
        search_container = QFrame()
        search_container.setStyleSheet("background: transparent; padding: 4px 8px;")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(self.global_search)
        sidebar_layout.addWidget(search_container)

        sidebar_layout.addSpacing(4)

        self.nav_btn_group = []
        for text, page_id in NAV_ITEMS:
            btn = QPushButton(f"  {text}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setProperty("page_id", page_id)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            self.nav_btn_group.append(btn)

        sidebar_layout.addStretch()

        version_label = QLabel("  v0.1.0")
        version_label.setStyleSheet("color: #666; font-size: 11px; padding: 8px; background: transparent;")
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        content_splitter = QSplitter(Qt.Orientation.Vertical)

        self.pages = QStackedWidget()

        self.dashboard = DashboardWidget(self.engine)
        self.scanner_page = ScannerPage(self.engine)
        self.exploit_page = ExploitPage(self.engine)
        self.exploit_page.set_exploit_manager(self.engine.get_module("exploit_manager"))

        self.autopilot_page = AutoPilotPage(self.engine)
        self.target_page = TargetPage(self.engine)
        self.tools_page = ToolsPage(self.engine)
        self.monitor_page = MonitorPage(self.engine)
        self.honeypot_page = HoneypotPage(self.engine)
        self.report_page = ReportPage(self.engine)

        settings_page = self._build_settings_page()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.scanner_page)
        self.pages.addWidget(self.exploit_page)
        self.pages.addWidget(self.autopilot_page)
        self.pages.addWidget(self.target_page)
        self.pages.addWidget(self.tools_page)
        self.pages.addWidget(self.monitor_page)
        self.pages.addWidget(self.honeypot_page)
        self.pages.addWidget(self.report_page)
        self.pages.addWidget(settings_page)

        content_splitter.addWidget(self.pages)

        self.terminal = TerminalWidget()
        self.terminal.setFixedHeight(170)
        content_splitter.addWidget(self.terminal)

        content_splitter.setSizes([650, 170])
        main_layout.addWidget(content_splitter)

        self.nav_btn_group[0].setChecked(True)

    def _connect_signals(self):
        for btn in self.nav_btn_group:
            btn.clicked.connect(self._on_nav_clicked)

        self.logger.on_message(self.terminal.write_log)
        self.terminal.command_entered.connect(self._handle_command)

    def _on_nav_clicked(self):
        sender = self.sender()
        if not sender:
            return
        for btn in self.nav_btn_group:
            btn.setChecked(btn is sender)

        page_map = {item[1]: i for i, item in enumerate(NAV_ITEMS)}
        page_id = sender.property("page_id")
        if page_id in page_map:
            self.pages.setCurrentIndex(page_map[page_id])

        if page_id == "dashboard":
            self.dashboard.refresh()
        elif page_id == "exploit":
            try:
                self.exploit_page._refresh_modules()
            except Exception:
                pass
        elif page_id == "target":
            self.target_page._refresh()

    def _handle_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return

        command = parts[0].lower()

        try:
            if command == "help":
                self.terminal.write("可用命令:")
                self.terminal.write("  scan <target>       - 端口扫描")
                self.terminal.write("  web <target>        - Web 漏洞扫描")
                self.terminal.write("  exploit list        - 列出利用模块")
                self.terminal.write("  stats               - 显示统计信息")
                self.terminal.write("  targets             - 列出已扫描目标")
                self.terminal.write("  clear               - 清屏")
            elif command == "clear":
                self.terminal.clear()
            elif command == "stats":
                stats = self.engine.db.get_stats()
                self.terminal.write(
                    f"目标: {stats.get('targets', 0)}  端口: {stats.get('open_ports', 0)}  "
                    f"漏洞: {stats.get('vulnerabilities', 0)}  利用: {stats.get('exploits', 0)}"
                )
            elif command == "targets":
                targets = self.engine.db.get_targets()
                if targets:
                    for t in targets:
                        host = t.get('host', '?')
                        ip = t.get('ip') or '-'
                        last = t.get('last_seen') or '-'
                        self.terminal.write(f"  {host} ({ip}) - {last}")
                else:
                    self.terminal.write("暂无目标记录")
            elif command == "exploit" and len(parts) > 1 and parts[1] == "list":
                mgr = self.engine.get_module("exploit_manager")
                if mgr:
                    for info in mgr.list_exploits():
                        self.terminal.write(f"  {info['name']} [{info['severity']}] - {info['description']}")
            elif command == "scan" and len(parts) > 1:
                target = parts[1]
                self.terminal.write(f"开始扫描: {target}", "#0078d4")
                scanner = self.engine.get_module("port_scanner")
                if scanner:
                    def run_scan():
                        try:
                            result = scanner.scan(target)
                            if result:
                                self.terminal.write(f"扫描完成: {len(result)} 个开放端口", "#2e7d32")
                            else:
                                self.terminal.write("扫描完成: 无开放端口")
                        except Exception as e:
                            self.terminal.write(f"扫描失败: {e}", "#c62828")
                    threading.Thread(target=run_scan, daemon=True).start()
            elif command == "web" and len(parts) > 1:
                target = parts[1]
                self.terminal.write(f"开始 Web 扫描: {target}", "#0078d4")
                scanner = self.engine.get_module("web_scanner")
                if scanner:
                    def run_web():
                        try:
                            result = scanner.scan(target)
                            if result:
                                self.terminal.write(f"Web 扫描完成: {len(result)} 个发现", "#2e7d32")
                            else:
                                self.terminal.write("Web 扫描完成: 无发现")
                        except Exception as e:
                            self.terminal.write(f"Web 扫描失败: {e}", "#c62828")
                    threading.Thread(target=run_web, daemon=True).start()
            else:
                self.terminal.write(f"未知命令: {command} (输入 help 查看帮助)", "#c62828")
        except Exception as e:
            self.terminal.write(f"命令执行出错: {e}", "#c62828")

    def _build_settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("系统设置")
        title.setObjectName("title")
        layout.addWidget(title)

        # 主题设置
        theme_group = QGroupBox("界面主题")
        theme_layout = QVBoxLayout(theme_group)

        theme_row = QHBoxLayout()
        theme_label = QLabel("当前主题:")
        theme_label.setFixedWidth(80)
        self.theme_combo = QComboBox()
        self.theme_combo.setFixedWidth(280)

        if self.theme_engine:
            for info in self.theme_engine.list_themes():
                self.theme_combo.addItem(info["display_name"], info["name"])
            current = self.theme_engine.current
            if current:
                idx = self.theme_combo.findData(current.name)
                if idx >= 0:
                    self.theme_combo.setCurrentIndex(idx)

        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        theme_layout.addLayout(theme_row)

        self.theme_desc = QLabel()
        self.theme_desc.setObjectName("subtitle")
        self.theme_desc.setWordWrap(True)
        self._update_theme_desc()
        theme_layout.addWidget(self.theme_desc)

        layout.addWidget(theme_group)

        # 代理设置
        proxy_group = QGroupBox("网络代理")
        proxy_layout = QVBoxLayout(proxy_group)

        proxy_enable_row = QHBoxLayout()
        self.proxy_enable = QCheckBox("启用代理")
        self.proxy_enable.setChecked(self.config.get("proxy.enabled", False))
        self.proxy_enable.toggled.connect(self._on_proxy_changed)
        proxy_enable_row.addWidget(self.proxy_enable)
        proxy_enable_row.addStretch()
        proxy_layout.addLayout(proxy_enable_row)

        for label, key in [("HTTP:", "http"), ("HTTPS:", "https"), ("SOCKS5:", "socks5")]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(60)
            input_field = QLineEdit(self.config.get(f"proxy.{key}", ""))
            input_field.setPlaceholderText("host:port")
            input_field.setObjectName(f"proxy_{key}")
            input_field.textChanged.connect(lambda text, k=key: self._on_proxy_field_changed(k, text))
            row.addWidget(lbl)
            row.addWidget(input_field)
            proxy_layout.addLayout(row)

        layout.addWidget(proxy_group)

        # 关于
        about_group = QGroupBox("关于")
        about_layout = QVBoxLayout(about_group)
        about_layout.addWidget(QLabel("DarkVeil - 攻防一体安全平台"))
        about_layout.addWidget(QLabel("版本: 0.1.0"))
        about_layout.addWidget(QLabel("技术栈: Python + PyQt6"))
        layout.addWidget(about_group)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _update_theme_desc(self):
        if not self.theme_engine:
            return
        name = self.theme_combo.currentData()
        theme = self.theme_engine.get(name)
        if theme:
            self.theme_desc.setText(theme.description)

    def _on_theme_changed(self, index):
        if not self.theme_engine:
            return
        name = self.theme_combo.currentData()
        if not name:
            return
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and self.theme_engine.apply(name, app):
            self.config.set("ui.theme", name)
            self._update_theme_desc()
            self.logger.info(f"主题已切换: {self.theme_combo.currentText()}")

    def _on_proxy_changed(self, checked):
        self.config.set("proxy.enabled", checked)
        self.logger.info(f"代理{'已启用' if checked else '已禁用'}")

    def _on_proxy_field_changed(self, key, text):
        self.config.set(f"proxy.{key}", text.strip())

    def closeEvent(self, event):
        try:
            self.config.set("ui.window_width", self.width())
            self.config.set("ui.window_height", self.height())
        except Exception:
            pass
        try:
            self.logger.remove_callback(self.terminal.write_log)
        except Exception:
            pass
        super().closeEvent(event)
