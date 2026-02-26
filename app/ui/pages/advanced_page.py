from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..widgets.card_frame import CardFrame


class AdvancedPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        card = CardFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        title = QLabel("高级")
        title.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        hint = QLabel("后续模块：DYN / LIST / OCP / Timing / LoadEffect")
        hint.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch(1)

        root.addWidget(card)
        root.addStretch(1)
