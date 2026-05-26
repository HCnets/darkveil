from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtGui import QColor


class ResultTable(QTableWidget):
    def __init__(self, headers=None, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        if headers:
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)

    def add_row(self, data, row_color=None):
        row = self.rowCount()
        self.insertRow(row)
        col_count = self.columnCount()
        for col, value in enumerate(data):
            if col >= col_count:
                break
            item = QTableWidgetItem(str(value) if value is not None else "")
            if row_color:
                item.setForeground(QColor(row_color))
            self.setItem(row, col, item)
        return row

    def clear_data(self):
        self.setRowCount(0)

    def set_column_widths(self, widths):
        for i, w in enumerate(widths):
            if i < self.columnCount():
                self.setColumnWidth(i, w)

    def get_row_data(self, row):
        data = {}
        for col in range(self.columnCount()):
            header = self.horizontalHeaderItem(col)
            key = header.text() if header else f"col_{col}"
            item = self.item(row, col)
            data[key] = item.text() if item else ""
        return data
