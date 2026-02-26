from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ..widgets.card_frame import CardFrame


def _kpi_card(title: str, value: str, unit: str) -> CardFrame:
    card = CardFrame()
    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(8)

    title_label = QLabel(title)
    title_label.setStyleSheet("color: #9AA7B2; font-size: 12px;")

    value_label = QLabel(value)
    value_label.setStyleSheet("font-size: 32px; font-weight: 800;")

    unit_label = QLabel(unit)
    unit_label.setStyleSheet("color: #9AA7B2; font-size: 12px;")

    layout.addWidget(title_label)
    layout.addWidget(value_label)
    layout.addWidget(unit_label)
    layout.addStretch(1)

    return card


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(_kpi_card("电压", "--", "V"), 0, 0)
        grid.addWidget(_kpi_card("电流", "--", "A"), 0, 1)
        grid.addWidget(_kpi_card("功率", "--", "W"), 0, 2)
        grid.addWidget(_kpi_card("电阻", "--", "Ω"), 0, 3)

        plot = CardFrame()
        plot_layout = QVBoxLayout(plot)
        plot_layout.setContentsMargins(14, 12, 14, 12)
        plot_layout.setSpacing(8)

        plot_title = QLabel("趋势")
        plot_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        plot_hint = QLabel("曲线占位（后续可接入 pyqtgraph）")
        plot_hint.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        plot_layout.addWidget(plot_title)
        plot_layout.addWidget(plot_hint)
        plot_layout.addStretch(1)

        root.addLayout(grid)
        root.addWidget(plot, 1)
