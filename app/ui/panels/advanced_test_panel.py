from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .short_test_panel import ShortTestPanel
from .battery_test_panel import BatteryTestPanel


class AdvancedTestPanel(QFrame):
    short_start_requested = pyqtSignal(float, str, str)  # duration_s, curr_prot, pow_prot
    short_stop_requested = pyqtSignal()
    short_estop_requested = pyqtSignal()

    battery_start_requested = pyqtSignal(str, str, str, str, str)  # mode, value, cutoff_v, cutoff_time_s, cutoff_mah
    battery_stop_requested = pyqtSignal()
    battery_estop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("高级测试")
        title.setStyleSheet("font-size: 14px; font-weight: 800;")

        self._mon_v = QLabel("电压  -- V")
        self._mon_i = QLabel("电流  -- A")
        self._mon_p = QLabel("功率  -- W")
        self._mon_r = QLabel("内阻  -- Ω")
        self._mon_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mon_i.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mon_p.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mon_r.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._mon_v.setStyleSheet("font-size: 16px; font-weight: 800; color: #3B82F6;")
        self._mon_i.setStyleSheet("font-size: 16px; font-weight: 800; color: #22C55E;")
        self._mon_p.setStyleSheet("font-size: 16px; font-weight: 800; color: #F59E0B;")
        self._mon_r.setStyleSheet("font-size: 16px; font-weight: 800; color: #A855F7;")

        mon_row = QHBoxLayout()
        mon_row.setSpacing(18)
        mon_row.addStretch(1)
        mon_row.addWidget(self._mon_v)
        mon_row.addWidget(self._mon_i)
        mon_row.addWidget(self._mon_p)
        mon_row.addWidget(self._mon_r)
        mon_row.addStretch(1)

        content = QHBoxLayout()
        content.setSpacing(12)

        self.mode_list = QListWidget()
        self.mode_list.setMinimumWidth(220)

        self.stack = QStackedWidget()

        self.short_panel = ShortTestPanel()
        self.short_panel.start_requested.connect(self.short_start_requested)
        self.short_panel.stop_requested.connect(self.short_stop_requested)
        self.short_panel.estop_requested.connect(self.short_estop_requested)

        self.battery_panel = BatteryTestPanel()
        self.battery_panel.start_requested.connect(self.battery_start_requested)
        self.battery_panel.stop_requested.connect(self.battery_stop_requested)
        self.battery_panel.estop_requested.connect(self.battery_estop_requested)

        self._placeholder_pages: dict[str, QWidget] = {}

        self._add_mode("短路 (SHORT)", self.short_panel)
        self._add_placeholder("列表测试 (LIST)")
        self._add_placeholder("动态测试 (DYNA)")
        self._add_placeholder("自动测试 (AUTO)")
        self._add_placeholder("负载效应 (EFFT)")
        self._add_mode("电池模式 (BATT)", self.battery_panel)
        self._add_placeholder("时序测试 (TIME)")
        self._add_placeholder("LED 测试 (LED)")
        self._add_placeholder("过流测试 (OCP)")

        content.addWidget(self.mode_list, 0)
        content.addWidget(self.stack, 1)

        root.addWidget(title)
        root.addLayout(mon_row)
        root.addLayout(content, 1)

        self.mode_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        if self.mode_list.count() > 0:
            self.mode_list.setCurrentRow(0)

    def _add_mode(self, label: str, widget: QWidget) -> None:
        self.mode_list.addItem(QListWidgetItem(label))
        self.stack.addWidget(widget)

    def _add_placeholder(self, label: str) -> None:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        tip = QLabel("开发中…")
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tip.setStyleSheet("color: #9AA7B2; font-size: 14px;")
        layout.addStretch(1)
        layout.addWidget(tip)
        layout.addStretch(1)
        self._add_mode(label, w)
        self._placeholder_pages[label] = w

    def set_locked(self, locked: bool) -> None:
        self.mode_list.setDisabled(locked)

    def set_monitor_values(self, v: float | None, i: float | None, p: float | None, r: float | None) -> None:
        self._mon_v.setText(f"电压  {v:.3f} V" if v is not None else "电压  -- V")
        self._mon_i.setText(f"电流  {i:.3f} A" if i is not None else "电流  -- A")
        self._mon_p.setText(f"功率  {p:.3f} W" if p is not None else "功率  -- W")
        self._mon_r.setText(f"内阻  {r:.3f} Ω" if r is not None else "内阻  -- Ω")
