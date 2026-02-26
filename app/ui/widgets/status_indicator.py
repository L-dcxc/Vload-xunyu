from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class StatusIndicator(QWidget):
    def __init__(self, diameter: int = 10, parent=None):
        super().__init__(parent)
        self._diameter = diameter
        self._color = QColor("#EF4444")
        self.setFixedSize(diameter, diameter)

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(self._color.darker(140))
        painter.setBrush(self._color)
        painter.drawEllipse(0, 0, self._diameter - 1, self._diameter - 1)
