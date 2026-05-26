from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
import pyqtgraph as pg
from pyqtgraph import PlotWidget, BarGraphItem, PlotDataItem
import numpy as np


SEVERITY_COLORS = {
    "CRITICAL": "#c62828",
    "HIGH": "#e65100",
    "MEDIUM": "#f57f17",
    "LOW": "#888",
}

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


class StatCard(QFrame):
    def __init__(self, title, value="0", color="#0078d4", parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self._accent = color
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
        self.title_label = QLabel(title)
        self.title_label.setObjectName("stat_label")

        layout.addWidget(self.value_label)
        layout.addWidget(self.title_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class ActivityItem(QFrame):
    def __init__(self, time_str, action, target, parent=None):
        super().__init__(parent)
        self.setObjectName("activity_item")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        safe_time = str(time_str or "")[:16]
        safe_action = str(action or "")
        safe_target = str(target or "")

        time_label = QLabel(safe_time)
        time_label.setObjectName("activity_time")
        time_label.setFixedWidth(130)

        action_label = QLabel(safe_action)
        action_label.setObjectName("activity_action")
        action_label.setFixedWidth(100)

        target_label = QLabel(safe_target)
        target_label.setObjectName("activity_target")

        layout.addWidget(time_label)
        layout.addWidget(action_label)
        layout.addWidget(target_label)
        layout.addStretch()


class DashboardWidget(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._last_activity_ids = set()
        self._setup_ui()

        # Auto-refresh timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(15000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        # Header with scan status indicator
        header = QHBoxLayout()
        header.setSpacing(8)
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("DarkVeil 控制中心")
        title.setObjectName("title")
        subtitle = QLabel("攻防一体安全平台")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col)
        header.addStretch()

        self.scan_indicator = QLabel("  空闲")
        self.scan_indicator.setObjectName("stat_label")
        self.scan_indicator.setStyleSheet("color: #888; font-size: 11px;")
        header.addWidget(self.scan_indicator)

        layout.addLayout(header)

        # Stat cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.card_targets = StatCard("扫描目标", "0", "#0078d4")
        self.card_ports = StatCard("开放端口", "0", "#2e7d32")
        self.card_vulns = StatCard("漏洞发现", "0", "#f57f17")
        self.card_exploits = StatCard("利用尝试", "0", "#c62828")

        for card in (self.card_targets, self.card_ports, self.card_vulns, self.card_exploits):
            stats_layout.addWidget(card, 1)
        layout.addLayout(stats_layout)

        # Middle row: Activity (left) + Vuln chart (right)
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(12)

        # Activity panel
        activity_frame = QFrame()
        activity_frame.setObjectName("panel")
        af_layout = QVBoxLayout(activity_frame)
        af_layout.setContentsMargins(0, 0, 0, 0)
        af_layout.setSpacing(0)

        af_header = QLabel("  最近活动")
        af_header.setObjectName("panel_header")
        af_header.setFixedHeight(32)
        af_layout.addWidget(af_header)

        scroll_area = QWidget()
        scroll_area.setObjectName("panel_body")
        self.activity_container = QVBoxLayout(scroll_area)
        self.activity_container.setContentsMargins(0, 4, 0, 4)
        self.activity_container.setSpacing(0)
        self.activity_container.addStretch()
        af_layout.addWidget(scroll_area, 1)

        # Vuln severity chart
        vuln_frame = QFrame()
        vuln_frame.setObjectName("panel")
        vf_layout = QVBoxLayout(vuln_frame)
        vf_layout.setContentsMargins(0, 0, 0, 0)
        vf_layout.setSpacing(0)

        vf_header = QLabel("  漏洞分布")
        vf_header.setObjectName("panel_header")
        vf_header.setFixedHeight(32)
        vf_layout.addWidget(vf_header)

        self.vuln_chart = PlotWidget()
        self.vuln_chart.setMinimumHeight(140)
        self.vuln_chart.setBackground(None)
        self.vuln_chart.hideAxis("left")
        self.vuln_chart.hideAxis("bottom")
        self.vuln_chart.setMouseEnabled(x=False, y=False)
        self.vuln_chart.showGrid(x=False, y=False)
        vf_layout.addWidget(self.vuln_chart, 1)

        mid_layout.addWidget(activity_frame, 3)
        mid_layout.addWidget(vuln_frame, 2)
        layout.addLayout(mid_layout, 1)

        # Bottom row: Port service chart (full width)
        port_frame = QFrame()
        port_frame.setObjectName("panel")
        pf_layout = QVBoxLayout(port_frame)
        pf_layout.setContentsMargins(0, 0, 0, 0)
        pf_layout.setSpacing(0)

        pf_header = QLabel("  端口服务分布")
        pf_header.setObjectName("panel_header")
        pf_header.setFixedHeight(32)
        pf_layout.addWidget(pf_header)

        self.port_chart = PlotWidget()
        self.port_chart.setMinimumHeight(140)
        self.port_chart.setMaximumHeight(200)
        self.port_chart.setBackground(None)
        self.port_chart.setMouseEnabled(x=False, y=False)
        self.port_chart.showGrid(x=False, y=False)
        pf_layout.addWidget(self.port_chart)

        layout.addWidget(port_frame)

        # Bottom row 2: Vuln timeline chart (full width)
        timeline_frame = QFrame()
        timeline_frame.setObjectName("panel")
        tf_layout = QVBoxLayout(timeline_frame)
        tf_layout.setContentsMargins(0, 0, 0, 0)
        tf_layout.setSpacing(0)

        tf_header = QLabel("  漏洞趋势（近 30 天）")
        tf_header.setObjectName("panel_header")
        tf_header.setFixedHeight(32)
        tf_layout.addWidget(tf_header)

        self.timeline_chart = PlotWidget()
        self.timeline_chart.setMinimumHeight(120)
        self.timeline_chart.setMaximumHeight(160)
        self.timeline_chart.setBackground(None)
        self.timeline_chart.setMouseEnabled(x=False, y=False)
        self.timeline_chart.showGrid(x=True, y=True, alpha=0.15)
        tf_layout.addWidget(self.timeline_chart)

        layout.addWidget(timeline_frame)

    def refresh(self):
        try:
            stats = self.engine.db.get_stats()
            self.card_targets.set_value(stats.get("targets", 0))
            self.card_ports.set_value(stats.get("open_ports", 0))
            self.card_vulns.set_value(stats.get("vulnerabilities", 0))
            self.card_exploits.set_value(stats.get("exploits", 0))

            # Activity list — incremental update
            history = self.engine.db.get_scan_history(8)
            if history:
                new_ids = {h.get("id") for h in history}
                if new_ids != self._last_activity_ids:
                    while self.activity_container.count() > 1:
                        child = self.activity_container.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    for h in history:
                        item = ActivityItem(
                            h.get("started_at", ""),
                            h.get("scan_type", ""),
                            h.get("target", ""),
                        )
                        self.activity_container.insertWidget(
                            self.activity_container.count() - 1, item
                        )
                    self._last_activity_ids = new_ids
            else:
                if not self._last_activity_ids:
                    pass  # already showing placeholder
                else:
                    self._last_activity_ids = set()

            # Scan status indicator
            scanning = getattr(self.engine, "_scanning", False)
            if scanning:
                self.scan_indicator.setText("  扫描中...")
                self.scan_indicator.setStyleSheet("color: #2e7d32; font-size: 11px; font-weight: bold;")
            else:
                self.scan_indicator.setText("  空闲")
                self.scan_indicator.setStyleSheet("color: #888; font-size: 11px;")

            # Charts
            self._update_vuln_chart(stats.get("vuln_by_severity", {}))
            self._update_port_chart()
            self._update_timeline_chart()

        except Exception as e:
            try:
                from core.logger import get_logger
                get_logger().error(f"Dashboard 刷新异常: {e}")
            except Exception:
                pass

    def _update_vuln_chart(self, vuln_severity):
        self.vuln_chart.clear()
        if not vuln_severity:
            self._show_empty_chart(self.vuln_chart, "暂无漏洞数据")
            return

        sevs, counts, colors = [], [], []
        for sev in SEVERITY_ORDER:
            cnt = vuln_severity.get(sev, 0)
            if cnt > 0:
                sevs.append(sev)
                counts.append(cnt)
                colors.append(SEVERITY_COLORS.get(sev, "#666"))

        if not counts:
            self._show_empty_chart(self.vuln_chart, "暂无漏洞数据")
            return

        x = np.arange(len(counts))
        brushes = [pg.mkBrush(c) for c in colors]
        bars = BarGraphItem(x=x, height=counts, width=0.55, brushes=brushes)
        self.vuln_chart.addItem(bars)

        for i, (sev, cnt) in enumerate(zip(sevs, counts)):
            txt = pg.TextItem(
                text=str(cnt), color=colors[i],
                anchor=(0.5, 1),
                fill=pg.mkBrush("#ffffff80"),
            )
            txt.setFont(pg.QtGui.QFont("Segoe UI", 10, pg.QtGui.QFont.Weight.Bold))
            txt.setPos(i, cnt)
            self.vuln_chart.addItem(txt)

            lbl = pg.TextItem(text=sev, color="#666", anchor=(0.5, 0))
            lbl.setFont(pg.QtGui.QFont("Segoe UI", 8))
            lbl.setPos(i, 0)
            self.vuln_chart.addItem(lbl)

        self.vuln_chart.setYRange(0, max(counts) * 1.4)
        self.vuln_chart.setXRange(-0.6, len(counts) - 0.4)

    def _update_port_chart(self):
        self.port_chart.clear()
        try:
            svc_stats = self.engine.db.get_port_service_stats()
        except Exception:
            return

        if not svc_stats:
            self._show_empty_chart(self.port_chart, "暂无端口数据")
            return

        services = [s["service"][:10] for s in svc_stats]
        counts = [s["cnt"] for s in svc_stats]

        x = np.arange(len(counts))
        palette = [
            "#0078d4", "#2e7d32", "#f57f17", "#c62828", "#7b1fa2",
            "#00838f", "#4e342e", "#37474f", "#e65100", "#1565c0",
        ]
        brushes = [pg.mkBrush(palette[i % len(palette)]) for i in range(len(counts))]
        bars = BarGraphItem(x=x, height=counts, width=0.55, brushes=brushes)
        self.port_chart.addItem(bars)

        # Value labels
        for i, cnt in enumerate(counts):
            txt = pg.TextItem(
                text=str(cnt), color=palette[i % len(palette)],
                anchor=(0.5, 1),
            )
            txt.setFont(pg.QtGui.QFont("Segoe UI", 9, pg.QtGui.QFont.Weight.Bold))
            txt.setPos(i, cnt)
            self.port_chart.addItem(txt)

        # X-axis labels
        ax = self.port_chart.getAxis("bottom")
        ticks = [(i, services[i]) for i in range(len(services))]
        ax.setTicks([ticks])
        ax.setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 8))
        ax.setHeight(24)

        self.port_chart.setYRange(0, max(counts) * 1.4)
        self.port_chart.setXRange(-0.6, len(counts) - 0.4)

    def _update_timeline_chart(self):
        self.timeline_chart.clear()
        try:
            timeline = self.engine.db.get_vuln_timeline(30)
        except Exception:
            self._show_empty_chart(self.timeline_chart, "暂无趋势数据")
            return

        if not timeline:
            self._show_empty_chart(self.timeline_chart, "暂无趋势数据")
            return

        timeline.reverse()
        counts = [t["cnt"] for t in timeline]
        dates = [t["day"] for t in timeline]

        x = np.arange(len(counts))
        pen = pg.mkPen(color="#c62828", width=2)
        self.timeline_chart.plot(x, counts, pen=pen, symbol="o", symbolSize=5, symbolBrush="#c62828")

        # X-axis date labels
        ax = self.timeline_chart.getAxis("bottom")
        step = max(1, len(dates) // 8)
        ticks = [(i, dates[i][5:]) for i in range(0, len(dates), step)]
        ax.setTicks([ticks])
        ax.setStyle(tickFont=pg.QtGui.QFont("Segoe UI", 7))
        ax.setHeight(20)

        if counts:
            self.timeline_chart.setYRange(0, max(counts) * 1.3 + 1)

    def _show_empty_chart(self, chart, text):
        msg = pg.TextItem(text=text, color="#aaa", anchor=(0.5, 0.5))
        msg.setFont(pg.QtGui.QFont("Segoe UI", 10))
        msg.setPos(0.5, 0.5)
        chart.addItem(msg)
        chart.setXRange(0, 1)
        chart.setYRange(0, 1)
