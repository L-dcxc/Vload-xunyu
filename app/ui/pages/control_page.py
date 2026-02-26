from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets.card_frame import CardFrame


def _section(title: str) -> tuple[CardFrame, QVBoxLayout]:
    card = CardFrame()
    root = QVBoxLayout(card)
    root.setContentsMargins(14, 12, 14, 12)
    root.setSpacing(10)

    t = QLabel(title)
    t.setStyleSheet("color: #9AA7B2; font-size: 12px;")
    root.addWidget(t)

    return card, root


class ControlPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        grid = QGridLayout()
        grid.setSpacing(12)

        conn_card, conn_layout = _section("连接")
        conn_form = QFormLayout()
        conn_form.setLabelAlignment(conn_form.labelAlignment())
        conn_form.setFormAlignment(conn_form.formAlignment())

        self.transport_combo = QComboBox()
        self.transport_combo.addItems(["TCP", "COM"])

        self.addr_input = QLineEdit()
        self.addr_input.setPlaceholderText("192.168.1.50:5025 或 COM3@115200")

        conn_form.addRow("方式", self.transport_combo)
        conn_form.addRow("地址", self.addr_input)

        conn_buttons = QHBoxLayout()
        self.btn_connect = QPushButton("连接")
        self.btn_disconnect = QPushButton("断开")
        self.btn_disconnect.setEnabled(False)
        conn_buttons.addWidget(self.btn_connect)
        conn_buttons.addWidget(self.btn_disconnect)
        conn_buttons.addStretch(1)

        self.idn_label = QLabel("*IDN?: --")
        self.idn_label.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        conn_layout.addLayout(conn_form)
        conn_layout.addLayout(conn_buttons)
        conn_layout.addWidget(self.idn_label)

        mode_card, mode_layout = _section("模式与设定")
        mode_form = QFormLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["CC", "CV", "CP", "CR"])
        self.setpoint_input = QLineEdit()
        self.setpoint_input.setPlaceholderText("设定值")
        self.btn_apply = QPushButton("应用")

        mode_form.addRow("模式", self.mode_combo)
        mode_form.addRow("设定值", self.setpoint_input)
        mode_layout.addLayout(mode_form)
        mode_layout.addWidget(self.btn_apply)

        protect_card, protect_layout = _section("保护")
        protect_form = QFormLayout()
        self.ocp_input = QLineEdit()
        self.ocp_input.setPlaceholderText("CURR:PROT")
        self.opp_input = QLineEdit()
        self.opp_input.setPlaceholderText("POW:PROT")
        protect_form.addRow("过流保护 OCP (A)", self.ocp_input)
        protect_form.addRow("过功率保护 OPP (W)", self.opp_input)
        protect_layout.addLayout(protect_form)

        system_card, system_layout = _section("系统")
        system_buttons = QHBoxLayout()
        self.btn_cls = QPushButton("*CLS")
        self.btn_rst = QPushButton("*RST")
        system_buttons.addWidget(self.btn_cls)
        system_buttons.addWidget(self.btn_rst)
        system_buttons.addStretch(1)
        system_layout.addLayout(system_buttons)

        grid.addWidget(conn_card, 0, 0)
        grid.addWidget(mode_card, 0, 1)
        grid.addWidget(protect_card, 1, 0)
        grid.addWidget(system_card, 1, 1)

        root.addLayout(grid)
        root.addStretch(1)
