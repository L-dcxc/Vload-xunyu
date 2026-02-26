from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class BottomPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("数据与日志")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        self.tabs = QTabWidget()

        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(10)

        export_row = QHBoxLayout()
        self.btn_export = QPushButton("导出 CSV/Excel")
        self.btn_export.setProperty("variant", "secondary")
        export_row.addWidget(self.btn_export)
        export_row.addStretch(1)

        self.data_table = QTableWidget(0, 5)
        self.data_table.setHorizontalHeaderLabels(["时间", "电压(V)", "电流(A)", "功率(W)", "内阻(Ω)"])
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(self.data_table.SelectionBehavior.SelectRows)
        self.data_table.setEditTriggers(self.data_table.EditTrigger.NoEditTriggers)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        data_layout.addLayout(export_row)
        data_layout.addWidget(self.data_table, 1)

        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(10)

        self.run_log = QTextEdit()
        self.run_log.setReadOnly(True)
        self.run_log.setPlaceholderText("运行日志将显示在这里…")

        log_layout.addWidget(self.run_log, 1)

        self.tabs.addTab(data_tab, "数据")
        self.tabs.addTab(log_tab, "运行日志")

        root.addWidget(title)
        root.addWidget(self.tabs, 1)

    def append_log(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.run_log.append(f"[{ts}] {text}")

    def append_data(self, v: float, i: float, p: float, r: float) -> None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        for col, val in enumerate([ts, f"{v:.3f}", f"{i:.3f}", f"{p:.3f}", f"{r:.3f}"]):
            self.data_table.setItem(row, col, QTableWidgetItem(val))

        self.data_table.scrollToBottom()
