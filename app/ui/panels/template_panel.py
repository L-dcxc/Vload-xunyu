from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class TemplatePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title_row = QHBoxLayout()
        title = QLabel("模板库")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        self.btn_apply = QPushButton("应用到序列")
        self.btn_apply.setProperty("variant", "secondary")

        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(self.btn_apply)

        content = QHBoxLayout()
        content.setSpacing(12)

        self.list = QListWidget()
        self.list.setMinimumWidth(260)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("选择左侧模板查看说明…")

        content.addWidget(self.list, 0)
        content.addWidget(self.preview, 1)

        root.addLayout(title_row)
        root.addLayout(content, 1)

        self._seed_templates()
        self.list.currentItemChanged.connect(self._on_selected)

    def _seed_templates(self) -> None:
        items = [
            ("空白模板", "生成一个空的序列，便于你手工编辑每一步。"),
            (
                "电池容量测试",
                "典型流程：恒流放电 → 记录时间/容量 → 低压截止。\n\n需要你补充：截止电压、放电电流、采样间隔等。",
            ),
            (
                "电源动态响应",
                "典型流程：在两档电流之间切换（DYN 或 LIST），观察电压跌落与恢复。\n\n需要你补充：高/低电流、驻留时间、斜率等。",
            ),
            (
                "稳压源测试",
                "典型流程：恒流扫描并记录输出电压，得到负载调整率。\n\n需要你补充：扫描步进、驻留时间、保护阈值等。",
            ),
        ]

        self._template_text: dict[str, str] = {}
        for name, text in items:
            self._template_text[name] = text
            self.list.addItem(QListWidgetItem(name))

        if self.list.count() > 0:
            self.list.setCurrentRow(0)

    def _on_selected(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        if not current:
            self.preview.clear()
            return

        name = current.text()
        self.preview.setPlainText(self._template_text.get(name, ""))

    def current_template(self) -> str:
        item = self.list.currentItem()
        return item.text() if item else ""
