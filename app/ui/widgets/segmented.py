from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QToolButton, QWidget


class SegmentedControl(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: list[QToolButton] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, label in enumerate(items):
            btn = QToolButton()
            btn.setText(label)
            btn.setCheckable(True)
            btn.setProperty("seg", "true")
            btn.setProperty("segPos", "left" if i == 0 else ("right" if i == len(items) - 1 else "mid"))
            self._group.addButton(btn)
            self._buttons.append(btn)
            layout.addWidget(btn)

        self._group.buttonClicked.connect(self._on_clicked)

        if self._buttons:
            self._buttons[0].setChecked(True)

    def value(self) -> str:
        for b in self._buttons:
            if b.isChecked():
                return b.text()
        return ""

    def set_value(self, value: str) -> None:
        for b in self._buttons:
            if b.text() == value:
                b.setChecked(True)
                self.changed.emit(value)
                return

    def _on_clicked(self, button):  # type: ignore[no-untyped-def]
        self.changed.emit(button.text())
