from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget

from .card_frame import CardFrame


@dataclass
class DeviceViewModel:
    alias: str
    transport: str
    address: str
    status: str


class DeviceCard(CardFrame):
    clicked = pyqtSignal()

    def __init__(self, device: DeviceViewModel, parent=None):
        super().__init__(parent)
        self._device = device

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        self.alias_label = QLabel(device.alias)
        self.alias_label.setStyleSheet("font-size: 14px; font-weight: 700;")

        self.status_label = QLabel(device.status)
        self.status_label.setStyleSheet("font-size: 12px;")

        title_row.addWidget(self.alias_label)
        title_row.addStretch(1)
        title_row.addWidget(self.status_label)

        self.addr_label = QLabel(f"{device.transport}  {device.address}")
        self.addr_label.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        preview = QWidget()
        preview_row = QHBoxLayout(preview)
        preview_row.setContentsMargins(0, 0, 0, 0)
        preview_row.setSpacing(10)

        self.preview_v = QLabel("电压 --")
        self.preview_i = QLabel("电流 --")
        self.preview_p = QLabel("功率 --")
        for w in (self.preview_v, self.preview_i, self.preview_p):
            w.setStyleSheet("font-size: 12px; color: #E6EDF3;")

        preview_row.addWidget(self.preview_v)
        preview_row.addWidget(self.preview_i)
        preview_row.addWidget(self.preview_p)
        preview_row.addStretch(1)

        root.addLayout(title_row)
        root.addWidget(self.addr_label)
        root.addWidget(preview)

        self.setMinimumWidth(240)

    @property
    def device(self) -> DeviceViewModel:
        return self._device

    def mousePressEvent(self, event):  # type: ignore[override]
        self.clicked.emit()
        return super().mousePressEvent(event)
