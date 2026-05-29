from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QTabWidget, QGroupBox, QSpinBox, QComboBox,
    QFormLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from gui.widgets.result_table import ResultTable


class IntelWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, client, method, args):
        super().__init__()
        self.client = client
        self.method = method
        self.args = args

    def run(self):
        try:
            fn = getattr(self.client, self.method)
            result = fn(**self.args)
            self.finished.emit(result if isinstance(result, dict) else {"data": result})
        except Exception as e:
            self.error.emit(str(e))


class NvdTab(QWidget):
    def __init__(self, config, db, logger):
        super().__init__()
        self._client = None
        self._worker = None
        self._config = config
        self._db = db
        self._logger = logger
        self._setup_ui()

    def _get_client(self):
        if self._client is None:
            from modules.intel.nvd_client import NVDClient
            self._client = NVDClient(self._config, self._db, self._logger)
        return self._client

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入关键词 / CVE-ID / CPE 进行查询...")
        input_layout.addWidget(self.query_input)

        self.query_type = QComboBox()
        self.query_type.addItems(["关键词", "CVE-ID", "CPE"])
        self.query_type.setFixedWidth(100)
        input_layout.addWidget(self.query_type)

        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(20)
        self.max_spin.setFixedWidth(70)
        input_layout.addWidget(QLabel("数量:"))
        input_layout.addWidget(self.max_spin)

        self.btn_search = QPushButton("查询")
        self.btn_search.clicked.connect(self._do_search)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(input_frame)

        self.result_table = ResultTable(["CVE ID", "严重程度", "CVSS", "描述", "发布日期"])
        self.result_table.set_column_widths([130, 80, 60, 350, 100])
        layout.addWidget(self.result_table)

        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

    def _do_search(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_label.setText("请输入查询内容")
            return

        self.btn_search.setEnabled(False)
        self.status_label.setText("查询中...")
        self.result_table.clear_data()

        qtype = self.query_type.currentText()
        client = self._get_client()
        max_r = self.max_spin.value()

        if qtype == "CVE-ID":
            method, args = "query_by_cve_id", {"cve_id": query}
        elif qtype == "CPE":
            method, args = "query_by_cpe", {"cpe_string": query, "max_results": max_r}
        else:
            method, args = "query", {"keyword": query, "max_results": max_r}

        self._worker = IntelWorker(client, method, args)
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, data):
        self.btn_search.setEnabled(True)
        vulns = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(vulns, dict):
            vulns = vulns.get("vulns", vulns.get("results", []))
        if not isinstance(vulns, list):
            self.status_label.setText("无结果")
            return

        self.result_table.clear_data()
        for v in vulns:
            if isinstance(v, dict):
                self.result_table.add_row([
                    v.get("cve_id", ""),
                    v.get("severity", ""),
                    str(v.get("cvss_score", "")),
                    v.get("description", "")[:100],
                    v.get("published", ""),
                ])
        self.status_label.setText(f"共 {len(vulns)} 条结果")

    def _on_error(self, msg):
        self.btn_search.setEnabled(True)
        self.status_label.setText(f"查询失败: {msg}")


class ShodanTab(QWidget):
    def __init__(self, config, db, logger):
        super().__init__()
        self._client = None
        self._worker = None
        self._config = config
        self._db = db
        self._logger = logger
        self._setup_ui()

    def _get_client(self):
        if self._client is None:
            from modules.intel.shodan_client import ShodanClient
            self._client = ShodanClient(self._config, self._db, self._logger)
        return self._client

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入 IP 或搜索查询 (如 port:22 country:CN)...")
        input_layout.addWidget(self.query_input)

        self.query_type = QComboBox()
        self.query_type.addItems(["主机查询", "搜索"])
        self.query_type.setFixedWidth(100)
        input_layout.addWidget(self.query_type)

        self.btn_search = QPushButton("查询")
        self.btn_search.clicked.connect(self._do_search)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(input_frame)

        self.result_table = ResultTable(["IP", "端口", "组织", "产品", "版本", "国家", "Banner"])
        self.result_table.set_column_widths([120, 60, 130, 100, 80, 60, 200])
        layout.addWidget(self.result_table)

        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

    def _do_search(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_label.setText("请输入查询内容")
            return

        self.btn_search.setEnabled(False)
        self.status_label.setText("查询中...")
        self.result_table.clear_data()

        client = self._get_client()
        qtype = self.query_type.currentText()

        if qtype == "主机查询":
            method, args = "host_lookup", {"ip": query}
        else:
            method, args = "search", {"query": query}

        self._worker = IntelWorker(client, method, args)
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, data):
        self.btn_search.setEnabled(True)
        if "error" in data:
            self.status_label.setText(f"查询失败: {data['error']}")
            return

        self.result_table.clear_data()
        banners = data.get("banners", [])
        if banners:
            for b in banners:
                self.result_table.add_row([
                    data.get("ip", ""),
                    str(b.get("port", "")),
                    data.get("org", ""),
                    b.get("product", ""),
                    b.get("version", ""),
                    data.get("country", ""),
                    (b.get("banner", "") or "")[:80],
                ])
            info_parts = [f"IP: {data.get('ip', '')}", f"OS: {data.get('os', '')}"]
            if data.get("vulns"):
                info_parts.append(f"漏洞: {len(data['vulns'])} 个")
            self.status_label.setText(" | ".join(info_parts))
        else:
            results = data.get("data", data) if isinstance(data, dict) else []
            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        self.result_table.add_row([
                            r.get("ip", ""),
                            str(r.get("port", "")),
                            r.get("org", ""),
                            r.get("product", ""),
                            r.get("version", ""),
                            r.get("country", ""),
                            (r.get("banner", "") or "")[:80],
                        ])
                self.status_label.setText(f"共 {len(results)} 条结果")
            else:
                self.status_label.setText("无结果")

    def _on_error(self, msg):
        self.btn_search.setEnabled(True)
        self.status_label.setText(f"查询失败: {msg}")


class FofaTab(QWidget):
    def __init__(self, config, db, logger):
        super().__init__()
        self._client = None
        self._worker = None
        self._config = config
        self._db = db
        self._logger = logger
        self._setup_ui()

    def _get_client(self):
        if self._client is None:
            from modules.intel.fofa_client import FofaClient
            self._client = FofaClient(self._config, self._db, self._logger)
        return self._client

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("输入 Fofa 查询语法 (如 title=\"login\" && country=\"CN\")...")
        input_layout.addWidget(self.query_input)

        self.query_type = QComboBox()
        self.query_type.addItems(["搜索", "主机信息"])
        self.query_type.setFixedWidth(100)
        input_layout.addWidget(self.query_type)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 500)
        self.size_spin.setValue(100)
        self.size_spin.setFixedWidth(70)
        input_layout.addWidget(QLabel("数量:"))
        input_layout.addWidget(self.size_spin)

        self.btn_search = QPushButton("查询")
        self.btn_search.clicked.connect(self._do_search)
        input_layout.addWidget(self.btn_search)

        layout.addWidget(input_frame)

        self.result_table = ResultTable(["IP", "端口", "主机", "标题", "Server"])
        self.result_table.set_column_widths([130, 60, 180, 200, 150])
        layout.addWidget(self.result_table)

        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

    def _do_search(self):
        query = self.query_input.text().strip()
        if not query:
            self.status_label.setText("请输入查询内容")
            return

        self.btn_search.setEnabled(False)
        self.status_label.setText("查询中...")
        self.result_table.clear_data()

        client = self._get_client()
        qtype = self.query_type.currentText()

        if qtype == "主机信息":
            method, args = "host_info", {"ip": query}
        else:
            method, args = "search", {"query": query, "size": self.size_spin.value()}

        self._worker = IntelWorker(client, method, args)
        self._worker.finished.connect(self._on_result)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_result(self, data):
        self.btn_search.setEnabled(True)
        if "error" in data:
            self.status_label.setText(f"查询失败: {data['error']}")
            return

        self.result_table.clear_data()
        results = data.get("results", [])
        for r in results:
            self.result_table.add_row([
                r.get("ip", ""),
                str(r.get("port", "")),
                r.get("host", ""),
                r.get("title", ""),
                r.get("server", ""),
            ])
        total = data.get("total", len(results))
        self.status_label.setText(f"共 {total} 条结果 (显示 {len(results)} 条)")

    def _on_error(self, msg):
        self.btn_search.setEnabled(True)
        self.status_label.setText(f"查询失败: {msg}")


class IntelPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("情报中心")
        title.setObjectName("title")
        layout.addWidget(title)

        tabs = QTabWidget()

        config = self.engine.config if hasattr(self.engine, 'config') else None
        db = self.engine.db if hasattr(self.engine, 'db') else None
        logger = self.engine.logger if hasattr(self.engine, 'logger') else None

        tabs.addTab(NvdTab(config, db, logger), "NVD 漏洞库")
        tabs.addTab(ShodanTab(config, db, logger), "Shodan")
        tabs.addTab(FofaTab(config, db, logger), "Fofa")

        layout.addWidget(tabs)
