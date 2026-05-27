from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSplitter, QGroupBox, QTextEdit, QMessageBox,
    QInputDialog, QDialog
)
from PyQt6.QtCore import Qt
from gui.widgets.result_table import ResultTable


SEVERITY_COLORS = {
    "CRITICAL": "#c62828",
    "HIGH": "#e65100",
    "MEDIUM": "#f9a825",
    "LOW": "#666",
}


class TargetPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("目标管理")
        title.setObjectName("title")
        layout.addWidget(title)

        # 操作栏
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.setObjectName("primary")
        self.btn_refresh.clicked.connect(self._refresh)
        btn_layout.addWidget(self.btn_refresh)

        self.btn_cve = QPushButton("CVE 匹配扫描")
        self.btn_cve.clicked.connect(self._cve_scan)
        btn_layout.addWidget(self.btn_cve)

        self.btn_add = QPushButton("添加目标")
        self.btn_add.clicked.connect(self._add_target)
        btn_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("删除目标")
        self.btn_delete.clicked.connect(self._delete_target)
        btn_layout.addWidget(self.btn_delete)

        self.btn_snapshot = QPushButton("创建快照")
        self.btn_snapshot.clicked.connect(self._create_snapshot)
        btn_layout.addWidget(self.btn_snapshot)

        self.btn_compare = QPushButton("对比扫描")
        self.btn_compare.clicked.connect(self._compare_scans)
        btn_layout.addWidget(self.btn_compare)

        btn_layout.addStretch()
        self.count_label = QLabel("")
        self.count_label.setObjectName("subtitle")
        btn_layout.addWidget(self.count_label)

        layout.addWidget(btn_frame)

        # 主内容区
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 上部：目标列表
        top_frame = QFrame()
        top_frame.setObjectName("panel")
        top_layout = QVBoxLayout(top_frame)

        top_layout.addWidget(QLabel("目标列表"))
        self.target_table = ResultTable(["ID", "主机", "IP", "首次发现", "最后活动"])
        self.target_table.set_column_widths([50, 200, 140, 160, 160])
        self.target_table.currentCellChanged.connect(self._on_target_selected)
        top_layout.addWidget(self.target_table)

        splitter.addWidget(top_frame)

        # 下部：详情区
        bottom_frame = QFrame()
        bottom_frame.setObjectName("panel")
        bottom_layout = QHBoxLayout(bottom_frame)

        # 左侧：端口
        port_group = QGroupBox("开放端口")
        port_layout = QVBoxLayout(port_group)
        self.port_table = ResultTable(["端口", "状态", "服务", "版本"])
        self.port_table.set_column_widths([80, 80, 150, 200])
        port_layout.addWidget(self.port_table)
        bottom_layout.addWidget(port_group)

        # 右侧：漏洞
        vuln_group = QGroupBox("漏洞（双击查看详情）")
        vuln_layout = QVBoxLayout(vuln_group)
        self.vuln_table = ResultTable(["严重程度", "类型", "标题", "描述"])
        self.vuln_table.set_column_widths([90, 100, 180, 250])
        self.vuln_table.cellDoubleClicked.connect(self._show_vuln_detail)
        vuln_layout.addWidget(self.vuln_table)
        bottom_layout.addWidget(vuln_group)

        splitter.addWidget(bottom_frame)
        splitter.setSizes([300, 300])

        layout.addWidget(splitter)

        # Notes section
        notes_frame = QFrame()
        notes_frame.setObjectName("panel")
        notes_layout = QHBoxLayout(notes_frame)
        notes_layout.setContentsMargins(8, 8, 8, 8)
        notes_layout.setSpacing(8)

        notes_layout.addWidget(QLabel("备注:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText("选择目标后可编辑备注...")
        notes_layout.addWidget(self.notes_edit, 1)

        self.btn_save_notes = QPushButton("保存备注")
        self.btn_save_notes.clicked.connect(self._save_notes)
        notes_layout.addWidget(self.btn_save_notes)

        layout.addWidget(notes_frame)

    def _refresh(self):
        db = self.engine.db
        if not db:
            return

        self.target_table.clear_data()
        self.port_table.clear_data()
        self.vuln_table.clear_data()

        targets = db.get_targets()
        for t in targets:
            self.target_table.add_row([
                str(t.get("id", "")),
                t.get("host", ""),
                t.get("ip") or "-",
                t.get("first_seen", "-"),
                t.get("last_seen", "-"),
            ])

        self.count_label.setText(f"{len(targets)} 个目标")

    def _on_target_selected(self, row, col, prev_row, prev_col):
        if row < 0:
            return
        item = self.target_table.item(row, 0)
        if not item:
            return
        try:
            tid = int(item.text())
        except (ValueError, TypeError):
            return

        db = self.engine.db
        if not db:
            return

        self._current_target_id = tid

        # 加载端口
        self.port_table.clear_data()
        ports = db.get_ports(tid)
        for p in ports:
            self.port_table.add_row([
                str(p.get("port", "")),
                p.get("state", ""),
                p.get("service") or "-",
                p.get("version") or "-",
            ])

        # 加载漏洞
        self.vuln_table.clear_data()
        self._vuln_data = []
        vulns = db.get_vulnerabilities(tid)
        for v in vulns:
            sev = v.get("severity", "")
            color = SEVERITY_COLORS.get(sev)
            self.vuln_table.add_row([
                sev,
                v.get("vuln_type", ""),
                v.get("title", ""),
                (v.get("description") or "-")[:80],
            ], row_color=color)
            self._vuln_data.append(v)

        # 加载备注
        targets = db.get_targets()
        for t in targets:
            if t.get("id") == tid:
                self.notes_edit.setPlainText(t.get("notes") or "")
                break

    def _cve_scan(self):
        db = self.engine.db
        if not db:
            QMessageBox.warning(self, "错误", "数据库未初始化")
            return

        from modules.cve_matcher import CVEMatcher
        matcher = CVEMatcher(db, self.engine.logger)

        targets = db.get_targets()
        if not targets:
            QMessageBox.information(self, "CVE 匹配", "没有目标数据，请先进行扫描。")
            return

        self.btn_cve.setEnabled(False)
        self.count_label.setText("正在匹配 CVE...")

        try:
            findings = matcher.scan_targets(targets)
            count = len(findings)
            self.count_label.setText(f"CVE 匹配完成: {count} 个发现")

            if count > 0:
                QMessageBox.information(
                    self, "CVE 匹配完成",
                    f"发现 {count} 个已知漏洞，已写入数据库。\n请刷新查看。"
                )
            else:
                QMessageBox.information(
                    self, "CVE 匹配完成",
                    "未发现已知 CVE。\n（需要目标端口有服务版本信息才能匹配）"
                )
            self._refresh()
        except Exception as e:
            QMessageBox.critical(self, "CVE 扫描失败", str(e))
            self.count_label.setText(f"CVE 扫描失败: {e}")
        finally:
            self.btn_cve.setEnabled(True)

    def _add_target(self):
        host, ok = QInputDialog.getText(self, "添加目标", "主机名或 IP:")
        if not ok or not host.strip():
            return
        host = host.strip()

        db = self.engine.db
        if not db:
            return

        ip, ok2 = QInputDialog.getText(self, "添加目标", "IP 地址（可选）:")
        ip = ip.strip() if ok2 and ip.strip() else None

        tid = db.get_or_create_target(host, ip)
        if tid:
            self.count_label.setText(f"已添加: {host}")
            self._refresh()
        else:
            self.count_label.setText("添加失败")

    def _delete_target(self):
        row = self.target_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "删除目标", "请先选择一个目标")
            return

        item = self.target_table.item(row, 1)
        if not item:
            return
        host = item.text()

        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除目标 {host} 及其所有关联数据？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        id_item = self.target_table.item(row, 0)
        if not id_item:
            return
        try:
            tid = int(id_item.text())
        except (ValueError, TypeError):
            return

        db = self.engine.db
        if not db:
            return

        try:
            db.delete_target(tid)
            self.count_label.setText(f"已删除: {host}")
            self._refresh()
        except Exception as e:
            self.count_label.setText(f"删除失败: {e}")

    def _create_snapshot(self):
        row = self.target_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "创建快照", "请先选择一个目标")
            return

        id_item = self.target_table.item(row, 0)
        host_item = self.target_table.item(row, 1)
        if not id_item:
            return
        try:
            tid = int(id_item.text())
        except (ValueError, TypeError):
            return
        host = host_item.text() if host_item else ""

        db = self.engine.db
        if not db:
            return

        snap_id = db.save_snapshot(tid)
        if snap_id:
            self.count_label.setText(f"快照已创建: {host}")
        else:
            self.count_label.setText("快照创建失败")

    def _compare_scans(self):
        row = self.target_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "对比扫描", "请先选择一个目标")
            return

        id_item = self.target_table.item(row, 0)
        host_item = self.target_table.item(row, 1)
        if not id_item:
            return
        try:
            tid = int(id_item.text())
        except (ValueError, TypeError):
            return
        host = host_item.text() if host_item else ""

        from gui.widgets.compare_dialog import CompareDialog
        dlg = CompareDialog(self.engine.db, tid, host, self)
        dlg.exec()

    def _save_notes(self):
        tid = getattr(self, '_current_target_id', None)
        if not tid:
            QMessageBox.information(self, "保存备注", "请先选择一个目标")
            return
        notes = self.notes_edit.toPlainText()
        self.engine.db.update_notes(tid, notes)
        self.count_label.setText("备注已保存")

    def _show_vuln_detail(self, row, col):
        vuln_data = getattr(self, '_vuln_data', [])
        if row < 0 or row >= len(vuln_data):
            return
        v = vuln_data[row]

        dlg = QDialog(self)
        dlg.setWindowTitle(f"漏洞详情 — {v.get('title', '')}")
        dlg.setMinimumSize(500, 400)
        dlg_layout = QVBoxLayout(dlg)

        sev = v.get("severity", "")
        sev_label = QLabel(f"[{sev}]")
        sev_label.setStyleSheet(f"color: {SEVERITY_COLORS.get(sev, '#666')}; font-weight: bold; font-size: 16px;")
        dlg_layout.addWidget(sev_label)

        title_label = QLabel(v.get("title", ""))
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        dlg_layout.addWidget(title_label)

        for field, label in [
            ("vuln_type", "类型"), ("description", "描述"),
            ("evidence", "证据"), ("recommendation", "修复建议"),
        ]:
            val = v.get(field, "")
            if val:
                lbl = QLabel(f"<b>{label}:</b><br>{val}")
                lbl.setWordWrap(True)
                lbl.setTextFormat(Qt.TextFormat.RichText)
                dlg_layout.addWidget(lbl)

        btn = QPushButton("关闭")
        btn.clicked.connect(dlg.accept)
        dlg_layout.addWidget(btn)

        dlg.exec()
