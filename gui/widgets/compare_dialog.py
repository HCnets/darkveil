from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


def _diff_lists(old_items, new_items, key_fn):
    """Compare two lists of dicts, return (added, removed, unchanged)."""
    old_map = {key_fn(item): item for item in old_items}
    new_map = {key_fn(item): item for item in new_items}

    old_keys = set(old_map.keys())
    new_keys = set(new_map.keys())

    added = [new_map[k] for k in (new_keys - old_keys)]
    removed = [old_map[k] for k in (old_keys - new_keys)]
    unchanged = [new_map[k] for k in (old_keys & new_keys)]

    return added, removed, unchanged


class CompareDialog(QDialog):
    def __init__(self, db, target_id, target_host, parent=None):
        super().__init__(parent)
        self.db = db
        self.target_id = target_id
        self.target_host = target_host
        self.setWindowTitle(f"扫描对比 - {target_host}")
        self.setMinimumSize(900, 600)
        self._setup_ui()
        self._load_snapshots()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Snapshot selectors
        sel_frame = QFrame()
        sel_layout = QHBoxLayout(sel_frame)

        sel_layout.addWidget(QLabel("基线:"))
        self.combo_old = QComboBox()
        self.combo_old.setFixedWidth(220)
        sel_layout.addWidget(self.combo_old)

        sel_layout.addWidget(QLabel("对比:"))
        self.combo_new = QComboBox()
        self.combo_new.setFixedWidth(220)
        sel_layout.addWidget(self.combo_new)

        btn_compare = QPushButton("对比")
        btn_compare.setObjectName("primary")
        btn_compare.clicked.connect(self._compare)
        sel_layout.addWidget(btn_compare)
        sel_layout.addStretch()

        layout.addWidget(sel_frame)

        # Result tabs
        self.tabs = QTabWidget()

        self.port_table = self._make_table(["端口", "服务", "版本", "状态"])
        self.tabs.addTab(self.port_table, "端口变化")

        self.vuln_table = self._make_table(["严重程度", "类型", "标题", "状态"])
        self.tabs.addTab(self.vuln_table, "漏洞变化")

        layout.addWidget(self.tabs)

        # Summary
        self.summary = QLabel("")
        self.summary.setObjectName("subtitle")
        layout.addWidget(self.summary)

    def _make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        return table

    def _load_snapshots(self):
        snapshots = self.db.get_snapshots(self.target_id)
        if not snapshots:
            self.summary.setText("没有快照数据。请先在目标管理页面创建快照。")
            return

        for s in snapshots:
            label = s.get("label", s.get("snapshot_time", ""))
            sid = s.get("snapshot_id")
            self.combo_old.addItem(label, sid)
            self.combo_new.addItem(label, sid)

        if self.combo_new.count() > 1:
            self.combo_new.setCurrentIndex(0)
            self.combo_old.setCurrentIndex(1)

    def _compare(self):
        old_id = self.combo_old.currentData()
        new_id = self.combo_new.currentData()
        if old_id is None or new_id is None:
            self.summary.setText("请选择两个快照")
            return
        if old_id == new_id:
            self.summary.setText("请选择两个不同的快照")
            return

        snapshots = self.db.get_snapshots(self.target_id)
        snap_map = {s["snapshot_id"]: s for s in snapshots}
        old_snap = snap_map.get(old_id, {})
        new_snap = snap_map.get(new_id, {})

        old_ports = old_snap.get("ports", [])
        new_ports = new_snap.get("ports", [])
        old_vulns = old_snap.get("vulns", [])
        new_vulns = new_snap.get("vulns", [])

        # Port diff
        added_p, removed_p, unchanged_p = _diff_lists(
            old_ports, new_ports, lambda p: p.get("port")
        )
        self._fill_port_table(added_p, removed_p, unchanged_p)

        # Vuln diff
        added_v, removed_v, unchanged_v = _diff_lists(
            old_vulns, new_vulns, lambda v: v.get("title", "")
        )
        self._fill_vuln_table(added_v, removed_v, unchanged_v)

        self.summary.setText(
            f"端口: +{len(added_p)} 新增 / -{len(removed_p)} 消失 / {len(unchanged_p)} 不变 | "
            f"漏洞: +{len(added_v)} 新增 / -{len(removed_v)} 消失 / {len(unchanged_v)} 不变"
        )

    def _fill_port_table(self, added, removed, unchanged):
        rows = []
        for p in added:
            rows.append((p, "新增", "#2e7d32"))
        for p in removed:
            rows.append((p, "消失", "#c62828"))
        for p in unchanged:
            rows.append((p, "不变", "#666"))

        self.port_table.setRowCount(len(rows))
        for i, (p, status, color) in enumerate(rows):
            self.port_table.setItem(i, 0, self._item(str(p.get("port", "")), color))
            self.port_table.setItem(i, 1, self._item(p.get("service") or "-", color))
            self.port_table.setItem(i, 2, self._item(p.get("version") or "-", color))
            self.port_table.setItem(i, 3, self._item(status, color))

    def _fill_vuln_table(self, added, removed, unchanged):
        rows = []
        for v in added:
            rows.append((v, "新增", "#2e7d32"))
        for v in removed:
            rows.append((v, "消失", "#c62828"))
        for v in unchanged:
            rows.append((v, "不变", "#666"))

        self.vuln_table.setRowCount(len(rows))
        for i, (v, status, color) in enumerate(rows):
            self.vuln_table.setItem(i, 0, self._item(v.get("severity", ""), color))
            self.vuln_table.setItem(i, 1, self._item(v.get("vuln_type", ""), color))
            self.vuln_table.setItem(i, 2, self._item(v.get("title", ""), color))
            self.vuln_table.setItem(i, 3, self._item(status, color))

    def _item(self, text, color):
        item = QTableWidgetItem(text)
        item.setForeground(QColor(color))
        return item
