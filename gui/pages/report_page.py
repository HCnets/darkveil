import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTextBrowser, QFileDialog, QGroupBox, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt
from modules.report.generator import ReportGenerator


class ReportPage(QWidget):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._report_md = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("安全报告")
        title.setObjectName("title")
        layout.addWidget(title)

        # Section selection
        section_frame = QFrame()
        section_frame.setObjectName("panel")
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(6)

        section_label = QLabel("报告章节:")
        section_layout.addWidget(section_label)

        cb_row1 = QHBoxLayout()
        cb_row1.setSpacing(12)
        self.section_summary = QCheckBox("执行摘要")
        self.section_summary.setChecked(True)
        cb_row1.addWidget(self.section_summary)

        self.section_targets = QCheckBox("目标详情")
        self.section_targets.setChecked(True)
        cb_row1.addWidget(self.section_targets)

        self.section_vulns = QCheckBox("漏洞汇总")
        self.section_vulns.setChecked(True)
        cb_row1.addWidget(self.section_vulns)

        self.section_high_risk = QCheckBox("高危详情")
        self.section_high_risk.setChecked(True)
        cb_row1.addWidget(self.section_high_risk)

        self.section_history = QCheckBox("扫描历史")
        self.section_history.setChecked(True)
        cb_row1.addWidget(self.section_history)
        cb_row1.addStretch()
        section_layout.addLayout(cb_row1)

        cb_row2 = QHBoxLayout()
        cb_row2.setSpacing(12)
        self.section_owasp = QCheckBox("OWASP Top 10")
        cb_row2.addWidget(self.section_owasp)

        self.section_cis = QCheckBox("CIS Benchmark")
        cb_row2.addWidget(self.section_cis)

        self.section_risk_matrix = QCheckBox("风险矩阵")
        cb_row2.addWidget(self.section_risk_matrix)
        cb_row2.addStretch()
        section_layout.addLayout(cb_row2)

        layout.addWidget(section_frame)

        # Company info
        company_frame = QFrame()
        company_frame.setObjectName("panel")
        company_layout = QHBoxLayout(company_frame)
        company_layout.setSpacing(8)

        company_layout.addWidget(QLabel("公司名称:"))
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("可选，用于报告封面")
        self.company_input.setFixedWidth(200)
        company_layout.addWidget(self.company_input)

        company_layout.addWidget(QLabel("Logo:"))
        self.logo_input = QLineEdit()
        self.logo_input.setPlaceholderText("Logo 图片路径")
        company_layout.addWidget(self.logo_input)

        self.btn_browse_logo = QPushButton("浏览")
        self.btn_browse_logo.setFixedWidth(60)
        self.btn_browse_logo.clicked.connect(self._browse_logo)
        company_layout.addWidget(self.btn_browse_logo)

        company_layout.addStretch()
        layout.addWidget(company_frame)

        # 操作栏
        btn_frame = QFrame()
        btn_frame.setObjectName("panel")
        btn_layout = QHBoxLayout(btn_frame)

        self.btn_generate = QPushButton("生成报告")
        self.btn_generate.setObjectName("primary")
        self.btn_generate.clicked.connect(self._generate)
        btn_layout.addWidget(self.btn_generate)

        self.btn_export_md = QPushButton("导出 Markdown")
        self.btn_export_md.setEnabled(False)
        self.btn_export_md.clicked.connect(self._export_markdown)
        btn_layout.addWidget(self.btn_export_md)

        self.btn_export_html = QPushButton("导出 HTML")
        self.btn_export_html.setEnabled(False)
        self.btn_export_html.clicked.connect(self._export_html)
        btn_layout.addWidget(self.btn_export_html)

        self.btn_export_pdf = QPushButton("导出 PDF")
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        btn_layout.addWidget(self.btn_export_pdf)

        btn_layout.addStretch()
        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        btn_layout.addWidget(self.status_label)

        layout.addWidget(btn_frame)

        # 报告预览
        preview_group = QGroupBox("报告预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        preview_layout.addWidget(self.preview)

        layout.addWidget(preview_group)

    def _get_sections(self):
        return {
            "summary": self.section_summary.isChecked(),
            "targets": self.section_targets.isChecked(),
            "vulns": self.section_vulns.isChecked(),
            "high_risk": self.section_high_risk.isChecked(),
            "history": self.section_history.isChecked(),
            "owasp": self.section_owasp.isChecked(),
            "cis": self.section_cis.isChecked(),
            "risk_matrix": self.section_risk_matrix.isChecked(),
        }

    def _generate(self):
        db = self.engine.db
        if not db:
            self.status_label.setText("数据库未初始化")
            return

        self.btn_generate.setEnabled(False)
        self.status_label.setText("正在生成...")

        try:
            gen = ReportGenerator(db)
            sections = self._get_sections()
            company_name = self.company_input.text().strip()
            self._report_md = gen.generate_markdown(sections=sections, company_name=company_name)
            html = gen.generate_html(sections=sections, company_name=company_name)
            self.preview.setHtml(html)

            self.btn_export_md.setEnabled(True)
            self.btn_export_html.setEnabled(True)
            self.btn_export_pdf.setEnabled(True)
            self.status_label.setText(f"报告已生成 ({len(self._report_md)} 字符)")
        except Exception as e:
            self.status_label.setText(f"生成失败: {e}")
        finally:
            self.btn_generate.setEnabled(True)

    def _export_markdown(self):
        if not self._report_md:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 Markdown", "darkveil_report.md", "Markdown (*.md)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._report_md)
                self.status_label.setText(f"已导出: {path}")
            except Exception as e:
                self.status_label.setText(f"导出失败: {e}")

    def _export_html(self):
        if not self._report_md:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 HTML", "darkveil_report.html", "HTML (*.html)"
        )
        if path:
            try:
                gen = ReportGenerator(self.engine.db)
                html = gen.generate_html()
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                self.status_label.setText(f"已导出: {path}")
            except Exception as e:
                self.status_label.setText(f"导出失败: {e}")

    def _browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Logo", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.logo_input.setText(path)

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 PDF", "darkveil_report.pdf", "PDF (*.pdf)"
        )
        if path:
            self.status_label.setText("正在生成 PDF...")
            try:
                from modules.report.pdf_generator import generate_pdf
                sections = self._get_sections()
                company_name = self.company_input.text().strip()
                logo_path = self.logo_input.text().strip()
                generate_pdf(self.engine.db, path,
                             company_name=company_name, logo_path=logo_path,
                             sections=sections)
                self.status_label.setText(f"已导出: {path}")
            except Exception as e:
                self.status_label.setText(f"PDF 导出失败: {e}")
