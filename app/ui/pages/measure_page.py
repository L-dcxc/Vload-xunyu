from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ..widgets.card_frame import CardFrame


class MeasurePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(12)

        card = CardFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        title = QLabel("测量")
        title.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        hint = QLabel("本页后续将显示 MEAS:VOLT?/CURR?/POWER?/RES? 以及 MAX/MIN/PTP 等数据。")
        hint.setStyleSheet("color: #9AA7B2; font-size: 12px;")
        hint.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch(1)

        grid.addWidget(card, 0, 0)
        root.addLayout(grid)
        root.addStretch(1)
