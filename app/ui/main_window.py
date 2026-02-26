from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDockWidget,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .pages.advanced_page import AdvancedPage
from .pages.control_page import ControlPage
from .pages.dashboard_page import DashboardPage
from .pages.measure_page import MeasurePage
from .pages.settings_page import SettingsPage
from .widgets.device_card import DeviceCard, DeviceViewModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("电子负载上位机")
        self.setMinimumSize(1200, 780)

        self._device_cards: list[DeviceCard] = []
        self._current_device: DeviceViewModel | None = None

        self._build_toolbar()
        self._build_central()
        self._build_dock()
        self._build_statusbar()

        self._seed_devices()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self.btn_add_device = QToolButton()
        self.btn_add_device.setText("+ 添加")
        self.btn_add_device.clicked.connect(self._add_device_placeholder)

        toolbar.addWidget(self.btn_add_device)
        toolbar.addSeparator()

        self.toolbar_hint = QLabel("界面骨架（暂未接入SCPI通信）")
        self.toolbar_hint.setStyleSheet("color: #9AA7B2; padding-left: 8px;")
        toolbar.addWidget(self.toolbar_hint)

    def _build_central(self) -> None:
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(290)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(10)

        sidebar_title = QLabel("设备")
        sidebar_title.setStyleSheet("color: #9AA7B2; font-size: 12px;")

        self.device_scroll = QScrollArea()
        self.device_scroll.setWidgetResizable(True)
        self.device_scroll.setFrameShape(self.device_scroll.Shape.NoFrame)

        self.device_container = QWidget()
        self.device_grid = QGridLayout(self.device_container)
        self.device_grid.setContentsMargins(0, 0, 0, 0)
        self.device_grid.setSpacing(10)

        self.device_scroll.setWidget(self.device_container)

        sidebar_layout.addWidget(sidebar_title)
        sidebar_layout.addWidget(self.device_scroll, 1)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        self.device_header = QLabel("当前设备：--")
        self.device_header.setStyleSheet("font-size: 14px; font-weight: 700;")

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.page_dashboard = DashboardPage()
        self.page_control = ControlPage()
        self.page_measure = MeasurePage()
        self.page_advanced = AdvancedPage()
        self.page_settings = SettingsPage()

        self.tabs.addTab(self.page_dashboard, "总览")
        self.tabs.addTab(self.page_control, "控制")
        self.tabs.addTab(self.page_measure, "测量")
        self.tabs.addTab(self.page_advanced, "高级")
        self.tabs.addTab(self.page_settings, "设置")

        main_layout.addWidget(self.device_header)
        main_layout.addWidget(self.tabs, 1)

        root.addWidget(self.sidebar)
        root.addWidget(main, 1)

        self.setCentralWidget(central)

    def _build_dock(self) -> None:
        self.dock = QDockWidget("日志 / SCPI 终端", self)
        self.dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock)

        dock_root = QWidget()
        dock_layout = QVBoxLayout(dock_root)
        dock_layout.setContentsMargins(12, 12, 12, 12)
        dock_layout.setSpacing(10)

        self.dock_tabs = QTabWidget()

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("通信日志将显示在这里…")

        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(10)

        btn_clear_log = QPushButton("清空日志")
        btn_clear_log.clicked.connect(self.log_view.clear)

        log_layout.addWidget(btn_clear_log, 0, Qt.AlignmentFlag.AlignLeft)
        log_layout.addWidget(self.log_view, 1)

        term_tab = QWidget()
        term_layout = QVBoxLayout(term_tab)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(10)

        self.term_output = QTextEdit()
        self.term_output.setReadOnly(True)
        self.term_output.setPlaceholderText("SCPI 终端输出…")

        input_row = QHBoxLayout()
        self.term_input = QLineEdit()
        self.term_input.setPlaceholderText("输入 SCPI 命令，例如 *IDN?")
        self.btn_term_send = QPushButton("发送")
        self.btn_term_send.clicked.connect(self._on_terminal_send)
        self.term_input.returnPressed.connect(self._on_terminal_send)

        input_row.addWidget(self.term_input, 1)
        input_row.addWidget(self.btn_term_send)

        term_layout.addWidget(self.term_output, 1)
        term_layout.addLayout(input_row)

        self.dock_tabs.addTab(log_tab, "日志")
        self.dock_tabs.addTab(term_tab, "SCPI 终端")

        dock_layout.addWidget(self.dock_tabs)
        self.dock.setWidget(dock_root)

        self.resizeDocks([self.dock], [220], Qt.Orientation.Vertical)

    def _build_statusbar(self) -> None:
        sb = QStatusBar()
        self.setStatusBar(sb)

        self.status_left = QLabel("未连接")
        self.status_left.setStyleSheet("color: #9AA7B2;")
        sb.addWidget(self.status_left)

    def _seed_devices(self) -> None:
        devices = [
            DeviceViewModel(alias="设备 A", transport="TCP", address="192.168.1.50:5025", status="未连接"),
            DeviceViewModel(alias="设备 B", transport="COM", address="COM3@115200", status="未连接"),
        ]
        for d in devices:
            self._add_device_card(d)

        if self._device_cards:
            self._select_device(self._device_cards[0])

    def _add_device_placeholder(self) -> None:
        idx = len(self._device_cards) + 1
        d = DeviceViewModel(alias=f"设备 {idx}", transport="TCP", address="0.0.0.0:5025", status="未连接")
        self._add_device_card(d)

    def _add_device_card(self, device: DeviceViewModel) -> None:
        card = DeviceCard(device)
        card.clicked.connect(lambda c=card: self._select_device(c))

        self._device_cards.append(card)

        row = (len(self._device_cards) - 1)
        self.device_grid.addWidget(card, row, 0)

    def _select_device(self, card: DeviceCard) -> None:
        for c in self._device_cards:
            c.set_selected(c is card)

        self._current_device = card.device
        self.device_header.setText(
            f"当前设备：{card.device.alias}   （{card.device.transport} {card.device.address}）   {card.device.status}"
        )
        self.status_left.setText(f"已选择：{card.device.alias}")

    def _on_terminal_send(self) -> None:
        cmd = self.term_input.text().strip()
        if not cmd:
            return

        device = self._current_device
        prefix = f"[{device.alias}]" if device else "[--]"

        self.term_output.append(f"{prefix} 发送：{cmd}")
        self.log_view.append(f"{prefix} 发送：{cmd}")
        self.term_input.clear()
