import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTextBrowser, QFileDialog, QGroupBox
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

    def _generate(self):
        db = self.engine.db
        if not db:
            self.status_label.setText("数据库未初始化")
            return

        self.btn_generate.setEnabled(False)
        self.status_label.setText("正在生成...")

        try:
            gen = ReportGenerator(db)
            self._report_md = gen.generate_markdown()
            html = gen.generate_html()
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

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 PDF", "darkveil_report.pdf", "PDF (*.pdf)"
        )
        if path:
            self.status_label.setText("正在生成 PDF...")
            try:
                from modules.report.pdf_generator import generate_pdf
                generate_pdf(self.engine.db, path)
                self.status_label.setText(f"已导出: {path}")
            except Exception as e:
                self.status_label.setText(f"PDF 导出失败: {e}")
