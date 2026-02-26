from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class SequencePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("任务序列")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        top = QHBoxLayout()
        top.addWidget(title)
        top.addStretch(1)

        self.template = QComboBox()
        self.template.addItems(["空白模板", "电池容量测试", "电源动态响应", "自定义..."])

        top.addWidget(QLabel("模板"))
        top.addWidget(self.template)

        btns = QHBoxLayout()
        self.btn_load = QPushButton("加载")
        self.btn_load.setProperty("variant", "secondary")
        self.btn_save = QPushButton("保存")
        self.btn_save.setProperty("variant", "secondary")
        self.btn_run = QPushButton("开始执行")
        self.btn_stop = QPushButton("停止")
        self.btn_stop.setProperty("variant", "secondary")

        btns.addWidget(self.btn_load)
        btns.addWidget(self.btn_save)
        btns.addStretch(1)
        btns.addWidget(self.btn_run)
        btns.addWidget(self.btn_stop)

        self.table = QTableWidget(6, 5)
        self.table.setHorizontalHeaderLabels(["步骤", "模式", "设定值", "持续(s)", "备注"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.DoubleClicked | self.table.EditTrigger.EditKeyPressed)

        for r in range(self.table.rowCount()):
            self.table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            self.table.setItem(r, 1, QTableWidgetItem("CC"))
            self.table.setItem(r, 2, QTableWidgetItem("1.0"))
            self.table.setItem(r, 3, QTableWidgetItem("5"))
            self.table.setItem(r, 4, QTableWidgetItem(""))

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        root.addLayout(top)
        root.addLayout(btns)
        root.addWidget(self.table, 1)
