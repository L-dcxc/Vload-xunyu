from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from ..widgets.card_frame import CardFrame


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        card = CardFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        title = QLabel("设置")
        title.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        form = QFormLayout()
        self.default_tcp_port = QLineEdit("5025")
        self.default_timeout = QLineEdit("2000")
        form.addRow("默认TCP端口", self.default_tcp_port)
        form.addRow("超时 (ms)", self.default_timeout)

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addStretch(1)

        root.addWidget(card)
        root.addStretch(1)
