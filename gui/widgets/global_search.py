from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, QTimer


class SearchResultItem(QFrame):
    def __init__(self, category, title, detail, parent=None):
        super().__init__(parent)
        self.setObjectName("activity_item")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        cat_label = QLabel(category)
        cat_label.setFixedWidth(60)
        cat_label.setStyleSheet(
            "font-size: 11px; font-weight: bold; "
            "color: #0078d4; background: transparent;"
        )
        layout.addWidget(cat_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600; background: transparent;")
        layout.addWidget(title_label, 2)

        detail_label = QLabel(detail)
        detail_label.setObjectName("subtitle")
        detail_label.setStyleSheet("font-size: 11px; background: transparent;")
        layout.addWidget(detail_label, 3)


class GlobalSearchWidget(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._do_search)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("全局搜索目标/端口/漏洞...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.search_input)

        self.result_scroll = QScrollArea()
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.result_scroll.setVisible(False)

        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(2)
        self.result_layout.addStretch()
        self.result_scroll.setWidget(self.result_container)

        layout.addWidget(self.result_scroll)

        self.count_label = QLabel("")
        self.count_label.setObjectName("subtitle")
        self.count_label.setStyleSheet("font-size: 10px; background: transparent;")
        layout.addWidget(self.count_label)

    def _on_text_changed(self, text):
        self._timer.start()

    def _do_search(self):
        query = self.search_input.text().strip().lower()
        if len(query) < 2:
            self.result_scroll.setVisible(False)
            self.count_label.setText("")
            return

        db = self.engine.db
        if not db:
            return

        results = []

        # Search targets
        targets = db.get_targets()
        for t in targets:
            host = (t.get("host") or "").lower()
            ip = (t.get("ip") or "").lower()
            if query in host or query in ip:
                results.append((
                    "目标",
                    t.get("host", ""),
                    f"IP: {t.get('ip') or '-'} | 最后活动: {t.get('last_seen', '-')}",
                ))

        # Search ports
        for t in targets:
            ports = db.get_ports(t["id"])
            for p in ports:
                service = (p.get("service") or "").lower()
                version = (p.get("version") or "").lower()
                port_str = str(p.get("port", ""))
                if query in service or query in version or query == port_str:
                    results.append((
                        "端口",
                        f"{t.get('host', '')}:{p['port']}",
                        f"{p.get('service') or '-'} {p.get('version') or ''}",
                    ))

        # Search vulnerabilities
        vulns = db.get_vulnerabilities()
        for v in vulns:
            title = (v.get("title") or "").lower()
            desc = (v.get("description") or "").lower()
            vtype = (v.get("vuln_type") or "").lower()
            if query in title or query in desc or query in vtype:
                target_name = ""
                for t in targets:
                    if t["id"] == v.get("target_id"):
                        target_name = t.get("host", "")
                        break
                results.append((
                    "漏洞",
                    f"[{v.get('severity')}] {v.get('title', '')}",
                    f"目标: {target_name} | 类型: {v.get('vuln_type', '')}",
                ))

        # Update UI
        while self.result_layout.count() > 1:
            child = self.result_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for cat, title, detail in results[:30]:
            item = SearchResultItem(cat, title, detail)
            self.result_layout.insertWidget(self.result_layout.count() - 1, item)

        self.result_scroll.setVisible(len(results) > 0)
        self.count_label.setText(f"{len(results)} 个结果" if results else "无匹配结果")
